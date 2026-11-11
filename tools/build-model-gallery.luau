local fs=require('@lune/fs')
local serde=require('@lune/serde')
local rb=require('@lune/roblox')
local g=require('../src/shared/Geometry').new(rb)
local V,CF=rb.Vector3,rb.CFrame
local data=serde.decode('json',fs.readFile('download/gallery-geometry.json'))
assert(#data==22,'Expected 22 current models')
local place=rb.deserializePlace(fs.readFile('rojo-check.rbxl'))
for _,service in {'Workspace','ServerScriptService','ReplicatedStorage','StarterGui','StarterPack','StarterPlayer'} do
 for _,o in place:GetService(service):GetChildren() do o:Destroy() end
end
local ws=place:GetService('Workspace')
local floor=g.part(ws,'Gallery floor',V.new(160,1,170),rb.Color3.fromRGB(111,127,103),CF.new(0,-.5,55),nil,true)
local spawn=rb.Instance.new('SpawnLocation');spawn.Name='Gallery spawn';spawn.Size=V.new(7,.4,7);spawn.CFrame=CF.new(0,.2,-23)
spawn.Anchored=true;spawn.Neutral=true;spawn.Parent=ws
local function label(parent,name,at,text)
 local post=g.part(parent,name,V.new(10,2.5,.2),rb.Color3.fromRGB(44,51,58),CF.new(at))
 for _,side in {rb.Enum.NormalId.Front,rb.Enum.NormalId.Back} do
  local gui=rb.Instance.new('SurfaceGui');gui.Face=side;gui.CanvasSize=rb.Vector2.new(800,200);gui.Parent=post
  local t=rb.Instance.new('TextLabel');t.Size=rb.UDim2.fromScale(1,1);t.BackgroundTransparency=1;t.TextColor3=rb.Color3.new(1,1,1)
  t.TextScaled=true;t.Text=text;t.Parent=gui
 end
end
local count=0
for i,item in data do
 local x=((i-1)%5-2)*29;local z=math.floor((i-1)/5)*30
 local model=g.model(ws,item.name)
 model:SetAttribute('Source','Blender geometry; local triangle preview')
 local offset=V.new(x,.35,z)
 local vertices={}
 for j,p in item.vertices do vertices[j]=V.new(p[1],p[2],p[3])+offset end
 local pad=g.part(model,'Display base',V.new(26,.3,25),rb.Color3.fromRGB(161,156,139),CF.new(x,.15,z),nil,true)
 for _,t in item.triangles do
  local c=item.colors[t[4]]
  local old=if c[4] then #model:GetChildren() else 0
  g.triangle(model,vertices[t[1]],vertices[t[2]],vertices[t[3]],rb.Color3.new(c[1],c[2],c[3]))
  if c[4] then
   local children=model:GetChildren()
   for j=old+1,#children do children[j].Material=rb.Enum.Material.Neon end
  end
 end
 label(model,'Model label',V.new(x,1.9,z+12),item.name)
 count+=1
 print('PLACED',item.name,#model:GetChildren())
end
label(ws,'Welcome',V.new(0,3,-32),'MODEL GALLERY / 22 Blender models')
local lighting=place:GetService('Lighting');lighting.ClockTime=13;lighting.Brightness=2;lighting.Ambient=rb.Color3.fromRGB(145,145,145)
lighting.OutdoorAmbient=rb.Color3.fromRGB(160,160,160)
local camera=rb.Instance.new('Camera');camera.Name='Camera';camera.CFrame=CF.lookAt(V.new(95,110,170),V.new(0,5,45));camera.Parent=ws
local output='download/model-gallery.rbxl'
assert(not fs.isFile(output),'Gallery already exists; preserve user edits and choose a new output filename')
fs.writeFile(output,rb.serializePlace(place))
local reopened=rb.deserializePlace(fs.readFile(output));local rw=reopened:GetService('Workspace')
for _,item in data do assert(rw:FindFirstChild(item.name),'Missing '..item.name) end
assert(rw:FindFirstChild('Gallery spawn'))
local parts=0
for _,o in rw:GetDescendants() do if o:IsA('BasePart') then parts+=1;assert(o.Anchored) end end
fs.writeFile('download/model-gallery-report.json',serde.encode('json',{models=count,parts=parts,reopened=true,format='Offline triangle preview; not uploaded MeshParts'}))
print('GALLERY_VERIFIED',output,count,parts)
