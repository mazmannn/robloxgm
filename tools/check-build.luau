local fs = require("@lune/fs")
local luau = require("@lune/luau")
local roblox = require("@lune/roblox")
local count = 0
local function compileDirectory(path)
    for _, name in fs.readDir(path) do
        local child = path .. "/" .. name
        if fs.isDir(child) then
            compileDirectory(child)
        elseif string.match(name, "%.luau$") then
            luau.compile(fs.readFile(child))
            count += 1
        end
    end
end
compileDirectory("src")
compileDirectory("tests")
compileDirectory("tools")
local place = roblox.deserializePlace(fs.readFile("rojo-check.rbxl"))
local server = place:GetService("ServerScriptService"):FindFirstChild("GameServer")
assert(server and server:FindFirstChild("ProfileStore").ClassName == "ModuleScript", "Missing server domain")
assert(server:FindFirstChild("main").ClassName == "Script", "Missing server bootstrap")
local client = place:GetService("StarterPlayer"):FindFirstChild("StarterPlayerScripts"):FindFirstChild("GameClient")
assert(client and client:FindFirstChild("main").ClassName == "LocalScript", "Missing client bootstrap")
local shared = place:GetService("ReplicatedStorage"):FindFirstChild("Shared")
assert(shared and shared:FindFirstChild("Config") and shared:FindFirstChild("Types"), "Missing shared modules")
print("PASS: " .. count .. " Luau files compiled; Rojo object layout checked")
