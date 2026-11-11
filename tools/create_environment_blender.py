"""Editable low-poly environment kit reconstructed from the hub reference PNG.
Blender background script. Z up, front -Y, dimensions in Roblox studs.
Does not place assets in the gameplay hub or overwrite other modelling work.
"""
import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]/'assets'/'meshes'/'Environment'
ROOT.mkdir(parents=True,exist_ok=True)
COLORS={'wood':(.27,.14,.06,1),'timber':(.43,.25,.11,1),'plaster':(.72,.57,.35,1),'stone':(.32,.39,.43,1),
 'stone_light':(.46,.51,.52,1),'roof_brown':(.32,.22,.15,1),'roof_red':(.57,.22,.14,1),'roof_blue':(.18,.33,.51,1),
 'roof_green':(.25,.37,.22,1),'roof_purple':(.37,.22,.43,1),'leaf':(.28,.44,.14,1),'leaf_light':(.40,.55,.20,1),
 'pine':(.12,.32,.22,1),'gold':(.76,.51,.16,1),'blue':(.10,.34,.57,1),'rune':(.10,.66,.90,1),
 'glass':(1,.62,.17,1),'dark':(.08,.09,.09,1),'ground':(.37,.47,.24,1),'water':(.13,.46,.57,1)}
def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 global mats;mats={}
 for name,color in COLORS.items():
  m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=.88
  if name in ['rune','glass']:
   p.inputs['Emission Color'].default_value=color;p.inputs['Emission Strength'].default_value=.6
  mats[name]=m
def finish(obj,name,mat):obj.name=name;obj.data.materials.append(mats[mat]);return obj
def box(name,pos,size,mat,angle=0,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.dimensions=size;o.rotation_euler.z=angle
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft worn edges','BEVEL');mod.width=bevel;mod.segments=1
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,name,mat)
def cone(name,pos,r1,r2,depth,mat,sides=8):
 bpy.ops.mesh.primitive_cone_add(vertices=sides,radius1=r1,radius2=r2,depth=depth,location=pos)
 return finish(bpy.context.object,name,mat)
def blob(name,pos,size,mat,seed=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=pos);o=bpy.context.object
 rng=random.Random(seed)
 for v in o.data.vertices:v.co*=rng.uniform(.9,1.1)
 o.scale=size;return finish(o,name,mat)
def beam(name,a,b,width,mat):
 d=Vector(b)-Vector(a);o=box(name,(Vector(a)+Vector(b))/2,(width,width,d.length),mat)
 o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def mesh(name,verts,faces,mat):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);return finish(o,name,mat)
def roof(width,depth,z,mat):
 # Gable faces along the front and rear, shingled surfaces across both slopes.
 half=width/2+.7;rise=width*.4
 mesh('Gable', [(-half,-depth/2,z),(half,-depth/2,z),(0,-depth/2,z+rise),(-half,depth/2,z),(half,depth/2,z),(0,depth/2,z+rise)],[(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)],'timber')
 for sign in [-1,1]:
  for row in range(5):
   x=sign*half*(row+.5)/5;zz=z+rise*(1-abs(x)/half)
   for j in range(6):
    o=box('RoofShingle',(x,-depth/2+(j+.5)*depth/6,zz+.12),(half/5+.1,depth/6+.08,.22),mat,bevel=.035)
    o.rotation_euler.y=sign*math.atan(rise/half)
  for y in [-depth/2-.12,depth/2+.12]:beam('GableTrim',(0,y,z+rise+.35),(sign*(half+.2),y,z-.12),.36,'wood')
 beam('Ridge',(0,-depth/2-.4,z+rise+.25),(0,depth/2+.4,z+rise+.25),.42,'wood')
def window(x,y,z):
 box('WindowRecess',(x,y,z),(1.5,.15,1.65),'dark',bevel=.08)
 box('WarmWindow',(x,y-.09,z),(1.2,.08,1.35),'glass')
 for dx in [-.77,0,.77]:box('WindowFrame',(x+dx,y-.16,z),(.13,.16,1.8),'wood')
 for dz in [-.9,0,.9]:box('WindowFrame',(x,y-.16,z+dz),(1.7,.16,.13),'wood')
def house(roofmat='roof_brown',kind='house'):
 w,d=9,8
 box('StoneFoundation',(0,0,.45),(10,9,.9),'stone',bevel=.18)
 box('PlasterWalls',(0,0,3.6),(w,d,6.3),'plaster',bevel=.08)
 for x in [-4.5,0,4.5]:box('FrontTimber',(x,-4.06,3.6),(.35,.28,6.4),'wood')
 for y in [-4,4]:
  for x in [-4.5,4.5]:box('CornerPost',(x,y,3.8),(.48,.48,6.7),'wood')
 for z in [1.1,6.5]:box('CrossTimber',(0,-4.13,z),(9.4,.3,.32),'wood')
 box('DoorFrame',(0,-4.25,2.65),(2.7,.3,4.3),'wood',bevel=.1)
 for i in range(5):box('DoorPlank',(-1+i*.5,-4.45,2.6),(.47,.18,3.8),'timber')
 blob('DoorHandle',(.74,-4.6,2.5),(.09,.06,.09),'gold')
 for x in [-2.9,2.9]:window(x,-4.25,3.8)
 for i in range(2):box('EntryStep',(0,-4.9-i*.65,.55-i*.18),(3.4,.8,.28),'stone_light',bevel=.08)
 roof(w,9.3,6.7,roofmat)
 # Stone chimney with discrete blocks, capped and without animated smoke.
 for i in range(5):box('ChimneyBlock',(2.6,2.1,7+i*.65),(1.35,1.3,.63),'stone_light',bevel=.08)
 box('ChimneyCap',(2.6,2.1,10.1),(1.7,1.65,.3),'stone')
 if kind=='forge':
  box('Forge',(5.4,-.5,1.7),(3,3,3.4),'stone',bevel=.2);box('FurnaceOpening',(5.4,-2.05,1.6),(1.9,.1,1.7),'dark');blob('Embers',(5.4,-2.15,1.1),(.7,.12,.35),'glass')
  cone('AnvilBase',(4.8,-4.8,.75),.8,.5,1.5,'wood');box('Anvil',(4.8,-4.8,1.75),(2,.9,.5),'dark',bevel=.1)
 if kind=='alchemist':
  cone('Cauldron',(5.5,-3,1.25),1.25,1.6,2,'dark',12);cone('PotionSurface',(5.5,-3,2.28),1.4,1.4,.05,'rune',12)
  for i in range(3):cone('Bottle',(-4.3+i*.6,-5.3,1.3),.2,.12,.7,'rune',8)
 if kind=='keeper':
  stall('roof_green',offset=(0,-7,0))
  for x in [-3,3]:box('PetCrate',(x,-6,1),(1.8,1.8,2),'timber',bevel=.08)
def stall(mat='roof_blue',offset=(0,0,0)):
 x,y,z=offset
 for dx in [-3,3]:box('AwningPost',(x+dx,y,z+2.8),(.35,.35,5.6),'wood')
 box('Counter',(x,y,z+1.6),(6.4,2.2,.3),'timber',bevel=.06)
 for i in range(8):
  o=box('AwningStripe',(x-2.8+i*.8,y,z+5.3),(.8,3.5,.12),mat if i%2==0 else 'plaster');o.rotation_euler.x=.15
 for i in range(3):box('GoodsCrate',(x-2+i*2,y,z+.7),(1.6,1.6,1.2),'timber',bevel=.06)
def lantern():
 box('Post',(0,0,3),(.45,.45,6),'wood');beam('Bracket',(0,0,5.8),(1.5,0,5.8),.3,'wood')
 box('Glass',(1.35,0,4.9),(.65,.65,1.05),'glass')
 for x in [1,1.7]:
  for y in [-.35,.35]:box('Cage',(x,y,4.9),(.1,.1,1.2),'dark')
 cone('LanternRoof',(1.35,0,5.6),.7,.15,.5,'dark',4);box('LanternBase',(1.35,0,4.3),(.9,.9,.15),'dark')
def fence():
 for x in [-3,3]:box('Post',(x,0,1.7),(.55,.55,3.4),'wood',bevel=.05)
 for z in [1,2.25]:box('Rail',(0,0,z),(6.4,.27,.32),'timber')
def paving():
 rng=random.Random(3)
 for x in range(3):
  for y in range(3):cone('PavingStone',((x-1)*1.8+(y%2)*.4,(y-1)*1.65,.15),1.04,1,.3,'stone_light' if (x+y)%3 else 'stone',rng.choice([5,6]))
def pine():
 cone('Trunk',(0,0,4),.55,.28,8,'wood')
 for i in range(4):cone('NeedleTier',(0,0,5+i*2.3),3.6-i*.7,.05,5,'pine',7)
def broadleaf():
 cone('Trunk',(0,0,4),1,.5,8,'timber')
 for i in range(6):
  a=i*math.tau/6;pos=(math.cos(a)*2.8,math.sin(a)*2.8,8.5+i%2)
  beam('Branch',(0,0,5),pos,.55,'wood');blob('LeafCrown',pos,(3.2,2.8,2.6),'leaf_light' if i%2 else 'leaf',i)
 blob('TopCrown',(0,0,10.8),(3.4,3.3,2.7),'leaf_light',4)
def wayfarer():
 cone('TreeIsland',(0,0,.3),6.8,6.5,.6,'ground',16)
 cone('Trunk',(0,0,5.7),2.25,1.1,11,'timber',9)
 for i in range(8):
  a=i*math.tau/8
  beam('Root',(math.cos(a)*5,math.sin(a)*5,.6),(0,0,3),.8,'wood')
  tip=(math.cos(a)*5,math.sin(a)*5,12+i%3)
  beam('Branch',(0,0,7),tip,1.05,'timber');blob('Crown',tip,(4.5,4.3,3.1),'leaf_light' if i%3==0 else 'leaf',i)
  p=(math.cos(a)*2.05,math.sin(a)*2.05,5+i%3)
  o=cone('BlueRune',p,.36,0,1.2,'rune',4);o.rotation_euler.y=.25
 blob('TopCrown',(0,0,15),(5,5,3.4),'leaf_light',10)
 for i in range(16):
  a=i*math.tau/16;cone('IslandRim',(math.cos(a)*7.8,math.sin(a)*7.8,.3),.9,.85,.6,'stone',6)
def gate():
 for x in [-10,10]:
  box('Footing',(x,0,1),(5,5,2),'stone',bevel=.2)
  for j in range(6):box('PillarBlock',(x,0,3+j*2.4),(3.5,3.6,2.3),'stone_light' if j%2 else 'stone',bevel=.14)
  cone('PillarRoof',(x,0,18),3.2,0,3.5,'roof_blue',4)
  box('Banner',(x,-2,10),(2.3,.1,7),'blue')
  for dx in [-.9,.9]:box('BannerGold',(x+dx,-2.1,10),(.16,.08,6.7),'gold')
  box('BannerRod',(x,-2.15,13.8),(3,.2,.2),'gold')
 for i in range(12):
  a,b=i*math.pi/12,(i+1)*math.pi/12
  verts=[(r*math.cos(t),y,14+r*math.sin(t)) for y in [-1.9,1.9] for r,t in [(7.4,a),(10.6,a),(10.6,b),(7.4,b)]]
  mesh('ArchVoussoir',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone_light' if i%3==0 else 'stone')
 for j in range(4):box('Step',(0,-3-j*1.3,.2+j*.18),(16,1.5,.35),'stone_light',bevel=.06)
def rock(seed=1):
 rng=random.Random(seed)
 for i in range(4):blob('RockMass',(rng.uniform(-2,2),rng.uniform(-1.5,1.5),1.5+i*.8),(2.6-i*.25,2.2,2.5),'stone' if i%2 else 'stone_light',seed+i)
def bridge():
 for i in range(15):box('DeckPlank',(0,-7+i,1),(6,.88,.3),'timber',bevel=.04)
 for x in [-3,3]:
  for y in [-7,-2,3,7]:box('Post',(x,y,1.8),(.4,.4,3.6),'wood')
  for z in [2,3]:beam('Handrail',(x,-7,z),(x,7,z),.25,'wood')
def save(name):
 target=ROOT/name;target.mkdir(exist_ok=True)
 scene=bpy.context.scene;objects=[o for o in scene.objects if o.type=='MESH']
 for o in objects:
  assert all(math.isfinite(v) for v in o.matrix_world.translation)
  for poly in o.data.polygons:poly.use_smooth=False
 scene['reference']='Desktop/ideas/Концепт фэнтезийного хаба с воротами.png'
 scene['status']='Editable reference reconstruction; not yet imported or placed in Roblox'
 scene['units']='Z up; front -Y; one unit per Roblox stud'
 bpy.ops.object.select_all(action='SELECT')
 bpy.ops.export_scene.gltf(filepath=str(target/(name+'.glb')),export_format='GLB',use_selection=True)
 bounds=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
 mn=Vector(tuple(min(p[i] for p in bounds) for i in range(3)));mx=Vector(tuple(max(p[i] for p in bounds) for i in range(3)))
 center=(mn+mx)/2;extent=max(mx-mn)
 bpy.ops.object.camera_add(location=center+Vector((1,-1.6,1.1))*extent)
 cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=extent*1.55;scene.camera=cam
 for loc,power in [((1,-2,3),500),((-2,-1,1),200)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(loc)*extent*.6);l=bpy.context.object;l.data.energy=power*(extent/5)**2;l.data.size=extent
  l.rotation_euler=(center-l.location).to_track_quat('-Z','Y').to_euler()
 scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
 scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
 scene.render.film_transparent=True;scene.render.filepath=str(target/(name+'.png'))
 scene.view_settings.view_transform='Standard'
 bpy.ops.wm.save_as_mainfile(filepath=str(target/(name+'.blend')));bpy.ops.render.render(write_still=True)
 return {'name':name,'mesh_objects':len(objects),'size':[round(v,2) for v in mx-mn],'blend':name+'/'+name+'.blend'}
jobs=[('WayfarerTree',wayfarer),('BiomeGate',gate),('Pine',pine),('BroadleafTree',broadleaf),('Lantern',lantern),('Fence',fence),('Paving',paving),('Bridge',bridge)]
for i in range(3):jobs.append(('RockCluster'+str(i+1),lambda i=i:rock(i+1)))
for suffix,mat in [('Brown','roof_brown'),('Red','roof_red'),('Blue','roof_blue'),('Green','roof_green')]:jobs.append(('House'+suffix,lambda mat=mat:house(mat)))
jobs += [('Forge',lambda:house('roof_brown','forge')),('Alchemist',lambda:house('roof_purple','alchemist')),('PetKeeper',lambda:house('roof_brown','keeper')),('ResourceStall',stall)]
results=[]
only=sys.argv[sys.argv.index('--only')+1] if '--only' in sys.argv else None
if only:jobs=[job for job in jobs if job[0]==only]
for name,build in jobs:
 reset();build();results.append(save(name));print('ASSET_DONE',name,flush=True)
if only and (ROOT/'manifest.json').exists():
 previous=json.loads((ROOT/'manifest.json').read_text());results=[r for r in previous if r['name']!=only]+results
(ROOT/'manifest.json').write_text(json.dumps(results,indent=2))
print('ENVIRONMENT_KIT_OK',len(results),flush=True)
