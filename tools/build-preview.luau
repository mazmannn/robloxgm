-- Preserve the map on disk; refresh only Rojo-owned folders in a generated preview.
local fs=require("@lune/fs")
local rb=require("@lune/roblox")
local map=rb.deserializePlace(fs.readFile("MythicPets.rbxl"))
local code=rb.deserializePlace(fs.readFile("rojo-check.rbxl"))
local function replace(parent,source,name)
    local old=parent:FindFirstChild(name)
    if old then old:Destroy() end
    source:FindFirstChild(name):Clone().Parent=parent
end
replace(map:GetService("ServerScriptService"),code:GetService("ServerScriptService"),"GameServer")
replace(map:GetService("ReplicatedStorage"),code:GetService("ReplicatedStorage"),"Shared")
replace(map:GetService("StarterPlayer"):FindFirstChild("StarterPlayerScripts"),code:GetService("StarterPlayer"):FindFirstChild("StarterPlayerScripts"),"GameClient")
require('../src/server/SceneBuilder').build(map:GetService('Workspace'),map:GetService('Lighting'),rb)
local camera=map:GetService('Workspace'):FindFirstChildOfClass('Camera')
if camera then camera.CFrame=rb.CFrame.lookAt(rb.Vector3.new(155,145,190),rb.Vector3.new(-25,23,-22)) end
fs.writeFile("download/stage4-preview.rbxl",rb.serializePlace(map))
fs.writeFile("download/reference-preview.rbxl",rb.serializePlace(map))
print("Preview created: download/stage4-preview.rbxl; original map preserved")
