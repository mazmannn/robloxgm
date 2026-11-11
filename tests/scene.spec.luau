local rb=require('@lune/roblox')
local Models=require('../src/shared/ReferenceModels')
local Scene=require('../src/server/SceneBuilder')
local maker=Models.new(rb)
local root=rb.Instance.new('Folder')
local pet,paw=maker:pet(root)
assert(pet.PrimaryPart and paw and pet:FindFirstChild('Face'))
local ore=maker:ore(root)
assert(ore.PrimaryPart.CanQuery and ore.PrimaryPart.Transparency==1)
local enemy=maker:enemy(root)
assert(enemy:FindFirstChild('MushroomCap') and enemy:FindFirstChild('Sprout'))
local world=rb.Instance.new('Workspace')
local scene=Scene.build(world,nil,rb)
assert(Scene.build(world,nil,rb)==scene,'opening a baked preview must not duplicate scenery')
assert(scene:FindFirstChild('WayfarerTree') and scene:FindFirstChild('BiomeGate'))
assert(scene:FindFirstChild('ForestPath') and scene:FindFirstChild('HubSpawn'))
assert(scene.HubPlateau.Size.X==200 and scene.HubPlateau.Size.Z==200,'full hub footprint')
assert(scene.HubSpawn.CFrame.Position.Z==38,'spawn remains within hub')
assert(not scene:FindFirstChild('House',true) and not scene:FindFirstChild('Shop',true))
local count=0
for _,parent in {root,scene} do
    for _,p in parent:GetDescendants() do
        if p:IsA('BasePart') then
            count+=1
            assert(p.Anchored and p.Size.X>0 and p.Size.Y>0 and p.Size.Z>0)
            for _,n in {p.CFrame:GetComponents()} do assert(n==n and math.abs(n)<10000,'invalid geometry: '..p:GetFullName()) end
        end
    end
end
assert(count<3500,'scene geometry budget exceeded')
print('PASS reference scene: model hitboxes, finite geometry, landmarks, no houses; '..count..' parts')
