import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]/'assets'/'meshes'/'Environment'
items=json.loads((root/'manifest.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
report=[]
for index,item in enumerate(items):
 name=item['name'];path=root/item['blend']
 assert path.is_file() and (root/name/(name+'.png')).is_file()
 assert (root/name/(name+'.glb')).read_bytes()[:4]==b'glTF'
 with bpy.data.libraries.load(str(path),link=False) as (source,target):target.objects=source.objects
 collection=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(collection)
 meshes=[o for o in target.objects if o and o.type=='MESH']
 assert meshes,name
 for obj in meshes:
  collection.objects.link(obj);obj.location+=Vector(((index%5)*38,(index//5)*38,0))
  assert len(obj.data.materials)>0 and all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
 report.append({'name':name,'meshes':len(meshes),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)})
bpy.context.scene['purpose']='Asset inspection library only; houses are not placed in the game hub'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'EnvironmentLibrary.blend'))
(root/'verification.json').write_text(json.dumps(report,indent=2))
print('LIBRARY_VERIFIED',len(report))
