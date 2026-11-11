import bpy,math,json,struct
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]/'assets/meshes/CopperOutcropV2'
bpy.ops.wm.open_mainfile(filepath=str(root/'CopperOutcropV2.blend'))
def inspect():
 bpy.context.view_layer.update()
 objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in objects:
  assert o.data.materials,o.name
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
  assert all(p.area>1e-10 for p in o.data.polygons),o.name
 points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
 return [max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)]
native=inspect()
for name in ['CopperOutcropV2','front','side','top','back']:
 data=(root/(name+'.png')).read_bytes()
 assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(1000,1000)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'CopperOutcropV2.glb'))
exported=inspect()
assert all(abs(a-b)<.001 for a,b in zip(native,exported)),(native,exported)
report={'blend_reopened':True,'glb_reimported':True,'finite_geometry':True,'nondegenerate_faces':True,'five_renders_verified':True,'bounds_match':True,'size':native,'roblox_import_tested':False}
(root/'verification.json').write_text(json.dumps(report,indent=2))
print('COPPER_VERIFIED',json.dumps(report),flush=True)
