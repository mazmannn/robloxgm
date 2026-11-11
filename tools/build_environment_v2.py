"""Second, independently modelled environment kit. Run in Blender background.
Z up, front -Y, one modelling unit = one intended Roblox stud.
No edits to the first library or Roblox places. --only NAME supports iteration.
"""
import bpy, bmesh, math, random, json, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]/'assets/meshes/EnvironmentV2'
ROOT.mkdir(parents=True,exist_ok=True)
COLORS={
 'beam':'604127','wood':'986039','wood_light':'BA8250','endgrain':'CA925A',
 'plaster':'D0B286','plaster_light':'E0C59B','stone':'6A7787','stone_light':'8D95A1','stone_dark':'535F72',
 'blue':'3565A1','blue_light':'527FB7','red':'A84C39','red_light':'BF6246',
 'brown':'886345','brown_light':'A67C52','green':'5B6742','green_light':'768153',
 'purple':'75558D','purple_light':'9470A7','cream':'E4CEA0','gold':'C29A49',
 'leaf':'658D36','leaf_light':'8CA843','leaf_dark':'486F32','pine':'34634C','pine_light':'487755',
 'grass':'83934A','earth':'645E46','path':'BAA27D','path_light':'C8B38E',
 'iron':'343F4A','dark':'252D33','orange':'FFAF36','cyan':'51D8EF','potion':'45E4AE','water':'408AAB',
 'pink':'C7758A','fur':'DFD0AA','ore':'B67847'}
M={}

def srgb(v):
 v=v/255;return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4

def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 random.seed(2401);M.clear()
 for name,h in COLORS.items():
  color=tuple(srgb(int(h[i:i+2],16)) for i in (0,2,4))+(1,)
  m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True
  p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=color
  p.inputs['Roughness'].default_value=1;p.inputs['Specular IOR Level'].default_value=0
  if name in ('orange','cyan','potion'):
   p.inputs['Emission Color'].default_value=color;p.inputs['Emission Strength'].default_value=.75
  M[name]=m

def finish(o,name,mat):
 o.name=name;o.data.materials.append(M[mat]);return o

def mesh(name,verts,faces,mat):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
 return finish(o,name,mat)

def box(name,p,s,mat='wood',bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=s
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('Hand-cut edge','BEVEL');b.width=min(bevel,min(s)*.2);b.segments=1
  bpy.ops.object.modifier_apply(modifier=b.name)
 return finish(o,name,mat)

def rod(name,a,b,r,mat='beam',r2=None,n=7):
 d=Vector(b)-Vector(a)
 bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(Vector(a)+Vector(b))/2)
 o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
 return finish(o,name,mat)

def timber(name,a,b,w=.4,mat='beam',depth=None):
 d=Vector(b)-Vector(a);o=box(name,(Vector(a)+Vector(b))/2,(w,depth or w,d.length),mat,.035)
 o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o

def ico(name,p,s,mat='leaf',sub=1,seed=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p);o=bpy.context.object
 rng=random.Random(seed)
 for v in o.data.vertices:v.co*=rng.uniform(.94,1.06)
 o.scale=s;return finish(o,name,mat)

def tube(name,points,radii,mat='wood',sides=8):
 verts=[]
 for j,(p,r) in enumerate(zip(points,radii)):
  d=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(j-1,0)])
  q=d.to_track_quat('Z','Y')
  for i in range(sides):
   a=math.tau*i/sides;verts.append(Vector(p)+q@Vector((r*math.cos(a),r*math.sin(a),0)))
 faces=[tuple(reversed(range(sides)))]
 for j in range(len(points)-1):
  for i in range(sides):k=j*sides+i;l=j*sides+(i+1)%sides;faces.append((k,l,l+sides,k+sides))
 faces.append(tuple(range((len(points)-1)*sides,len(points)*sides)))
 return mesh(name,verts,faces,mat)

def ring(name,p,outer,inner,h,mat='stone',n=12):
 verts=[]
 for z,r in [(0,outer),(h,outer),(0,inner),(h,inner)]:
  verts += [(p[0]+r*math.cos(i*math.tau/n),p[1]+r*math.sin(i*math.tau/n),p[2]+z) for i in range(n)]
 faces=[]
 for i in range(n):j=(i+1)%n;faces += [(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(n+i,n+j,3*n+j,3*n+i),(j,i,2*n+i,2*n+j)]
 return mesh(name,verts,faces,mat)

def arch(name,c,inner,outer,depth,start=0,end=math.pi,count=9,mat='stone'):
 for i in range(count):
  a=start+(end-start)*i/count+.008;b=start+(end-start)*(i+1)/count-.008
  v=[(c[0]+r*math.cos(t),c[1]+y,c[2]+r*math.sin(t)) for y in [-depth/2,depth/2] for r,t in [(inner,a),(outer,a),(outer,b),(inner,b)]]
  mesh(name+f'_{i:02}',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone_light' if i%3==0 else mat)

def diamond(name,p,s,mat='cyan'):
 x,y,z=p;w,h=s
 return mesh(name,[(x,y-.1,z+h),(x+w,y-.1,z),(x,y-.1,z-h),(x-w,y-.1,z),(x,y-.3,z),(x,y+.08,z)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(1,0,5),(2,1,5),(3,2,5),(0,3,5)],mat)

def banner(x,y,z,w=1.6,h=3.8):
 v=[(x-w/2,y,z),(x+w/2,y,z),(x+w/2,y-.13,z-h+.65),(x,y-.2,z-h),(x-w/2,y-.13,z-h+.65)]
 o=mesh('Blue pointed banner',v,[(0,4,3,2,1)],'blue');mod=o.modifiers.new('Cloth thickness','SOLIDIFY');mod.thickness=.045
 for side in [-1,1]:timber('Gold embroidered border',(x+side*(w/2-.12),y-.035,z-.1),(x+side*(w/2-.12),y-.17,z-h+.8),.065,'gold')
 diamond('Gold banner emblem',(x,y-.18,z-h*.43),(.23,.62),'gold')
 timber('Banner crossbar',(x-w*.7,y,z+.12),(x+w*.7,y,z+.12),.14,'gold')

def lantern_at(p,scale=1):
 x,y,z=p;s=scale
 box('Amber lantern',(x,y,z),(.52*s,.52*s,.75*s),'orange',.035*s)
 for a in [-1,1]:
  for b in [-1,1]:box('Lantern iron corner',(x+a*.3*s,y+b*.3*s,z),(.075*s,.075*s,.88*s),'iron')
 for dz in [-.48,.48]:box('Lantern rim',(x,y,z+dz*s),(.75*s,.75*s,.13*s),'iron',.025*s)
 rod('Peaked lantern hood',(x,y,z+.52*s),(x,y,z+.83*s),.55*s,'iron',.12*s,4)
 ring_o=ring('Lantern hanger',(0,0,0),.18*s,.12*s,.08*s,'iron',8)
 ring_o.rotation_euler.x=math.pi/2;ring_o.location=(x,y,z+.95*s)

def crate(x,y,z=0,size=1.7,goods=False):
 s=size
 for i in range(4):
  for yy in [-s/2,s/2]:box('Crate horizontal plank',(x,y+yy,z+.17+s*i/4),(s,.13,s*.21),'wood_light' if i%2 else 'wood',.025)
  for xx in [-s/2,s/2]:box('Crate side plank',(x+xx,y,z+.17+s*i/4),(.13,s,s*.21),'wood',.025)
 box('Crate floor',(x,y,z+.07),(s,s,.14),'wood')
 for xx in [-.4,.4]:box('Crate end strap',(x+xx*s,y-s/2-.1,z+s/2),(.16,.12,s),'beam')
 if goods:
  for i in range(5):ico('Stored resource',(x+random.uniform(-s*.3,s*.3),y+random.uniform(-s*.3,s*.3),z+s*.8),(.33,.3,.4),['ore','cyan','leaf_light'][goods%3],1,i)

def barrel(x,y,z=0):
 tube('Faceted barrel',[(x,y,z),(x,y,z+.45),(x,y,z+1.25),(x,y,z+1.7)],[.57,.72,.72,.57],'wood_light',12)
 for zz,r in [(.15,.63),(.55,.75),(1.3,.71),(1.6,.62)]:ring('Iron barrel hoop',(x,y,z+zz),r,r-.08,.12,'iron',12)
 rod('Barrel lid',(x,y,z+1.67),(x,y,z+1.72),.55,'wood',n=12)

def foundation(w,d):
 for y in [-d/2,d/2]:
  n=math.ceil(w/1.6)
  for i in range(n):box('Foundation ashlar',(-w/2+(i+.5)*w/n,y,.45),(w/n-.05,.72,.85),'stone_light' if i%3==0 else 'stone',.08)
 for x in [-w/2,w/2]:
  for i in range(math.ceil(d/1.6)):box('Foundation side ashlar',(x,-d/2+(i+.5)*d/math.ceil(d/1.6),.45),(.72,d/math.ceil(d/1.6)-.05,.85),'stone',.07)

def wall_shell(w,d,eave):
 foundation(w+.3,d+.3)
 box('Solid plaster shell',(0,0,(eave+.8)/2),(w,d,eave-.8),'plaster',.06)
 for x in [-w/2,w/2]:
  for y in [-d/2,d/2]:box('Massive corner timber',(x,y,(eave+.6)/2),(.48,.48,eave+.05),'beam',.055)
 for z in [1.1,eave-.1]:
  for y in [-d/2-.05,d/2+.05]:box('Facade horizontal timber',(0,y,z),(w+.55,.32,.38),'beam',.03)
  for x in [-w/2-.05,w/2+.05]:box('Side horizontal timber',(x,0,z),(.32,d+.5,.38),'beam',.03)
 for x in [-w/2,w/2]:
  for y in [-d/6,d/6]:box('Side wall upright',(x,y,(eave+1)/2),(.3,.3,eave-1),'wood')

def roof(w,d,eave,rise,color,cx=0,cy=0):
 # Slab underlay and independent thick, overlapping hand-cut shingle courses.
 hx=w/2+.75;hy=d/2+.65
 for yy in [-d/2,d/2]:
  mesh('Plaster gable',[(cx-w/2,cy+yy,eave),(cx+w/2,cy+yy,eave),(cx,cy+yy,eave+rise*.93)],[(0,1,2)],'plaster_light')
  timber('Gable kingpost',(cx,cy+yy-.06,eave),(cx,cy+yy-.06,eave+rise-.12),.3)
 for sign in [-1,1]:
  a=(cx,cy-hy,eave+rise);b=(cx+sign*hx,cy-hy,eave-.1)
  mesh('Roof board backing',[a,b,(b[0],cy+hy,b[2]),(a[0],cy+hy,a[2])],[(0,1,2,3)],'beam')
  rows=4;cols=5 if d<8 else 6
  for r in range(rows):
   t0=r/rows;t1=min(1.04,(r+1)/rows+.045)
   for j in range(cols):
    y0=cy-hy+j*2*hy/cols+.018;y1=cy-hy+(j+1)*2*hy/cols-.018
    jitter=random.uniform(-.045,.045);x0=cx+sign*hx*t0;x1=cx+sign*hx*t1
    z0=eave+rise*(1-t0)+.15+jitter;z1=eave+rise*(1-t1)+.12+jitter
    v=[(x0,y0,z0),(x1,y0,z1),(x1,y1,z1),(x0,y1,z0)]
    v += [(x,y,z-.17) for x,y,z in v]
    mesh('Overlapping roof tile',v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],color+'_light' if (j+r)%4==0 else color)
  for y in [-hy-.05,hy+.05]:
   timber('Bargeboard',(cx,cy+y,eave+rise+.35),(cx+sign*(hx+.27),cy+y,eave-.06),.43,'beam')
   timber('Upturned roof finial',(cx+sign*(hx+.1),cy+y,eave),(cx+sign*(hx+.4),cy+y,eave+.6),.38,'wood')
  timber('Eave fascia',(cx+sign*hx,cy-hy,eave),(cx+sign*hx,cy+hy,eave),.37,'wood')
 timber('Ridge cap',(cx,cy-hy-.4,eave+rise+.34),(cx,cy+hy+.4,eave+rise+.34),.48,'beam')

def window(x,y,z,side=False,shutters=True):
 before=set(bpy.context.scene.objects)
 box('Window shadow',(0,0,z),(1.7,.16,1.9),'dark',.04)
 box('Honey window',(0,-.09,z),(1.35,.1,1.5),'orange')
 for xx in [-.8,0,.8]:box('Window mullion',(xx,-.18,z),(.13,.2,1.95),'beam')
 for zz in [-.9,.15,.9]:box('Window lintel',(0,-.18,z+zz),(1.8,.22,.15),'beam')
 box('Projecting sill',(0,-.28,z-1.05),(2.25,.6,.18),'wood_light',.04)
 if shutters:
  for sign in [-1,1]:
   box('Open shutter',(sign*1.15,.02,z),(.5,.15,1.8),'wood',.03)
   for zz in [-.55,.55]:box('Shutter hinge',(sign*1.15,-.09,z+zz),(.48,.09,.1),'iron')
 for o in set(bpy.context.scene.objects)-before:
  if side:o.rotation_euler.z=math.pi/2;o.location=Vector((x,y,0))+Vector((-o.location.y,o.location.x,o.location.z))
  else:o.location+=Vector((x,y,0))

def door(x,y,h=3.8):
 box('Door shadow',(x,y,1+h/2),(2.3,.25,h+.22),'dark',.06)
 for i in range(5):box('Vertical door board',(x-1+i*.5,y-.16,1+h/2),(.47,.14,h),'wood_light' if i%3==0 else 'wood',.025)
 for sign in [-1,1]:box('Door jamb',(x+sign*1.3,y-.16,1+h/2),(.28,.4,h+.5),'beam',.03)
 box('Door lintel',(x,y-.18,1+h+.12),(3,.48,.4),'beam',.06)
 for z in [1.6,3.5]:box('Door iron strap',(x,y-.28,z),(2.1,.08,.14),'iron')
 rod('Door handle',(x+.7,y-.29,2.7),(x+.7,y-.48,2.7),.12,'gold',n=8)
 for i in range(2):box('Doorstep',(x,y-.6-i*.55,.66-i*.22),(3.2+i*.3,1,.35),'stone_light',.08)

def chimney(x,y,z,height=3.5):
 for row in range(math.ceil(height/.65)):
  for sign in [-1,1]:box('Chimney course',(x+sign*.4,y,z+row*.65),(.77,1.6,.62),'stone_light' if row%3==0 else 'stone',.055)
 top=z+(math.ceil(height/.65)-1)*.65+.38
 box('Chimney cap',(x,y,top),(2,2,.27),'stone_dark',.06)
 box('Chimney flue',(x,y,top+.15),(1.25,1.25,.05),'dark')

def cottage(kind):
 cfg={'Brown':(8.2,7,5.8,3.2,'brown',0),'Red':(7.4,7,6.2,4.0,'red',-1.35),'Blue':(9.1,7.8,5.8,3.1,'blue',-1.65),'Green':(8,6.6,5.5,2.8,'green',1.25)}
 w,d,e,r,c,dx=cfg[kind];wall_shell(w,d,e);roof(w,d,e,r,c);door(dx,-d/2-.2)
 wx=-2.2 if dx>0 else 2.25
 window(wx,-d/2-.18,3.3,shutters=kind!='Red');window(w/2+.15,.25,3.3,True)
 for s in [-1,1]:timber('Gable diagonal brace',(s*(w/2-.3),-d/2-.08,e-.2),(s*.7,-d/2-.08,e+1.6),.23,'wood')
 chimney(-w*.27,d*.22,e+r-1,2.5)
 lantern_at((dx-1.85,-d/2-.6,3.6),.7)
 if kind=='Red':
  # Tall front loft and projecting lintel rather than a colour swap.
  box('Loft inset',(0,-d/2-.05,e+1.1),(1.15,.12,1.25),'dark')
  for x in [-.58,.58]:box('Loft frame',(x,-d/2-.13,e+1.1),(.14,.18,1.4),'wood')
  timber('Loft beam',(-1,-d/2-.15,e+.4),(1,-d/2-.15,e+.4),.24)
 elif kind=='Blue':
  for x in [dx-1.6,dx+1.6]:box('Porch post',(x,-d/2-2,2.7),(.3,.3,5.4),'beam',.04)
  roof(3.3,2,4.9,1.1,'blue',dx,-d/2-1)
 elif kind=='Green':
  box('Window herb box',(wx,-d/2-.65,2.1),(2.3,.85,.5),'wood',.06)
  for i in range(5):ico('Window herbs',(wx-.8+i*.4,-d/2-.65,2.5),(.35,.3,.4),'leaf_light',1,i)
 else:
  crate(w/2+.9,-d/2+.3,size=1.4);barrel(-w/2-.9,1)

def lean_to(x,y,w,d,z,mat):
 for xx in [x-w/2,x+w/2]:
  box('Canopy support',(xx,y-d/2,z/2),(.4,.4,z),'beam',.04)
  timber('Canopy knee brace',(xx,y-d/2,z-1),(xx+(.7 if xx<x else -.7),y-d/2,z-.2),.26,'wood')
 for j in range(6):
  xx=x-w/2+(j+.5)*w/6
  o=box('Canopy board',(xx,y,z+.35),(w/6-.03,d,.18),mat if j%3 else mat+'_light',.03);o.rotation_euler.x=.18
 timber('Canopy front beam',(x-w/2-.2,y-d/2,z),(x+w/2+.2,y-d/2,z),.35)

def forge():
 # Open workshop front, with an actual recessed hearth and chimney left of the roof.
 w,d,e=9,7,6.2;foundation(10,8)
 box('Rear masonry wall',(0,3.5,3.5),(9,.7,6),'plaster')
 box('Right workshop wall',(4.5,0,3.5),(.65,7,6),'plaster')
 for x in [-4.5,4.5]:
  for y in [-3.5,3.5]:box('Workshop post',(x,y,3.4),(.6,.6,6.8),'beam',.04)
 timber('Workshop front lintel',(-4.7,-3.6,6.2),(4.7,-3.6,6.2),.6)
 roof(w,d,e,3.1,'blue')
 for j in range(6):box('Workshop paving floor',(0,-2.9+j*1.1,.72),(8.5,1.06,.18),'stone_dark',.025)
 box('Workshop entrance step',(0,-4.15,.34),(8.7,1,.4),'stone_light',.06)
 # Dark slate roof, coloured independently from the trader's blue fabric.
 for o in bpy.context.scene.objects:
  if 'roof tile' in o.name:o.data.materials.clear();o.data.materials.append(M['stone_dark'] if random.random()<.7 else M['stone'])
 for x in [-2.4,2.4]:
  for z in [1.2,2,2.8]:box('Hearth pier',(x,-.4,z),(1.15,2.5,.75),'stone',.07)
 box('Hearth rear', (0,.8,2.6),(4.5,.65,3.8),'stone_dark',.1)
 arch('Furnace arch',(0,-1.15,2.85),1.8,2.6,1.4,count=9)
 box('Hearth lip',(0,-1.8,.85),(5.8,1,.4),'stone_light',.07)
 box('Glowing coal bed',(0,-.4,1.05),(3.5,1.8,.18),'orange',.05)
 for i in range(7):
  x=-1.35+i*.45;ico('Ember',(x,-.5,1.3),(.25,.35,.2),'orange',1,i)
  rod('Stylized flame',(x,-.3,1.3),(x+.1,-.3,2.2+(.5 if i%2 else 0)),.3,'orange',0,5)
 chimney(-3,1.4,6.2,6.5)
 lean_to(-6.5,0,3.1,6,4.8,'red')
 for j in range(7):rod('Stacked firewood',(-6.4+(j%3)*.45,-2.5,.45+(j//3)*.5),(-6.4+(j%3)*.45,-.7,.45+(j//3)*.5),.24,'wood_light',n=7)
 rod('Anvil stump',(2.4,-4.5,0),(2.4,-4.5,1.4),.85,'wood',.7,9)
 box('Anvil foot',(2.4,-4.5,1.6),(1.3,.8,.35),'iron',.06)
 box('Anvil waist',(2.4,-4.5,1.95),(.75,.65,.5),'iron',.06)
 box('Anvil face',(2.4,-4.5,2.3),(1.7,.85,.3),'stone_dark',.06)
 rod('Anvil horn',(1.6,-4.5,2.3),(.7,-4.5,2.3),.32,'iron',.05,6)
 timber('Hammer handle',(3,-4.5,2.5),(3.55,-4.6,3.15),.12,'wood')
 box('Hammer head',(3.55,-4.6,3.15),(.5,.3,.3),'iron',.035)
 crate(5.7,-2,size=1.7);barrel(5.7,.5)
 lantern_at((4.5,-3.9,4.8),.9)
 for i in range(3):timber('Tool handle',(4.9,1+i*.65,1.3),(4.9,1+i*.65,3.5),.13,'wood_light');box('Tool head',(4.9,1+i*.65,3.5),(.2,.6,.25),'iron')

def bottle(x,y,z,color='potion',s=1):
 tube('Potion bottle',[(x,y,z),(x,y,z+.15*s),(x,y,z+.65*s),(x,y,z+.82*s),(x,y,z+1.1*s)],[.21*s,.3*s,.3*s,.12*s,.12*s],color,8)
 rod('Bottle cork',(x,y,z+1.1*s),(x,y,z+1.22*s),.13*s,'wood',n=8)

def alchemist():
 wall_shell(7.5,6.8,5.8);roof(7.5,6.8,5.8,3.5,'purple');door(1.3,-3.6);window(-2.25,-3.6,3.4);window(3.9,.6,3.3,True)
 lean_to(-5.3,-.4,3.5,6,4.7,'purple')
 box('Apothecary counter',(-5.3,-2.7,1.8),(3.5,1.1,.3),'wood_light',.04)
 for x in [-6.7,-3.9]:box('Counter leg',(x,-2.7,.9),(.25,.4,1.8),'beam')
 for i in range(5):bottle(-6.5+i*.55,-2.7,1.95,['potion','cyan','pink'][i%3],.6+i%2*.2)
 x,y=-2,-5.4
 tube('Cauldron bowl',[(x,y,.4),(x,y,.8),(x,y,1.5),(x,y,2.1)],[.9,1.4,1.55,1.28],'iron',12)
 ring('Thick cauldron rim',(x,y,2.05),1.45,1.15,.28,'stone_dark',12)
 rod('Green potion surface',(x,y,2.1),(x,y,2.15),1.16,'potion',n=12)
 for xx in [-1.1,1.1]:rod('Cauldron foot',(x+xx,y,.15),(x+xx*.8,y,.65),.16,'iron',n=6)
 for dx,dz,s in [(-.5,2.6,.2),(.35,3.1,.32),(-.15,3.7,.18)]:ico('Floating potion bubble',(x+dx,y,dz),(s,s,s),'potion',1)
 for dx in [-1.65,1.65]:
  o=ring('Cauldron handle',(0,0,0),.35,.23,.14,'iron',8);o.rotation_euler.x=math.pi/2;o.location=(x+dx,y,1.65)
 crate(4.9,-3,size=1.4,goods=1);barrel(4.8,0)
 lantern_at((3.4,-4,4.1),.8);bottle(-6.3,.6,.1,'cyan',1.3)

def fabric_roof(x,y,w,d,z,color='blue'):
 # Curved canopy cross-section; front edge has scalloped fabric instead of rigid roof tiles.
 for i in range(8):
  x0=x-w/2+i*w/8;x1=x-w/2+(i+1)*w/8
  sections=[(y+d/2,z+.55),(y+d*.15,z+.28),(y-d*.15,z-.05),(y-d/2,z-.2)]
  verts=[(xx,yy,zz) for yy,zz in sections for xx in [x0,x1]]
  mesh('Striped canvas',verts,[(0,1,3,2),(2,3,5,4),(4,5,7,6)],color if i%2==0 else color+'_light')
  mesh('Canvas scallop',[(x0,y-d/2,z-.2),(x1,y-d/2,z-.2),(x1-.08,y-d/2-.02,z-.62),((x0+x1)/2,y-d/2-.04,z-.73),(x0+.08,y-d/2-.02,z-.62)],[(0,1,2,3,4)],color if i%2==0 else color+'_light')

def market(keeper=False):
 w=9;d=5
 foundation(9,5)
 for j in range(7):box('Market floorboard',(0,-2.1+j*.7,.72),(8.7,.67,.16),'wood',.02)
 for x in [-4.2,4.2]:
  for y in [-2.4,2.4]:
   box('Market post',(x,y,3.35),(.5,.5,6.7),'beam',.04)
   timber('Knee brace',(x,y,5.3),(x+(.85 if x<0 else -.85),y,6.1),.3,'wood')
 for y in [-2.4,2.4]:timber('Market lintel',(-4.6,y,6.4),(4.6,y,6.4),.48)
 for x in [-4.2,4.2]:timber('Market side rail',(x,-2.7,6.3),(x,2.8,6.7),.42)
 for i in range(12):box('Back planks',(-4+i*.72,2.4,2.8),(.67,.16,4.3),'wood_light' if i%3==0 else 'wood',.025)
 if keeper:
  roof(9,4,6.5,1.7,'purple',0,1.3)
  fabric_roof(0,-2.2,8,3.2,5.7,'cream')
 else:fabric_roof(0,0,9.7,6.6,6.8,'blue')
 for x in [-3.9,3.9]:box('Counter support',(x,-2.8,1.2),(.45,.6,2.4),'beam')
 box('Merchant countertop',(0,-2.8,2.4),(8.6,1.6,.3),'wood_light',.06)
 for i in range(12):box('Counter face plank',(-3.9+i*.71,-3.45,1.3),(.65,.15,1.9),'wood',.025)
 for z in [.45,2.1]:box('Counter frame',(0,-3.55,z),(8.7,.2,.16),'beam')
 if keeper:
  for i in range(3):
   x=-2.8+i*2.8;box('Pet display plinth',(x,-2.75,2.65),(1.65,1.4,.2),'wood_light',.04)
   ico('Pet display body',(x,-2.75,3.15),(.5,.44,.5),['fur','blue_light','pink'][i],1,i)
   ico('Pet display head',(x,-2.9,3.75),(.72,.58,.65),['fur','blue_light','pink'][i],2,i)
   for sign in [-1,1]:
    rod('Pet ear',(x+sign*.4,-2.9,4.1),(x+sign*.5,-2.9,4.55),.2,['fur','blue_light','pink'][i],.04,5)
    ico('Pet eye',(x+sign*.25,-3.43,3.8),(.065,.04,.08),'dark',1)
    ico('Pet foot',(x+sign*.3,-3.05,2.9),(.21,.23,.16),['fur','blue_light','pink'][i],1)
  box('Keeper sign',(3.5,-2.8,6),(1.8,.25,1.3),'wood_light',.08)
  ico('Paw sign pad',(3.5,-2.97,5.85),(.3,.06,.23),'cream',1)
  for xx in [-.35,0,.35]:ico('Paw sign toe',(3.5+xx,-2.97,6.25),(.13,.06,.16),'cream',1)
 else:
  for i in range(3):crate(-2.8+i*2.8,-2.7,2.55,1.55,i+1)
  for z in [2.5,4.2]:box('Stock shelf',(0,1.85,z),(8,1,.2),'wood_light')
  for i in range(6):bottle(-3.3+i*1.3,1.8,4.3,['cyan','potion','orange'][i%3],.55)
  crate(5,-2,0,1.8,1);crate(5.2,.25,0,1.7,2);barrel(-5.2,0)
 lantern_at((-4.3,-2.9,4.7),.8)

def leaf_cluster(p,s,seed=1,pine=False):
 rng=random.Random(seed)
 for i in range(5):
  a=i*math.tau/5;x=p[0]+math.cos(a)*s[0]*.38;y=p[1]+math.sin(a)*s[1]*.38
  ico('Angular foliage crown',(x,y,p[2]+rng.uniform(-.2,.3)),(s[0]*.7,s[1]*.7,s[2]*.85),['leaf','leaf_light','leaf_dark'][i%3],1,seed+i)
 ico('Crown top',(p[0],p[1],p[2]+s[2]*.45),(s[0]*.65,s[1]*.65,s[2]*.75),'leaf_light',1,seed+8)

def broadleaf():
 tube('Bent tree trunk',[(0,0,0),(.25,.1,2),(-.2,0,4),(.65,.2,6.5)],[.85,.65,.55,.2],'wood',7)
 for i in range(5):
  a=i*math.tau/5;p=(math.cos(a)*2.5,math.sin(a)*2.5,6.4+i%2)
  tube('Forked branch',[(0,0,3.6),(.6*math.cos(a),.6*math.sin(a),5),p],[.4,.32,.09],'wood',6)
  leaf_cluster(p,(2.4,2.2,1.8),i+2)
 leaf_cluster((.3,.1,8),(2.7,2.5,1.8),11)

def pine():
 tube('Pine trunk',[(0,0,0),(.1,0,3),(-.12,0,7),(0,0,12)],[.65,.5,.28,.06],'wood',7)
 for tier in range(4):
  z=3+tier*2.25;r=3.5-tier*.7;n=9
  # Jagged outline, sloping broad facets, asymmetric tier tips.
  v=[]
  for j in range(n*2):
   a=j*math.tau/(n*2);rr=r*(1 if j%2==0 else .68)
   v.append((math.cos(a)*rr,math.sin(a)*rr,z+(0 if j%2==0 else .45)))
  v.append((.15*(-1)**tier,0,z+4.2));v.append((0,0,z+.6))
  f=[(j,(j+1)%(n*2),n*2) for j in range(n*2)]+[(j,n*2+1,(j+1)%(n*2)) for j in range(n*2)]
  mesh('Serrated pine tier',v,f,'pine' if tier%2==0 else 'pine_light')

def grass(x,y,z=0,s=1):
 for i in range(3):
  a=i*2.1;dx=math.cos(a)*.45*s;dy=math.sin(a)*.45*s
  mesh('Grass blade',[(x-dy*.22,y+dx*.22,z),(x+dy*.22,y-dx*.22,z),(x+dx,y+dy,z+s*.7)],[(0,1,2)],'grass')

def wayfarer():
 rod('Island earth',(0,0,0),(0,0,.5),6.4,'earth',6.3,20)
 rod('Island grass',(0,0,.5),(0,0,.65),6.25,'grass',6.2,20)
 # Annular stone basin has a hollow centre and inset blue rune segments.
 for i in range(24):
  a=i*math.tau/24;b=a+math.tau/24-.015
  verts=[(r*math.cos(t),r*math.sin(t),z) for z in [.1,.65] for r,t in [(6.6,a),(8.2,a),(8.2,b),(6.6,b)]]
  mesh('Basin wedge',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone_light' if i%3 else 'stone')
  if i%3==0:
   o=box('Basin cyan inlay',(7.35*math.cos(a+.1),7.35*math.sin(a+.1),.68),(.7,.9,.08),'cyan');o.rotation_euler.z=a
 tube('Twisting main trunk',[(0,0,.5),(-.7,.1,2.6),(-.35,-.1,5),(.7,.1,7.1),(.2,.15,10)],[2.1,1.5,1.25,1.0,.6],'wood',9)
 for i in range(7):
  a=i*math.tau/7
  tube('Spreading buttress root',[(math.cos(a)*.5,math.sin(a)*.5,2.8),(math.cos(a)*2.7,math.sin(a)*2.7,.85),(math.cos(a)*5.2,math.sin(a)*5.2,.6)],[.85,.5,.08],'wood',7)
 for i in range(8):
  a=i*math.tau/8;r=5.5 if i%2==0 else 4.4
  p=(r*math.cos(a),r*math.sin(a),10.5+i%3*.8)
  tube('Mature branching bough',[(0,0,5.8),(.9*math.cos(a),.9*math.sin(a),7.6),(3.5*math.cos(a),3.5*math.sin(a),8.7),p],[.8,.75,.45,.12],'wood',7)
  leaf_cluster(p,(3.55,3.2,1.8),i*6+3)
 leaf_cluster((.25,0,13),(4.2,3.8,2.3),77)
 for x,z in [(-.6,4),(.5,6.7),(1,8.7)]:diamond('Trunk rune socket',(x,-1.23,z),(.5,.8),'stone_dark');diamond('Cyan trunk diamond',(x,-1.43,z),(.29,.54))
 for x,z in [(-4.2,8.7),(4.6,9.2)]:
  rod('Hanging rune chain',(x,-1,z),(x,-1,z-2),.035,'gold',n=5);diamond('Suspended rune',(x,-1,z-2.4),(.36,.62))
 for x in [-5.7,5.7]:banner(x,-3.1,8.8,1.6,3.5)
 for i in range(18):
  a=i*math.tau/18;grass(5.6*math.cos(a),5.6*math.sin(a),.65,.9)
  if i%3==0:ico('Root moss',(4.3*math.cos(a),4.3*math.sin(a),.75),(.7,.65,.35),'leaf_light',1,i)

def gate():
 for x in [-8.8,8.8]:
  box('Tower plinth',(x,0,.65),(4.9,4.5,1.3),'stone_dark',.12)
  for j in range(8):
   z=1.4+j*1.55
   box('Tower masonry course',(x,0,z),(3.7,3.6,1.5),'stone',.065)
   # Alternate corner quoins create a bonded tower, not a stacked bare pillar.
   for s in [-1,1]:box('Tower front quoin',(x+s*1.4,-1.86,z),(.85 if j%2 else 1.2,.45,1.4),'stone_light',.045)
  for z in [2.6,10.9,13.6]:box('Tower string course',(x,0,z),(4.2,4.1,.45),'stone_light',.06)
  box('Tower crown',(x,0,14.4),(4.2,4,1.3),'stone',.06)
  for dx in [-1.55,1.55]:box('Crown merlon',(x+dx,-1.55,15.3),(1,1,1.3),'stone_light',.07)
  rod('Blue pyramidal cap',(x,.1,15),(x,.1,17.7),2.7,'blue',0,4)
  rod('Gold finial',(x,.1,17.7),(x,.1,18.4),.12,'gold',.04,6)
  banner(x,-2.15,12.8,2,6.7)
  lantern_at((x,-2.7,4),.9)
 arch('Great portal voussoir',(0,0,10.5),6.85,9.05,3.2,count=13)
 for obj in bpy.context.scene.objects:
  if obj.name.startswith('Great portal voussoir'):
   for v in obj.data.vertices:v.co.z=10.5+(v.co.z-10.5)*.65
 for i in range(4):box('Portal approach step',(0,-3.4-i*1.1,.65-i*.15),(13.7+i*.3,1.2,.3),'stone_light',.055)

def lantern():
 box('Lamp footing',(0,0,.25),(1.1,1.1,.5),'stone',.08)
 timber('Lamp post',(0,0,.45),(-.1,0,6.4),.42,'wood')
 timber('Lamp bracket',(-.2,0,6.05),(1.7,0,6.05),.35,'beam')
 timber('Lamp diagonal brace',(0,0,4.7),(1.4,0,6),.25,'wood')
 rod('Lamp chain',(1.5,0,6),(1.5,0,5.5),.045,'iron',n=6)
 lantern_at((1.5,0,4.6),1)

def fence():
 for x in [-3.5,3.5]:
  box('Fence post',(x,0,1.65),(.55,.6,3.3),'wood',.05)
  box('Post cap',(x,0,3.35),(.7,.75,.2),'wood_light',.04)
  for z in [1.1,2.5]:box('Iron nail',(x,-.34,z),(.1,.07,.1),'iron')
 for z in [1,2.35]:timber('Uneven fence rail',(-3.8,-.12,z),(3.8,-.12,z+.12),.3,'wood_light',.22)

def paving():
 rng=random.Random(23)
 for row in range(4):
  for col in range(4):
   x=(col-1.5)*2.1+(row%2)*.65;y=(row-1.5)*1.7;c=rng.uniform(.1,.22)
   pts=[(x-1+c,y-.79),(x+1-c,y-.79),(x+1,y-.79+c),(x+1,y+.79-c),(x+1-c,y+.79),(x-1+c,y+.79),(x-1,y+.79-c),(x-1,y-.79+c)]
   verts=[(xx,yy,z) for z in [0,.24] for xx,yy in pts]
   mesh('Hand-cut flagstone',verts,[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)],'path_light' if (row+col)%3==0 else 'path')

def bridge():
 for x in [-2.8,2.8]:timber('Under-deck stringer',(x,-8,.5),(x,8,.5),.55,'beam')
 for j in range(17):
  y=-8+j;z=1+.3*(1-(y/8)**2)
  o=box('Individual bridge plank',(random.uniform(-.12,.12),y,z),(6.9,.91,.3),'wood_light' if j%4==0 else 'wood',.045);o.rotation_euler.z=random.uniform(-.025,.025)
 for x in [-3.2,3.2]:
  for y in [-8,-3,3,8]:
   box('Bridge pile',(x,y,1.5),(.55,.6,4.5),'beam',.06)
   box('Pile cap',(x,y,3.8),(.75,.8,.22),'wood_light',.04)
  for z in [2.25,3.35]:
   for a,b in [(-8,-3),(-3,3),(3,8)]:timber('Bridge railing',(x,a,z),(x,b,z),.23,'wood')
  timber('Bridge structural brace',(x,-7,-.5),(x,0,.7),.4,'beam')
  timber('Bridge structural brace',(x,7,-.5),(x,0,.7),.4,'beam')

def rock(seed):
 rng=random.Random(seed*56)
 for k in range(4):
  x=(k%2)*3-1.7;y=(k//2)*2.5-1.3;h=rng.uniform(3.5,7);w=rng.uniform(1.7,2.4);d=rng.uniform(1.5,2.2)
  # Chamfered rectangular geological columns, slanted planar sides and stepped ledges.
  poly=[(-w*.7,-d), (w*.65,-d),(w,-d*.55),(w,d*.6),(w*.65,d),(-w*.7,d),(-w,d*.5),(-w,-d*.65)]
  verts=[]
  for z,scale,ox in [(0,1.12,0),(h*.7,1, rng.uniform(-.3,.3)),(h,.83,rng.uniform(-.5,.5))]:
   verts += [(x+px*scale+ox,y+py*scale,z) for px,py in poly]
  faces=[tuple(reversed(range(8))),tuple(range(16,24))]
  for row in range(2):faces += [(row*8+i,row*8+(i+1)%8,(row+1)*8+(i+1)%8,(row+1)*8+i) for i in range(8)]
  mesh('Faceted cliff column',verts,faces,'stone' if k%2 else 'stone_dark')
  if k%2==0:
   mesh('Grassy cliff cap',[(xx,yy,zz+.03) for xx,yy,zz in verts[16:]], [tuple(range(8))],'grass')
   grass(x,y,h+.1,1)

def save(name):
 target=ROOT/name;target.mkdir(exist_ok=True)
 scene=bpy.context.scene;meshes=[o for o in scene.objects if o.type=='MESH']
 # Consistent outward normals, flat faces, applied modifier geometry for both outputs.
 for o in meshes:
  bpy.context.view_layer.objects.active=o;o.select_set(True)
  for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  o.select_set(False)
 bpy.context.view_layer.update()
 bounds=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
 lo=Vector([min(v[i] for v in bounds) for i in range(3)]);hi=Vector([max(v[i] for v in bounds) for i in range(3)])
 scene['reference']='Концепт фэнтезийного хаба с воротами.png';scene['asset_version']='V2 independent reconstruction'
 scene['units']='One Blender unit = one intended Roblox stud; Z up, front -Y. Verify import scale in Studio.'
 scene['integration']='Not placed in Roblox. Static environment assets, no rig required.'
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(target/(name+'.glb')),export_format='GLB',use_selection=True)
 center=(lo+hi)/2;extent=max(hi-lo)
 bpy.ops.object.camera_add(location=center+Vector((1.05,-1.65,1.1))*extent)
 cam=bpy.context.object;cam.name='Preview camera';cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=extent*1.44;scene.camera=cam
 for pos,power,size in [((-1,-2,3),850,1.3),((2,-1,1.8),450,1.7),((0,2,2.5),600,1.3)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(pos)*extent*.65);o=bpy.context.object;o.data.energy=power*(extent/5)**2;o.data.shape='DISK';o.data.size=extent*size
  o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
 scene.world=bpy.data.worlds.new('Neutral soft studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
 scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
 scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
 scene.render.film_transparent=True;scene.render.filepath=str(target/(name+'.png'));scene.view_settings.view_transform='Standard'
 scene.view_settings.look='None';scene.view_settings.exposure=0
 # Open native file in material mode, framed around its mesh, with render helpers hidden in viewport.
 for o in scene.objects:
  if o.type in ['CAMERA','LIGHT']:o.hide_set(True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0]
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    area.spaces.active.region_3d.view_distance=extent*1.65;area.spaces.active.region_3d.view_location=center
    area.spaces.active.shading.type='MATERIAL'
 bpy.ops.wm.save_as_mainfile(filepath=str(target/(name+'.blend')))
 bpy.ops.render.render(write_still=True)
 triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
 return {'name':name,'blend':name+'/'+name+'.blend','mesh_objects':len(meshes),'triangles':triangles,'size':[round(v,3) for v in hi-lo]}

# Cream alternation is the pet keeper's canvas, not a palette variant of the creature.
COLORS['cream_light']='F2DDB0'
jobs=[('WayfarerTree',wayfarer),('BiomeGate',gate),('Pine',pine),('BroadleafTree',broadleaf),('Lantern',lantern),('Fence',fence),('Paving',paving),('Bridge',bridge)]
jobs += [('RockCluster'+str(i),lambda i=i:rock(i)) for i in range(1,4)]
jobs += [('House'+k,lambda k=k:cottage(k)) for k in ['Brown','Red','Blue','Green']]
jobs += [('Forge',forge),('Alchemist',alchemist),('PetKeeper',lambda:market(True)),('ResourceStall',market)]
only=sys.argv[sys.argv.index('--only')+1].split(',') if '--only' in sys.argv else None
if only:jobs=[job for job in jobs if job[0] in only]
if not jobs:raise ValueError('No matching asset names')
if (ROOT/'verification.json').exists():(ROOT/'verification.json').unlink()
results=[]
for name,build in jobs:
 reset();build();results.append(save(name));print('ASSET_DONE',name,flush=True)
if only and (ROOT/'manifest.json').exists():
 previous=json.loads((ROOT/'manifest.json').read_text());results=[r for r in previous if r['name'] not in only]+results
(ROOT/'manifest.json').write_text(json.dumps(results,indent=2))
print('ENVIRONMENT_V2_READY',len(results),flush=True)
