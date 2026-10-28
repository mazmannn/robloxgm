-- One-time creation only. Never overwrite the map edited in Studio.
local fs = require("@lune/fs")
local roblox = require("@lune/roblox")
assert(not fs.isFile("MythicPets.rbxl"), "MythicPets.rbxl already exists; open it in Studio instead")
local place = roblox.deserializePlace(fs.readFile("rojo-check.rbxl"))
local workspace = place:GetService("Workspace")
local base = roblox.Instance.new("Part")
base.Name = "Baseplate"
base.Anchored = true
base.Size = roblox.Vector3.new(160, 1, 160)
base.Position = roblox.Vector3.new(0, -0.5, 0)
base.Color = roblox.Color3.fromRGB(113, 146, 105)
base.Parent = workspace
local spawn = roblox.Instance.new("SpawnLocation")
spawn.Name = "Spawn"
spawn.Anchored = true
spawn.Size = roblox.Vector3.new(8, 1, 8)
spawn.Position = roblox.Vector3.new(0, 0.5, 0)
spawn.Neutral = true
spawn.Parent = workspace
fs.writeFile("MythicPets.rbxl", roblox.serializePlace(place))
local reopened = roblox.deserializePlace(fs.readFile("MythicPets.rbxl"))
assert(reopened:GetService("Workspace"):FindFirstChild("Baseplate"))
assert(reopened:GetService("Workspace"):FindFirstChild("Spawn").ClassName == "SpawnLocation")
print("Created and reopened MythicPets.rbxl: baseplate, spawn, Stage 3 scripts")
