-- Small deterministic geometry toolkit. Engine injection also permits offline model checks.
local Geometry={}
function Geometry.new(engine)
    local E=engine or {Instance=Instance,Vector3=Vector3,CFrame=CFrame,Color3=Color3,Enum=Enum}
    local V,CF=E.Vector3,E.CFrame
    local g={V=V,CF=CF,E=E}
    function g.color(r,b,c) return E.Color3.fromRGB(r,b,c) end
    function g.model(parent,name)
        local m=E.Instance.new('Model'); m.Name=name; m.Parent=parent; return m
    end
    function g.part(parent,name,size,color,cf,shape,collide)
        local p=E.Instance.new('Part'); p.Name=name; p.Size=size; p.CFrame=cf
        p.Color=color; p.Anchored=true; p.CanCollide=collide==true; p.CanTouch=false; p.CanQuery=collide==true
        p.Material=E.Enum.Material.SmoothPlastic
        p.TopSurface=E.Enum.SurfaceType.Smooth; p.BottomSurface=E.Enum.SurfaceType.Smooth
        if shape then p.Shape=shape end
        p.Parent=parent; return p
    end
    function g.beam(parent,name,a,b,width,color)
        local center=(a+b)/2
        local direction=(b-a).Unit
        local up=if math.abs(direction.Y)>.98 then V.new(1,0,0) else V.new(0,1,0)
        return g.part(parent,name,V.new(width,(b-a).Magnitude,width),color,
            CF.lookAt(center,b,up)*CF.Angles(math.pi/2,0,0))
    end
    function g.triangle(parent,a,b,c,color)
        local ab,ac,bc=b-a,c-a,c-b
        if ab.Magnitude>ac.Magnitude and ab.Magnitude>bc.Magnitude then c,a=a,c
        elseif ac.Magnitude>bc.Magnitude and ac.Magnitude>ab.Magnitude then a,b=b,a end
        ab,ac,bc=b-a,c-a,c-b
        local normal=ac:Cross(ab)
        if normal.Magnitude<.00001 then return end
        local right=normal.Unit; local back=bc.Unit; local up=bc:Cross(right).Unit
        local h=math.abs(ab:Dot(up))
        for _,s in {{a,b,right,back,math.abs(ab:Dot(back))},{a,c,-right,-back,math.abs(ac:Dot(back))}} do
            if s[5]>.00001 then
                local w=E.Instance.new('WedgePart'); w.Name='Facet'; w.Size=V.new(.025,h,s[5])
                w.CFrame=CF.fromMatrix((s[1]+s[2])/2,s[3],up,s[4]); w.Color=color
                w.Material=E.Enum.Material.SmoothPlastic; w.Anchored=true
                w.CanCollide=false; w.CanQuery=false; w.CanTouch=false; w.Parent=parent
            end
        end
    end
    -- Octagonal bipyramid: flat shading is real geometry, without realistic textures.
    function g.gem(parent,name,cf,size,color,sides)
        local m=g.model(parent,name); sides=sides or 7
        local points={}
        for i=1,sides do
            local angle=(i-1)*math.pi*2/sides
            points[i]=cf:PointToWorldSpace(V.new(math.cos(angle)*size.X/2,0,math.sin(angle)*size.Z/2))
        end
        local top=cf:PointToWorldSpace(V.new(0,size.Y/2,0))
        local bottom=cf:PointToWorldSpace(V.new(0,-size.Y/2,0))
        for i=1,sides do
            local shade=.84+.16*((i%3)/2)
            local col=E.Color3.new(color.R*shade,color.G*shade,color.B*shade)
            g.triangle(m,top,points[i],points[i%sides+1],col)
            g.triangle(m,bottom,points[i%sides+1],points[i],col)
        end
        return m
    end
    function g.hitbox(parent,size,cf)
        local p=g.part(parent,'Hitbox',size,E.Color3.new(1,1,1),cf)
        p.Transparency=1; p.CanQuery=true; parent.PrimaryPart=p; return p
    end
    function g.blob(parent,name,cf,size,color,sides)
        local m=g.model(parent,name); sides=sides or 8
        local rings={}
        for j=1,3 do
            rings[j]={}; local latitude=(j-2)*math.pi/4
            for i=1,sides do
                local a=(i-1)*math.pi*2/sides
                rings[j][i]=cf:PointToWorldSpace(V.new(math.cos(a)*math.cos(latitude)*size.X/2,math.sin(latitude)*size.Y/2,math.sin(a)*math.cos(latitude)*size.Z/2))
            end
        end
        local top=cf:PointToWorldSpace(V.new(0,size.Y/2,0)); local bottom=cf:PointToWorldSpace(V.new(0,-size.Y/2,0))
        for i=1,sides do
            local k=i%sides+1
            local shade=.9+.1*((i%3)/2)
            local c=E.Color3.new(color.R*shade,color.G*shade,color.B*shade)
            g.triangle(m,bottom,rings[1][k],rings[1][i],c)
            g.triangle(m,top,rings[3][i],rings[3][k],c)
            for j=1,2 do
                g.triangle(m,rings[j][i],rings[j][k],rings[j+1][i],c)
                g.triangle(m,rings[j+1][i],rings[j][k],rings[j+1][k],c)
            end
        end
        return m
    end
    function g.cone(parent,name,cf,size,color)
        local m=g.model(parent,name)
        for i=1,6 do
            local a,b=(i-1)*math.pi/3,i*math.pi/3
            local shade=.88+.12*(i%2)
            local c=E.Color3.new(color.R*shade,color.G*shade,color.B*shade)
            g.triangle(m,cf:PointToWorldSpace(V.new(0,size.Y/2,0)),
                cf:PointToWorldSpace(V.new(math.cos(a)*size.X/2,-size.Y/2,math.sin(a)*size.Z/2)),
                cf:PointToWorldSpace(V.new(math.cos(b)*size.X/2,-size.Y/2,math.sin(b)*size.Z/2)),c)
        end
        return m
    end
    function g.leaf(parent,name,at,size,rotation)
        return g.gem(parent,name,CF.new(at)*CF.Angles(0,0,rotation or 0),size,g.color(119,164,57),4)
    end
    return g
end
return Geometry
