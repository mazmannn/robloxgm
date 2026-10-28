local fs = require("@lune/fs")
assert(fs.isFile("src/server/ProfileStore.luau"), "Stage 3 missing: server ProfileStore is not implemented")
local Store = require("../src/server/ProfileStore")
local passed = 0
local function test(name, body)
    local ok, message = pcall(body)
    assert(ok, name .. ": " .. tostring(message))
    passed += 1
    print("PASS " .. name)
end
local function newStore(overrides)
    local config = {
        SchemaVersion = 1, TeamLimit = 3, CollectionLimit = 10,
        RequestInterval = 0.15, StarterSpeciesId = "prototype",
        Species = { prototype = true },
    }
    for key, value in overrides or {} do config[key] = value end
    local serial = 0
    return Store.new(config, function()
        serial += 1
        return "pet-" .. serial
    end)
end
local function owned(store, userId)
    return store:snapshot(userId).profile.EquippedPetIds[1]
end

test("new profiles have isolated resources and globally distinct pet IDs", function()
    local store = newStore()
    assert(store:open(101))
    assert(store:open(202))
    local a, b = store:snapshot(101), store:snapshot(202)
    assert(a.profile.SchemaVersion == 1 and a.storageMode == "MemoryOnly")
    assert(a.profile.Resources.Crystals == 0)
    assert(owned(store, 101) ~= owned(store, 202))
    a.profile.Resources.Crystals = 999
    a.profile.Pets[owned(store, 101)].Level = 999
    table.clear(a.profile.EquippedPetIds)
    assert(store:snapshot(101).profile.Resources.Crystals == 0)
    assert(store:snapshot(101).profile.Pets[owned(store, 101)].Level == 1)
    assert(#store:snapshot(202).profile.EquippedPetIds == 1)
end)

test("opening twice does not reset progress or create another starter", function()
    local store = newStore()
    store:open(101)
    local id = owned(store, 101)
    assert(store:open(101) == false)
    assert(owned(store, 101) == id)
end)

test("players cannot equip another player's pet", function()
    local store = newStore()
    store:open(101); store:open(202)
    local result = store:handle(101, { action = "EquipPet", petId = owned(store, 202) }, 0)
    assert(not result.ok and result.code == "PetNotOwned")
    assert(#store:snapshot(101).profile.EquippedPetIds == 1)
end)

test("repeated equip is idempotent and unequip leaves pet in collection", function()
    local store = newStore()
    store:open(101)
    local id = owned(store, 101)
    assert(store:handle(101, {action = "EquipPet", petId = id}, 0).ok)
    assert(store:handle(101, {action = "EquipPet", petId = id}, 1).ok)
    assert(#store:snapshot(101).profile.EquippedPetIds == 1)
    assert(store:handle(101, {action = "UnequipPet", petId = id}, 2).ok)
    assert(#store:snapshot(101).profile.EquippedPetIds == 0)
    assert(store:snapshot(101).profile.Pets[id] ~= nil)
    assert(store:handle(101, {action = "UnequipPet", petId = id}, 3).ok)
end)

test("team cannot exceed configured limit", function()
    local store = newStore()
    store:open(101)
    for i = 1, 2 do
        local ok, id = store:grantPet(101, "prototype")
        assert(ok)
        assert(store:handle(101, { action = "EquipPet", petId = id }, i).ok)
    end
    local _, extra = store:grantPet(101, "prototype")
    local result = store:handle(101, {action = "EquipPet", petId = extra}, 3)
    assert(not result.ok and result.code == "TeamFull")
    assert(#store:snapshot(101).profile.EquippedPetIds == 3)
    assert(store:snapshot(101).profile.Pets[extra] ~= nil)
end)

test("collection limit and unknown species never mutate profile", function()
    local store = newStore({CollectionLimit = 1, TeamLimit = 1})
    store:open(101)
    local ok, code = store:grantPet(101, "prototype")
    assert(not ok and code == "CollectionFull")
    local ok2, code2 = store:grantPet(101, "unknown")
    assert(not ok2 and code2 == "UnknownSpecies")
    assert(#store:snapshot(101).profile.EquippedPetIds == 1)
end)

test("malformed and forged payloads cannot change resources or ownership", function()
    local store = newStore()
    store:open(101)
    local bad = {
        false, "EquipPet", {}, {action = 1}, {action = "GrantPet"},
        {action = "GetState", userId = 202}, {action = "GetState", crystals = 500},
        {action = "EquipPet"}, {action = "EquipPet", petId = {}},
        {action = "EquipPet", petId = ""}, {action = "EquipPet", petId = string.rep("x", 129)},
        {action = "RecallTeam", petId = "pet-1"},
    }
    assert(not store:handle(101, nil, 0).ok)
    for i, payload in bad do
        local result = store:handle(101, payload, i)
        assert(not result.ok, "accepted malformed payload " .. i)
    end
    assert(store:snapshot(101).profile.Resources.Crystals == 0)
    assert(store:handle(101, {action = "GetState"}, 100).ok)
end)

test("rate limiting is per player and recovers after the interval", function()
    local store = newStore()
    store:open(101); store:open(202)
    assert(store:handle(101, {action = "GetState"}, 0).ok)
    assert(store:handle(101, {action = "GetState"}, 0.01).code == "RateLimited")
    assert(store:handle(202, {action = "GetState"}, 0.01).ok)
    assert(store:handle(101, {action = "GetState"}, 0.2).ok)
end)

test("recall is safe with an empty team and keeps collection", function()
    local store = newStore()
    store:open(101)
    local id = owned(store, 101)
    store:handle(101, {action = "UnequipPet", petId = id}, 0)
    local result = store:handle(101, {action = "RecallTeam"}, 1)
    assert(result.ok and result.state.session.Task == "Idle")
    assert(result.state.profile.Pets[id] ~= nil)
end)

test("closing removes session and rejoining starts fresh memory-only profile", function()
    local store = newStore()
    store:open(101)
    local previous = owned(store, 101)
    store:close(101)
    assert(store:snapshot(101) == nil)
    assert(store:handle(101, {action = "GetState"}, 0).code == "ProfileNotReady")
    store:open(101)
    assert(owned(store, 101) ~= previous)
end)

test("duplicate generated ID cannot overwrite an existing pet", function()
    local store = Store.new({SchemaVersion = 1, TeamLimit = 3, CollectionLimit = 10,
        RequestInterval = 0.15, StarterSpeciesId = "prototype", Species = {prototype = true}},
        function() return "same-id" end)
    store:open(101)
    local ok, code = store:grantPet(101, "prototype")
    assert(not ok and code == "DuplicatePetId")
    local ok2 = store:open(202)
    assert(not ok2 and store:snapshot(202) == nil)
    assert(store:snapshot(101).profile.Pets["same-id"].Level == 1)
end)

test("foreign unequip cannot remove either player's team", function()
    local store = newStore()
    store:open(101); store:open(202)
    local foreign = owned(store, 202)
    local result = store:handle(101, {action = "UnequipPet", petId = foreign}, 0)
    assert(not result.ok and result.code == "PetNotOwned")
    assert(#store:snapshot(101).profile.EquippedPetIds == 1)
    assert(owned(store, 202) == foreign)
end)

test("mutating a request response cannot change server state", function()
    local store = newStore()
    store:open(101)
    local result = store:handle(101, {action = "GetState"}, 0)
    result.state.profile.Resources.Crystals = 500
    table.clear(result.state.profile.Pets)
    result.state.session.Task = "FakeTask"
    local nextResult = store:handle(101, {action = "GetState"}, 1)
    assert(nextResult.state.profile.Resources.Crystals == 0)
    assert(nextResult.state.profile.Pets[owned(store, 101)] ~= nil)
    assert(nextResult.state.session.Task == "Idle")
end)

test("invalid ID generation leaves no partially opened profile", function()
    local config = {SchemaVersion = 1, TeamLimit = 1, CollectionLimit = 1,
        RequestInterval = 0.15, StarterSpeciesId = "prototype", Species = {prototype = true}}
    for _, generator in {
        function() return "" end,
        function() return 42 end,
        function() error("ID service unavailable") end,
    } do
        local store = Store.new(config, generator)
        assert(not store:open(101))
        assert(store:snapshot(101) == nil)
        assert(store:handle(101, {action = "GetState"}, 0).code == "ProfileNotReady")
    end
end)

test("invalid clocks are rejected without poisoning subsequent requests", function()
    local store = newStore()
    store:open(101)
    for _, value in {0/0, math.huge, -math.huge, "now"} do
        assert(store:handle(101, {action = "GetState"}, value).code == "InvalidClock")
    end
    assert(store:handle(101, {action = "GetState"}, 0).ok)
end)

print("All " .. passed .. " profile-store tests passed")
