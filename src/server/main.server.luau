local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")
local Config = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config"))
local ProfileStore = require(script.Parent:WaitForChild("ProfileStore"))
local store = ProfileStore.new(Config, function() return HttpService:GenerateGUID(false) end)

-- Runtime objects are created by the server, outside the Shared source folder.
local network = Instance.new("Folder")
network.Name = "GameNetwork"
local request = Instance.new("RemoteEvent")
request.Name = "Request"
request.Parent = network
local response = Instance.new("RemoteEvent")
response.Name = "Response"
response.Parent = network

request.OnServerEvent:Connect(function(player, payload)
    -- Player comes from Roblox, never from a client-controlled userId.
    local result = store:handle(player.UserId, payload, os.clock())
    -- Silence floods rather than echoing every rejected packet.
    if result.code ~= "RateLimited" and player.Parent == Players then
        response:FireClient(player, result)
    end
end)

local function added(player)
    local ok, reason = store:open(player.UserId)
    if ok then
        print("[Server] Temporary profile ready for " .. player.Name .. " (MemoryOnly)")
    elseif reason ~= "AlreadyOpen" then
        warn("[Server] Could not create profile: " .. tostring(reason))
        player:Kick("Не удалось создать тестовый профиль. Попробуй зайти снова.")
    end
end
Players.PlayerAdded:Connect(added)
Players.PlayerRemoving:Connect(function(player) store:close(player.UserId) end)
for _, player in Players:GetPlayers() do added(player) end
-- Publish only after handlers and current player profiles are ready.
network.Parent = ReplicatedStorage
print("[Server] Stage 3 ready. Progress is temporary; saving is not connected.")
