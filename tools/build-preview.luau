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
fs.writeFile("download/stage4-preview.rbxl",rb.serializePlace(map))
print("Preview created: download/stage4-preview.rbxl; original map preserved")
