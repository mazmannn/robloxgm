"""Hand-composed copper outcrop from the supplied concept sheet. Blender 5.2.
Independent V2 source; preserves V1 and game files. Front -Y, up Z.
"""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]/'assets/meshes/CopperOutcropV2'
ROOT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
M={}
def linear(c):
 c/=255;return c/12.92 if c<.04045 else ((c+.055)/1.055)**2.4
def material(name,h,emission=0):
 c=tuple(linear(int(h[i:i+2],16)) for i in (0,2,4))+(1,)
 m=bpy.data.materials.new(name);m.diffuse_color=c;m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF']
 p.inputs['Base Color'].default_value=c;p.inputs['Roughness'].default_value=1;p.inputs['Specular IOR Level'].default_value=0
 p.inputs['Emission Color'].default_value=c;p.inputs['Emission Strength'].default_value=emission;M[name]=m
for i,h in enumerate(['49494C','505053','555558','5B5A5D','454548','616063','4D4D50']):material('Basalt_'+str(i),h)
for i,h in enumerate(['EB641F','FF842D','FFAB48','DA5017','F57522']):material('Copper_'+str(i),h,.65)
material('Hot edge','FFBF69',1.2);material('Orange fissure','FF892C',2.0)

def mesh(name,verts,faces,mats):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
 for m in mats:d.materials.append(M[m])
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();d.update()
 return o

def stone(name,c,scale,seed,tilt=(0,0)):
 """Octagonal, shoulder-cut rock with flat top; subdivided faces retain broad planes."""
 rng=random.Random(seed);cx,cy,cz=c;sx,sy,sz=scale
 outline=[(-.68,-1),(.52,-1),(1,-.5),(1,.58),(.55,1),(-.62,1),(-1,.5),(-1,-.48)]
 outline=[(x*rng.uniform(.92,1.05),y*rng.uniform(.93,1.05)) for x,y in outline]
 verts=[]
 for r,z in [( .81,0),(1,.28),(.91,.72),(.62,1)]:
  for j,(x,y) in enumerate(outline):
   zz=z*sz+(rng.uniform(-.035,.035)*sz if z not in (0,1) else 0)
   verts.append((cx+x*r*sx+tilt[0]*z,cy+y*r*sy+tilt[1]*z,cz+zz+(x*.05+y*.035)*sz*z))
 faces=[tuple(reversed(range(8)))]
 # Triangular patches are low-contrast flat materials rather than noisy textures.
 for row in range(3):
  for j in range(8):
   ids=[row*8+j,row*8+(j+1)%8,(row+1)*8+(j+1)%8,(row+1)*8+j]
   p=sum((Vector(verts[k]) for k in ids),Vector())/4
   center=len(verts);verts.append(tuple(p))
   for k in range(4):faces.append((ids[k],ids[(k+1)%4],center))
 # Off-centre top facet, four broad patches.
 top=len(verts);verts.append(tuple(sum((Vector(v) for v in verts[24:32]),Vector())/8+Vector((.03,0,.015))))
 for j in range(8):faces.append((24+j,24+(j+1)%8,top))
 o=mesh(name,verts,faces,['Basalt_'+str(i) for i in range(7)])
 for p in o.data.polygons:
  # Distribution deliberately stays dark; occasional muted lighter planar patch.
  p.material_index=rng.choices(range(7),[26,24,17,8,13,3,9])[0]
 return o

def vein(name,points,width=.025,mat='Orange fissure'):
 verts=[];sides=5
 for j,p in enumerate(points):
  d=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])
  q=d.to_track_quat('Z','Y');r=width*(.35 if j in (0,len(points)-1) else 1)
  for i in range(sides):a=i*math.tau/sides;verts.append(Vector(p)+q@Vector((r*math.cos(a),r*math.sin(a),0)))
 faces=[tuple(reversed(range(sides)))]
 for j in range(len(points)-1):
  for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;faces.append((a,b,b+sides,a+sides))
 faces.append(tuple(range((len(points)-1)*sides,len(points)*sides)))
 return mesh(name,verts,faces,[mat])

def copper(name,c,s,seed,lean=0):
 # Broad embedded angular nugget: irregular bevel corners, slanted cap, no spherical lumps.
 rng=random.Random(seed);cx,cy,cz=c;sx,sy,sz=s
 poly=[(-.65,-1),(.45,-1),(1,-.45),(.8,.7),(-.4,1),(-1,.35)]
 verts=[]
 for z,r in [(0,.7),(.24,1),(.78,.9),(1,.55)]:
  for x,y in poly:verts.append((cx+x*sx*r+lean*z,cy+y*sy*r,cz+sz*z+x*.13*sz))
 faces=[tuple(reversed(range(6)))]
 for row in range(3):
  for j in range(6):
   a=row*6+j;b=row*6+(j+1)%6;c=b+6;d=a+6
   if (j+row)%2:faces.extend([(a,b,d),(b,c,d)])
   else:faces.append((a,b,c,d))
 faces += [(18,19,20),(18,20,23),(20,21,23),(21,22,23)]
 o=mesh(name,verts,faces,['Copper_'+str(i) for i in range(5)])
 for p in o.data.polygons:p.material_index=rng.choices(range(5),[20,35,15,8,22])[0]
 # A sparse connected set of bright facet edges: not a uniform wireframe.
 for a,b in [(6,12),(12,18),(18,19),(19,20),(20,14),(12,19),(7,12),(7,14),(14,8)]:
  va=Vector(verts[a]);vb=Vector(verts[b]);va.y-=.012;vb.y-=.012
  vein(name+' / lit facet',[va,(va+vb)/2,vb],.007,'Hot edge')
 return o

# Macro composition matches the concept's tall left shoulder and large front-right slab.
stone('01 Tall rear-left basalt',(-.63,.27,.1),(1.03,.87,4.12),12,(-.17,.08))
stone('02 Main front-right basalt',(.75,-.15,.05),(1.05,.95,3.05),29,(-.13,.08))
stone('03 Left buttress',(-1.67,-.04,.02),(.57,.75,2.12),43,(-.05,.12))
stone('04 Far right support',(1.68,.05,.02),(.49,.68,1.95),45,(-.07,.13))
stone('05 Front-left footing',(-1.02,-.86,.01),(.75,.54,1.02),51)
stone('06 Front-middle footing',(.1,-.98,0),(.61,.4,.68),57)
stone('07 Right toe',(1.35,-.78,0),(.55,.48,.65),63)
stone('08 Left toe',(-1.93,-.65,0),(.38,.46,1.35),71)
stone('09 Back shoulder',(.65,.69,.02),(.85,.55,2.95),75)
stone('10 Back footing',(-.55,1.05,0),(1,.42,1.4),88)

copper('Copper / main left pocket',(-1.02,-.81,1.0),(.59,.48,1.22),22,.06)
copper('Copper / upper tooth',(.43,.12,3.02),(.37,.36,1.03),32,-.19)
copper('Copper / right pocket',(1.67,-.51,.65),(.33,.37,.92),40,.03)
copper('Copper / small left chip',(-1.62,-.98,.96),(.21,.19,.45),44,.06)
copper('Copper / lower wedge',(-.12,-1.1,.66),(.27,.21,.43),48,-.07)
copper('Copper / lower right chip',(1.03,-.91,.38),(.25,.24,.45),52,.06)
copper('Copper / top chips',(.92,.15,2.91),(.23,.23,.35),56,-.05)
copper('Copper / rear pocket',(-.38,1.15,1.4),(.37,.23,.7),60)

# Fractures follow boundaries and disappear under stones; rear seams complete the 3D object.
paths=[
 [(-1.58,-.53,2.6),(-1.52,-.74,2.28),(-1.4,-.92,2.02),(-1.32,-1.07,1.83)],
 [(-.65,-.77,2.08),(-.41,-.92,1.77),(-.3,-1.02,1.43),(-.17,-1.13,1.13),(.05,-1.06,.78)],
 [(-1.44,-1.05,1.15),(-1.57,-1.07,.92),(-1.66,-1.03,.65),(-1.7,-.91,.16)],
 [(-.54,-1.15,1.03),(-.36,-1.2,.85),(-.25,-1.18,.55),(-.28,-1.12,.12)],
 [(1.32,-.64,2.1),(1.48,-.79,1.8),(1.42,-.88,1.46),(1.58,-.82,1.17)],
 [(1.35,-.89,.79),(1.2,-1.02,.63),(.99,-1.06,.31),(.87,-.91,.08)],
 [(.16,-.16,3.65),(.26,-.29,3.37),(.42,-.49,3.12),(.68,-.62,3.02),(1.04,-.46,2.99)],
 [(-1.28,.83,1.74),(-.98,1.13,1.61),(-.55,1.32,1.56),(-.27,1.29,1.34),(.13,1.15,.89)],
 [(.92,.94,2.65),(1.26,.91,2.11),(1.42,.76,1.78)]
]
rockverts=[];rockfaces=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.data.materials[0].name.startswith('Basalt'):
  offset=len(rockverts);rockverts.extend([o.matrix_world@v.co for v in o.data.vertices]);rockfaces.extend([tuple(offset+j for j in f.vertices) for f in o.data.polygons])
surface=BVHTree.FromPolygons(rockverts,rockfaces)
for i,p in enumerate(paths):
 projected=[];back=i>=7
 for a,b in zip(p,p[1:]):
  for j in range(9):
   v=Vector(a).lerp(Vector(b),j/8)
   hit,normal,index,distance=surface.ray_cast(Vector((v.x,5 if back else -5,v.z)),Vector((0,-1 if back else 1,0)))
   if hit is not None:
    q=hit+Vector((0,.012 if back else -.012,0))
    if not projected or (q-projected[-1]).length>.001:projected.append(q)
 if len(projected)>1:vein('Surface fissure %02d'%i,projected,.018)

# Slightly wider mound, matching the concept rather than a tall stack of separate rocks.
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  for v in o.data.vertices:v.co.x*=1.09;v.co.y*=1.2
  o.data.update()
bpy.context.view_layer.update()

scene=bpy.context.scene;objects=[o for o in scene.objects if o.type=='MESH']
scene['reference']='Концепт-лист светящейся медной руды.png'
scene['status']='Copper V2; independent reference reconstruction; not imported into Roblox'
scene['orientation']='Front -Y; Z up; one authored unit intended as one stud'
scene['scope']='Intact deposit only. Mining states and hit particles in concept sheet are not implemented here.'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'CopperOutcropV2.glb'),export_format='GLB',use_selection=True)
bb=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
lo=Vector([min(v[i] for v in bb) for i in range(3)]);hi=Vector([max(v[i] for v in bb) for i in range(3)])
center=(lo+hi)/2;size=max(hi-lo)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Reference comparison camera';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.25
for p,power,s in [((-3,-4,7),420,5),((4,-2,4),180,5),((0,4,5),250,4)]:
 bpy.ops.object.light_add(type='AREA',location=p);l=bpy.context.object;l.data.energy=power;l.data.size=s
 l.rotation_euler=(center-l.location).to_track_quat('-Z','Y').to_euler()
scene.world=bpy.data.worlds.new('Neutral world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard';scene.render.film_transparent=True
def angle(direction,name):
 cam.location=center+Vector(direction)*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(ROOT/name);bpy.ops.render.render(write_still=True)
angle((.12,-2, .85),'CopperOutcropV2.png')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_location=center;area.spaces.active.region_3d.view_distance=size*1.8
for o in scene.objects:
 if o.type in ['CAMERA','LIGHT']:o.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'CopperOutcropV2.blend'))
angle((0,-2,.02),'front.png');angle((2,0,.25),'side.png');angle((0,0,2),'top.png');angle((.6,2,.65),'back.png')
report={'name':'CopperOutcropV2','mesh_objects':len(objects),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects),'size':list(hi-lo),'roblox_import_tested':False}
(ROOT/'manifest.json').write_text(json.dumps(report,indent=2))
print('COPPER_V2_BUILT',json.dumps(report),flush=True)
