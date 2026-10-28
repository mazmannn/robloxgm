local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")
local Config = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config"))
local ProfileStore = require(script.Parent:WaitForChild("ProfileStore"))
local store = ProfileStore.new(Config, function() return HttpService:GenerateGUID(false) end)
local MiningConfig = require(ReplicatedStorage.Shared:WaitForChild("MiningConfig"))
local MiningService = require(script.Parent:WaitForChild("MiningService"))
local mining = MiningService.new(MiningConfig, function(uid, amount) return store:awardCrystals(uid, amount) end)
local function decorate(uid, result)
    if result.state then
        result.state.mining = mining:snapshot(uid)
        result.state.session.Task = if result.state.mining and result.state.mining.targetId then "Mining" else "Idle"
    end
    return result
end
local function distance(player, id)
    local node=MiningConfig.Nodes[id]
    local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
    local humanoid=player.Character and player.Character:FindFirstChildOfClass("Humanoid")
    if not node or not root or not humanoid or humanoid.Health<=0 then return nil end
    return (root.Position-Vector3.new(node.x,node.y,node.z)).Magnitude
end

-- Runtime objects are created by the server, outside the Shared source folder.
local network = Instance.new("Folder")
network.Name = "GameNetwork"
for id,node in MiningConfig.Nodes do
    local hit=workspace:Raycast(Vector3.new(node.x,100,node.z),Vector3.new(0,-200,0))
    if hit then node.y=hit.Position.Y end
    network:SetAttribute(id.."_Y",node.y)
end
local request = Instance.new("RemoteEvent")
request.Name = "Request"
request.Parent = network
local response = Instance.new("RemoteEvent")
response.Name = "Response"
response.Parent = network

request.OnServerEvent:Connect(function(player, payload)
    -- Player comes from Roblox, never from a client-controlled userId.
    local now=os.clock()
    local selectRequest=type(payload)=="table" and payload.action=="SelectTarget"
    -- Reuse the profile gate for per-player rate limiting before validating a target.
    local result = store:handle(player.UserId, if selectRequest then {action="GetState"} else payload, now)
    if result.ok and selectRequest then
        local valid=type(payload.nodeId)=="string" and #payload.nodeId<=64
        local count=0
        for key in payload do
            count+=1
            if count>2 or (key~="action" and key~="nodeId") then valid=false; break end
        end
        if not valid then result={ok=false,code="InvalidRequest"}
        else
            local ok,code=mining:select(player.UserId,payload.nodeId,now,distance(player,payload.nodeId),#result.state.profile.EquippedPetIds>0)
            result=if ok then result else {ok=false,code=code}
        end
    elseif result.ok and (payload.action=="RecallTeam" or payload.action=="UnequipPet" or payload.action=="EquipPet") then
        mining:recall(player.UserId)
    end
    decorate(player.UserId,result)
    -- Silence floods rather than echoing every rejected packet.
    if result.code ~= "RateLimited" and player.Parent == Players then
        response:FireClient(player, result)
    end
end)

local function added(player)
    local ok, reason = store:open(player.UserId)
    if ok then
        mining:open(player.UserId)
        player.CharacterRemoving:Connect(function()
            mining:recall(player.UserId)
            if player.Parent==Players then
                response:FireClient(player,decorate(player.UserId,{ok=true,code="OK",state=store:snapshot(player.UserId)}))
            end
        end)
        print("[Server] Temporary profile ready for " .. player.Name .. " (MemoryOnly)")
    elseif reason ~= "AlreadyOpen" then
        warn("[Server] Could not create profile: " .. tostring(reason))
        player:Kick("Не удалось создать тестовый профиль. Попробуй зайти снова.")
    end
end
Players.PlayerAdded:Connect(added)
Players.PlayerRemoving:Connect(function(player) mining:close(player.UserId); store:close(player.UserId) end)
for _, player in Players:GetPlayers() do added(player) end
-- Publish only after handlers and current player profiles are ready.
network.Parent = ReplicatedStorage
task.spawn(function()
    while true do
        task.wait(0.1)
        for _,player in Players:GetPlayers() do
            local s=store:snapshot(player.UserId)
            local m=mining:snapshot(player.UserId)
            if s and m and mining:tick(player.UserId,os.clock(),distance(player,m.targetId),#s.profile.EquippedPetIds>0) then
                response:FireClient(player,decorate(player.UserId,{ok=true,code="OK",state=store:snapshot(player.UserId)}))
            end
        end
    end
end)
print("[Server] Stage 4 ready. Progress is temporary; saving is not connected.")
