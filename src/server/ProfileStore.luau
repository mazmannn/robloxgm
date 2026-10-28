-- Pure server domain; no Roblox services so the same rules can run in Lune tests.
local ProfileStore = {}
ProfileStore.__index = ProfileStore

local function copy(value)
    if type(value) ~= "table" then return value end
    local result = {}
    for key, item in value do result[key] = copy(item) end
    return result
end

local function validId(id)
    return type(id) == "string" and #id > 0 and #id <= 128
end

function ProfileStore.new(config, generateId)
    assert(type(generateId) == "function", "ID generator required")
    assert(config.TeamLimit >= 1 and config.CollectionLimit >= config.TeamLimit, "Invalid limits")
    assert(config.Species[config.StarterSpeciesId], "Unknown starter")
    return setmetatable({
        config = copy(config), generateId = generateId,
        entries = {}, owners = {},
    }, ProfileStore)
end

-- Server-only issuance; never register this method as a client action.
function ProfileStore:grantPet(userId, speciesId)
    local entry = self.entries[userId]
    if not entry then return false, "ProfileNotReady" end
    if not self.config.Species[speciesId] then return false, "UnknownSpecies" end
    local count = 0
    for _ in entry.profile.Pets do count += 1 end
    if count >= self.config.CollectionLimit then return false, "CollectionFull" end
    local id = self.generateId()
    if not validId(id) then return false, "InvalidPetId" end
    if self.owners[id] ~= nil then return false, "DuplicatePetId" end
    entry.profile.Pets[id] = {Id = id, SpeciesId = speciesId, Form = 1, Level = 1}
    self.owners[id] = userId
    return true, id
end

function ProfileStore:open(userId)
    if self.entries[userId] then return false, "AlreadyOpen" end
    self.entries[userId] = {
        profile = {
            SchemaVersion = self.config.SchemaVersion,
            Resources = {Crystals = 0, UpgradeMaterial = 0, RareMaterial = 0},
            Pets = {}, EquippedPetIds = {},
        },
        session = {Task = "Idle"}, busy = false, lastRequest = nil,
    }
    local called, ok, id = pcall(self.grantPet, self, userId, self.config.StarterSpeciesId)
    if not called or not ok then
        self.entries[userId] = nil
        return false, if called then id else "IdGenerationFailed"
    end
    table.insert(self.entries[userId].profile.EquippedPetIds, id)
    return true
end

function ProfileStore:close(userId)
    local entry = self.entries[userId]
    if entry then
        for id in entry.profile.Pets do self.owners[id] = nil end
    end
    self.entries[userId] = nil
end

function ProfileStore:snapshot(userId)
    local entry = self.entries[userId]
    if not entry then return nil end
    return {
        storageMode = "MemoryOnly",
        profile = copy(entry.profile), session = copy(entry.session),
    }
end

local function validate(request)
    if type(request) ~= "table" then return false end
    local action = request.action
    if action ~= "GetState" and action ~= "EquipPet"
        and action ~= "UnequipPet" and action ~= "RecallTeam" then return false end
    local needsPet = action == "EquipPet" or action == "UnequipPet"
    -- Bound the work even for huge tables and reject spoofed owner/reward fields.
    local fields = 0
    for key in request do
        fields += 1
        if fields > 2 then return false end
        if key ~= "action" and not (needsPet and key == "petId") then return false end
    end
    return not needsPet or validId(request.petId)
end

-- This entire operation MUST stay non-yielding. Add async persistence outside it.
function ProfileStore:handle(userId, request, now)
    local entry = self.entries[userId]
    if not entry then return {ok = false, code = "ProfileNotReady"} end
    if entry.busy then return {ok = false, code = "Busy"} end
    if type(now) ~= "number" or now ~= now or math.abs(now) == math.huge then
        return {ok = false, code = "InvalidClock"}
    end
    if entry.lastRequest and now - entry.lastRequest < self.config.RequestInterval then
        return {ok = false, code = "RateLimited"}
    end
    entry.lastRequest = now
    if not validate(request) then return {ok = false, code = "InvalidRequest"} end

    entry.busy = true
    local succeeded, response = pcall(function()
        local action = request.action
        if action == "EquipPet" or action == "UnequipPet" then
            if not entry.profile.Pets[request.petId] then
                return {ok = false, code = "PetNotOwned"}
            end
            local team = entry.profile.EquippedPetIds
            local index = table.find(team, request.petId)
            if action == "EquipPet" and not index then
                if #team >= self.config.TeamLimit then return {ok = false, code = "TeamFull"} end
                table.insert(team, request.petId)
            elseif action == "UnequipPet" and index then
                table.remove(team, index)
            end
        elseif action == "RecallTeam" then
            entry.session.Task = "Idle"
        end
        return {ok = true, code = "OK", state = self:snapshot(userId)}
    end)
    entry.busy = false
    if not succeeded then
        warn("ProfileStore operation failed: " .. tostring(response))
        return {ok = false, code = "InternalError"}
    end
    return response
end

return ProfileStore
