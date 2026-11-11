local Geometry=if script then require(script.Parent.Geometry) else require('./Geometry')
local Models={}
function Models.new(engine)
    local g=Geometry.new(engine); local V,CF=g.V,g.CF; local col=g.color
    local self={geometry=g}
    function self:pet(parent)
        local m=g.model(parent,'MossCompanion')
        local root=g.hitbox(m,V.new(2.5,2.6,2.4),CF.new(0,1.45,0)); root.CanQuery=false
        -- Round, faceted head with a cream muzzle and a deliberately smaller body.
        g.blob(m,'MossHead',CF.new(0,1.6,0),V.new(2.65,2.6,2.4),col(137,179,63),8)
        g.blob(m,'Face',CF.new(0,1.48,-.98),V.new(1.9,1.8,.66),col(245,225,171),8)
        for _,x in {-.42,.42} do
            g.part(m,'Eye',V.new(.22,.29,.14),col(41,31,23),CF.new(x,1.65,-1.24),g.E.Enum.PartType.Ball)
            g.part(m,'Cheek',V.new(.28,.13,.08),col(224,152,119),CF.new(x*1.65,1.37,-1.19),g.E.Enum.PartType.Ball)
            g.gem(m,'Foot',CF.new(x,.28,-.1),V.new(.62,.52,.72),col(157,125,72),6)
            g.beam(m,'Twig',V.new(x,2.45,0),V.new(x*1.3,3.2,.02),.16,col(116,77,40))
            g.leaf(m,'Leaf',V.new(x*1.85,3.04,0),V.new(.55,.9,.14),-x*.8)
            g.leaf(m,'Leaf',V.new(x*.9,3.34,.02),V.new(.42,.68,.12),x*.7)
        end
        for i=1,5 do
            local a=i*math.pi/4
            g.gem(m,'MossTuft',CF.new(math.cos(a)*.96,1.9+math.sin(a)*.45,.22+math.sin(a)*.6),V.new(.7,.65,.65),col(139+(i%3)*7,182,62),5)
        end
        -- Two curved-looking short strokes preserve the tiny w-shaped mouth.
        g.beam(m,'Smile',V.new(-.16,1.38,-1.28),V.new(0,1.30,-1.29),.055,col(65,44,28))
        g.beam(m,'Smile',V.new(0,1.30,-1.29),V.new(.16,1.38,-1.28),.055,col(65,44,28))
        local paw=g.part(m,'RightPaw',V.new(.58,.65,.6),col(145,186,68),CF.new(1,1.05,-.3),g.E.Enum.PartType.Ball)
        return m,paw
    end
    function self:ore(parent)
        local m=g.model(parent,'CopperOutcrop')
        g.hitbox(m,V.new(5.4,4,4.3),CF.new(0,2,0))
        for i,data in {{-1.4,1.25,.1,2.7,2.6,2.9},{.5,1.7,.2,3.1,3.6,3},{1.7,.8,-.4,2.3,1.8,2.4},{-.2,1,-1.2,2.8,2.3,2}} do
            local x,y,z,sx,sy,sz=table.unpack(data)
            g.gem(m,'Rock',CF.new(x,y,z)*CF.Angles(.1*i,.32*i,.12*i),V.new(sx,sy,sz),col(83+i*3,83+i*2,93+i*2),6)
        end
        for i,p in {V.new(-1.6,1.9,-.9),V.new(.2,2.4,-1),V.new(1.5,1.4,-1.1),V.new(.6,3.1,.4),V.new(-.6,.65,-1.7)} do
            local gem=g.gem(m,'Copper',CF.new(p)*CF.Angles(.2*i,.3*i,.15*i),V.new(.75,1.05,.6),col(255,142,52),5)
            for _,f in gem:GetDescendants() do if f:IsA('BasePart') then f.Material=g.E.Enum.Material.Neon end end
        end
        return m
    end
    function self:enemy(parent)
        local m=g.model(parent,'Penkun'); local bark=col(114,75,45)
        g.hitbox(m,V.new(4.8,4.4,3.5),CF.new(0,2.2,0))
        -- Bark is made of separate tapered staves around an octagonal stump.
        for i=1,10 do
            local a=(i-1)*math.pi/5
            g.part(m,'Bark',V.new(1.05,2.9,.5),col(107+(i%3)*12,70+(i%3)*8,40+(i%3)*5),
                CF.new(math.sin(a)*1.35,2.15,math.cos(a)*1.08)*CF.Angles(.1*math.cos(a),a,.05*math.sin(a)))
        end
        local top=g.part(m,'CutTop',V.new(.2,2.9,2.9),col(189,145,85),CF.new(0,3.66,0)*CF.Angles(0,0,math.pi/2),g.E.Enum.PartType.Cylinder)
        for i=1,3 do
            local a=i*.6
            g.beam(m,'GrowthRing',V.new(-.65,3.78,a-.9),V.new(.6,3.78,a-.95),.045,col(145,103,58))
        end
        g.part(m,'FaceShadow',V.new(2.25,.85,.12),col(42,30,21),CF.new(0,2.25,-1.36))
        for _,x in {-.62,.62} do
            g.part(m,'Eye',V.new(.45,.38,.14),col(250,218,136),CF.new(x,2.2,-1.47),g.E.Enum.PartType.Ball)
            g.part(m,'Pupil',V.new(.15,.27,.08),col(27,24,20),CF.new(x,2.2,-1.56))
            g.part(m,'Brow',V.new(1.12,.32,.32),bark,CF.new(x,2.65,-1.48)*CF.Angles(0,0,-x*.4))
            g.gem(m,'Foot',CF.new(x,.35,-.1),V.new(1.15,.7,1.45),bark,6)
            g.beam(m,'BranchArm',V.new(x*2,2.8,0),V.new(x*3.1,1.7,-.1),.35,bark)
            g.beam(m,'Hand',V.new(x*3.1,1.7,-.1),V.new(x*3.3,1.05,-.4),.27,bark)
            for k=1,2 do g.beam(m,'Finger',V.new(x*3.3,1.05,-.4),V.new(x*(3.15+k*.12),.8,-.65+k*.18),.12,bark) end
            g.leaf(m,'ArmLeaf',V.new(x*3.2,2,-.1),V.new(.65,.95,.2),-x)
            g.gem(m,'MossPatch',CF.new(x*1.5,3,-.7),V.new(.9,.22,.8),col(118,151,55),5)
        end
        g.beam(m,'SproutStem',V.new(-.4,3.7,0),V.new(-.4,4.65,0),.15,col(87,118,42))
        g.leaf(m,'Sprout',V.new(-.65,4.6,0),V.new(.65,1.15,.16),.45)
        g.leaf(m,'SproutLeaf',V.new(-.05,4.55,0),V.new(.65,1,.16),-.55)
        g.beam(m,'MushroomStem',V.new(.75,3.6,.15),V.new(.85,4.25,.15),.28,col(236,216,165))
        g.gem(m,'MushroomCap',CF.new(.85,4.3,.15),V.new(1.2,.65,1.15),col(213,91,49),7)
        g.part(m,'MushroomSpot',V.new(.2,.06,.24),col(251,226,168),CF.new(.65,4.59,.12))
        return m
    end
    return self
end
return Models
