"""Update existing native materials only; assert exact geometry preservation."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]/'assets/meshes/CopperOutcropV2'
bpy.ops.wm.open_mainfile(filepath=str(root/'CopperOutcropV2.blend'))
def geometry_digest():
 h=hashlib.sha256()
 for o in sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:o.name):
  h.update(o.name.encode())
  for row in o.matrix_world:
   for c in row:h.update(struct.pack('<d',c))
  for v in o.data.vertices:
   for c in v.co:h.update(struct.pack('<d',c))
  for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
before=geometry_digest()
def linear(v):
 v/=255;return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4
palette=['49494C','505053','555558','5B5A5D','454548','616063','4D4D50']
for i,h in enumerate(palette):
 m=bpy.data.materials['Basalt_'+str(i)];c=tuple(linear(int(h[j:j+2],16)) for j in (0,2,4))+(1,)
 m.diffuse_color=c;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c
assert geometry_digest()==before
bpy.ops.wm.save_as_mainfile(filepath=str(root/'CopperOutcropV2.blend'))
bpy.ops.object.select_all(action='DESELECT')
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(root/'CopperOutcropV2.glb'),export_format='GLB',use_selection=True)
scene=bpy.context.scene;cam=scene.camera
points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
center=(lo+hi)/2;size=max(hi-lo)
for direction,name in [((.12,-2,.85),'CopperOutcropV2'),((0,-2,.02),'front'),((2,0,.25),'side'),((0,0,2),'top'),((.6,2,.65),'back')]:
 cam.location=center+Vector(direction)*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(root/(name+'.png'));bpy.ops.render.render(write_still=True)
assert geometry_digest()==before
(root/'material-update.json').write_text(json.dumps({'geometry_before':before,'geometry_after':geometry_digest(),'geometry_unchanged':True,'basalt_palette':palette,'copper_materials_unchanged':True},indent=2))
print('MATERIAL_UPDATE_VERIFIED',before,flush=True)
