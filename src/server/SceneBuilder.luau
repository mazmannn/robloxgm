local Models=if script then require(game:GetService('ReplicatedStorage').Shared.ReferenceModels) else require('../shared/ReferenceModels')
local Scene={}
function Scene.build(world,lighting,engine)
    local existing=world:FindFirstChild('ReferenceWorld')
    if existing then return existing end
    local maker=Models.new(engine); local g=maker.geometry
    local V,CF,col=g.V,g.CF,g.color
    local scene=g.model(world,'ReferenceWorld')
    local ground=20
    local grass=col(106,132,76); local stone=col(118,130,139); local wood=col(115,80,45)
    local function solid(parent,name,size,color,cf,shape)
        return g.part(parent,name,size,color,cf,shape,true)
    end
    local function tile(parent,x,z,w,d,color,y)
        return solid(parent,'PathStone',V.new(w,.18,d),color,CF.new(x,y or ground+.06,z))
    end
    -- A raised plateau keeps the generated scene separate from the user's existing terrain.
    solid(scene,'HubPlateau',V.new(200,7,200),grass,CF.new(0,ground-3.5,0))
    solid(scene,'ForestPlateau',V.new(126,7,117),col(95,122,73),CF.new(-138.6,ground-3.5,-104.4))
    local path=g.model(scene,'ForestPath')
    local function trail(parent,a,b,width)
        local delta=b-a; local n=math.ceil(delta.Magnitude/5)
        for i=0,n do
            local p=a:Lerp(b,i/n)
            local t=tile(parent,p.X,p.Z,width,5.3,col(174+(i%3)*4,151+(i%2)*3,109))
            t.CFrame=CF.lookAt(V.new(p.X,ground+.08,p.Z),V.new(b.X,ground+.08,b.Z)+delta.Unit*.01)
        end
    end
    trail(path,V.new(-30,0,-16),V.new(-118.8,0,-86.4),14)
    trail(path,V.new(-118.8,0,-86.4),V.new(-169.2,0,-129.6),12)
    trail(scene,V.new(0,0,40),V.new(0,0,-84),16)
    trail(scene,V.new(-64,0,0),V.new(64,0,0),14)
    -- Circular stone plaza and the warm central landmark.
    local plaza=solid(scene,'Plaza',V.new(.35,60,60),col(150,148,124),CF.new(0,ground+.06,0)*CF.Angles(0,0,math.pi/2),g.E.Enum.PartType.Cylinder)
    for i=1,20 do
        local a=i*math.pi/10
        solid(scene,'PlazaRim',V.new(9,.5,1.2),col(128,139,139),CF.new(math.sin(a)*30,ground+.22,math.cos(a)*30)*CF.Angles(0,a,0))
    end
    local tree=g.model(scene,'WayfarerTree')
    local ring=solid(tree,'TreeIsland',V.new(.7,15,15),col(93,128,67),CF.new(0,ground+.4,0)*CF.Angles(0,0,math.pi/2),g.E.Enum.PartType.Cylinder)
    for i=1,8 do
        local a=i*math.pi/4
        g.beam(tree,'Root',V.new(math.sin(a)*5,ground+.75,math.cos(a)*5),V.new(0,ground+3,0),1,col(126,85,45))
    end
    solid(tree,'Trunk',V.new(4,11,3.4),wood,CF.new(0,ground+6,0)*CF.Angles(0,0,-.08))
    for i=1,6 do
        local a=i*math.pi/3
        local at=V.new(math.sin(a)*5,ground+13+(i%2)*1.7,math.cos(a)*4)
        g.beam(tree,'Branch',V.new(0,ground+8,0),at,1.4,wood)
        g.blob(tree,'Crown',CF.new(at),V.new(9,6,8),col(104+(i%2)*9,147,68),6)
        local rune=g.gem(tree,'BlueRune',CF.new(math.sin(a)*2.2,ground+6+(i%3),math.cos(a)*1.9),V.new(.45,1,.3),col(83,195,231),4)
        for _,p in rune:GetDescendants() do if p:IsA('BasePart') then p.Material=g.E.Enum.Material.Neon end end
    end
    g.blob(tree,'TopCrown',CF.new(0,ground+17,0),V.new(10,7,9),col(125,159,73),6)
    -- Decorative gateway. No new teleport/gameplay system is inferred from the image.
    local gate=g.model(scene,'BiomeGate')
    for _,x in {-11,11} do
        solid(gate,'Foundation',V.new(6,2,6),stone,CF.new(x,ground+1,-45))
        solid(gate,'Pillar',V.new(3.6,16,4),stone,CF.new(x,ground+9,-45))
        for i=1,4 do solid(gate,'PillarBand',V.new(4,.45,4.5),col(144,153,157),CF.new(x,ground+i*3.5,-45)) end
        g.gem(gate,'PillarCap',CF.new(x,ground+19,-45),V.new(6,4,6),col(101,124,143),4)
        local banner=g.part(gate,'BlueBanner',V.new(2.5,8,.15),col(51,99,147),CF.new(x,ground+11,-47.1))
        g.part(gate,'GoldStripe',V.new(.35,7,.16),col(211,165,75),banner.CFrame*CF.new(0,0,-.1))
    end
    for i=0,8 do
        local a=i*math.pi/8
        solid(gate,'ArchStone',V.new(4.25,3.3,4),col(121+(i%2)*12,135+(i%2)*10,146+(i%2)*8),
            CF.new(math.cos(a)*10,ground+16+math.sin(a)*8,-45)*CF.Angles(0,0,a-math.pi/2))
    end
    for i=1,3 do solid(gate,'Step',V.new(16,.45,3),col(147,152,142),CF.new(0,ground+.15+i*.15,-37-i*2.3)) end
    -- Move the gateway as a whole: architectural proportions remain unchanged.
    for _,part in gate:GetDescendants() do
        if part:IsA('BasePart') then part.CFrame=part.CFrame+V.new(0,0,-36) end
    end
    local function pine(parent,x,z,height)
        local t=g.model(parent,'Pine')
        g.part(t,'Trunk',V.new(.8,height*.65,.8),wood,CF.new(x,ground+height*.3,z))
        for level=1,3 do
            local s=height*(.85-level*.16)
            g.cone(t,'Needles',CF.new(x,ground+height*(.25+level*.21),z),V.new(s,height*.7,s),
                col(52+level*7,103+level*9,74+level*3))
        end
    end
    local forest=g.model(scene,'Forest')
    for _,p in { {-34,-35,13},{-45,-48,15},{-52,-24,13},{-70,-29,16},{-80,-43,15},{-98,-51,17},{-77,-80,16},{-99,-88,17},{-56,-73,15},
        {42,-39,16},{35,-50,14},{-34,37,13},{43,30,12},{-42,24,14},{29,43,12},{47,-16,13},{-23,-48,13} } do pine(forest,p[1]*1.8,p[2]*1.8,p[3]) end
    local cliffs=g.model(scene,'Cliffs')
    for i=1,16 do
        local a=i*math.pi/8
        local x,z=math.sin(a)*95,math.cos(a)*95
        -- Leave open the gate and forest route.
        if not (z < -79 and math.abs(x)<26) and not (x< -54 and z< -22) then
            solid(cliffs,'RockCore',V.new(10,8+(i%3)*3,11),stone,CF.new(x,ground-2,z)*CF.Angles(.05*i,.4*i,.08))
            g.gem(cliffs,'RockFace',CF.new(x,ground+3,z),V.new(14,15,13),stone,5)
        end
    end
    local fence=g.model(scene,'Fences')
    for _,line in { {-37,4,-37,30},{28,32,45,32},{-49,-34,-65,-47} } do
        local a,b=V.new(line[1]*1.8,ground,line[2]*1.8),V.new(line[3]*1.8,ground,line[4]*1.8)
        local n=math.ceil((b-a).Magnitude/6)
        for i=0,n do local p=a:Lerp(b,i/n); g.part(fence,'Post',V.new(.55,2.5,.55),wood,CF.new(p+V.new(0,1.25,0))) end
        for _,y in {.8,1.8} do g.beam(fence,'Rail',a+V.new(0,y,0),b+V.new(0,y,0),.25,wood) end
    end
    for _,p in { {-15,17},{15,17},{-16,-23},{17,-29},{-38,-24},{-78,-58} } do
        local at=V.new(p[1]*1.8,ground,p[2]*1.8); local lamp=g.model(scene,'Lantern')
        g.part(lamp,'Post',V.new(.35,5,.35),wood,CF.new(at+V.new(0,2.5,0)))
        g.part(lamp,'Arm',V.new(1.7,.3,.3),wood,CF.new(at+V.new(.7,5,0)))
        local light=g.part(lamp,'WarmGlass',V.new(.65,1,.65),col(255,201,111),CF.new(at+V.new(1.35,4.15,0)))
        light.Material=g.E.Enum.Material.Neon
        g.gem(lamp,'Roof',CF.new(at+V.new(1.35,4.8,0)),V.new(1.15,.55,1.1),col(79,79,63),4)
    end
    -- Small grass tufts at deterministic positions, avoiding walkways and targets.
    for i=1,34 do
        local a=i*2.399963; local r=46+(i%5)*5
        local x,z=math.cos(a)*r,math.sin(a)*r
        if math.abs(x)>9 and math.abs(z)>9 and not (x< -18 and z< -10) then
            g.leaf(scene,'GroundPlant',V.new(x,ground+.65,z),V.new(.8,1.3,.18),.35)
            g.leaf(scene,'GroundPlant',V.new(x+.4,ground+.5,z),V.new(.6,1,.18),-.5)
        end
    end
    local spawn=g.E.Instance.new('SpawnLocation'); spawn.Name='HubSpawn'; spawn.Size=V.new(5,.2,5)
    spawn.CFrame=CF.new(0,ground+.3,38); spawn.Transparency=1; spawn.Anchored=true
    spawn.CanCollide=false; spawn.Neutral=true; spawn.Duration=0; spawn.Parent=scene
    -- Old spawn remains intact on disk and is only disabled while this scene runs.
    for _,p in world:GetDescendants() do if p:IsA('SpawnLocation') and p~=spawn then p.Enabled=false end end
    if lighting then
        lighting.ClockTime=13.5; lighting.Brightness=2
        lighting.Ambient=col(157,169,159); lighting.OutdoorAmbient=col(165,180,174)
        lighting.GlobalShadows=false; lighting.FogColor=col(165,202,213); lighting.FogStart=170; lighting.FogEnd=400
    end
    scene:SetAttribute('GroundY',ground)
    return scene
end
return Scene
