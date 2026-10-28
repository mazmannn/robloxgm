local ReplicatedStorage = game:GetService("ReplicatedStorage")
local network = ReplicatedStorage:WaitForChild("GameNetwork", 15)
if not network then
    warn("[Client] GameNetwork missing; check the server Output")
    return
end
local request = network:WaitForChild("Request")
local response = network:WaitForChild("Response")
local updateView = require(script.Parent:WaitForChild("MiningView")).start(request)
local receivedState = false
local currentState = nil
response.OnClientEvent:Connect(function(result)
    updateView(result)
    if result.ok and result.state then
        currentState = result.state
        receivedState = true
        print(string.format("[Client] Profile received: schema %d, team %d, storage %s",
            currentState.profile.SchemaVersion, #currentState.profile.EquippedPetIds,
            currentState.storageMode))
    else
        warn("[Client] Request rejected: " .. tostring(result.code))
    end
end)

-- Bounded startup retry for a player joining while server setup completes.
for _ = 1, 10 do
    request:FireServer({action = "GetState"})
    task.wait(1)
    if receivedState then break end
end
if not receivedState then warn("[Client] Profile was not received; check server Output") end
