"""Reopen native assets and independently import their GLBs; build inspection library."""
import bpy,json,math,struct
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]/'assets/meshes/EnvironmentV2'
items=json.loads((ROOT/'manifest.json').read_text())
assert len(items)==19 and len({i['name'] for i in items})==19
report=[]
def bounds(objects):
 bpy.context.view_layer.update()
 p=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
 return [max(v[i] for v in p)-min(v[i] for v in p) for i in range(3)]
for item in items:
 name=item['name'];folder=ROOT/name
 bpy.ops.wm.open_mainfile(filepath=str(folder/(name+'.blend')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 assert len(meshes)==item['mesh_objects'],name
 for obj in meshes:
  assert len(obj.data.materials)>0 and all(math.isfinite(v) for p in obj.data.vertices for v in p.co),obj.name
  assert all(p.area>1e-9 for p in obj.data.polygons),('Degenerate polygon',obj.name)
 triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
 assert triangles==item['triangles']
 native=bounds(meshes)
 png=(folder/(name+'.png')).read_bytes()
 assert png[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',png[16:24])==(800,800)
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(folder/(name+'.glb')))
 imported=[o for o in bpy.context.scene.objects if o.type=='MESH']
 assert imported and all(o.data.materials for o in imported)
 size=bounds(imported)
 assert all(abs(a-b)<.01 for a,b in zip(size,native)),(name,native,size)
 report.append({'name':name,'blend_reopened':True,'glb_imported':True,'native_meshes':len(meshes),'triangles':triangles,'size':native,'export_bounds_match':True,'render_size':[800,800]})
 print('ROUNDTRIP_OK',name,triangles,flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
for index,item in enumerate(items):
 with bpy.data.libraries.load(str(ROOT/item['blend']),link=False) as (source,target):target.objects=source.objects
 collection=bpy.data.collections.new(item['name']);bpy.context.scene.collection.children.link(collection)
 for obj in target.objects:
  if obj and obj.type=='MESH':collection.objects.link(obj);obj.location+=Vector(((index%5)*30,(index//5)*32,0));obj.hide_set(False)
scene=bpy.context.scene
scene['purpose']='V2 asset inspection library. Not a game map. Houses not placed in Roblox.'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_location=(60,48,0);area.spaces.active.region_3d.view_distance=130
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'EnvironmentLibraryV2.blend'))
(ROOT/'verification.json').write_text(json.dumps({'verified_assets':len(report),'checks':report,'roblox_import_tested':False},indent=2))
print('V2_VERIFIED',len(report),flush=True)
