"""Extract actual Blender geometry/materials for an offline Studio inspection place."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
base=Path(__file__).resolve().parents[1]
root=base/'assets/meshes'
items=json.loads((root/'EnvironmentV2/manifest.json').read_text())
sources=[(i['name'],root/'EnvironmentV2'/i['blend'],False) for i in items]
sources += [('MossCompanion',root/'MossCompanion/MossCompanion.blend',True),('Penkun',root/'Penkun/Penkun.blend',True),('CopperOutcropV2',root/'CopperOutcropV2/CopperOutcropV2.blend',False)]
def srgb(c):return max(0,min(1,c*12.92 if c<=.0031308 else 1.055*c**(1/2.4)-.055))
result=[]
for name,path,flip in sources:
 bpy.ops.wm.open_mainfile(filepath=str(path))
 deps=bpy.context.evaluated_depsgraph_get();points=[];faces=[];colors=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  obj=o.evaluated_get(deps);m=obj.to_mesh();m.calc_loop_triangles();offset=len(points)
  for v in m.vertices:
   p=obj.matrix_world@v.co
   points.append([float(-p.x if flip else p.x),float(p.z),float(p.y if flip else -p.y)])
  for t in m.loop_triangles:
   mat=m.materials[t.material_index] if m.materials else None
   c=mat.diffuse_color if mat else (.5,.5,.5,1);glow=False
   if mat and mat.use_nodes:
    bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bs:
     c=bs.inputs['Base Color'].default_value
     glow=bs.inputs.get('Emission Strength') is not None and bs.inputs['Emission Strength'].default_value>.2
   color=[round(srgb(float(x)),4) for x in c[:3]]+[glow]
   if color not in colors:colors.append(color)
   faces.append([*[offset+i+1 for i in t.vertices],colors.index(color)+1])
  obj.to_mesh_clear()
 lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
 for p in points:p[0]-=(lo[0]+hi[0])/2;p[1]-=lo[1];p[2]-=(lo[2]+hi[2])/2
 result.append({'name':name,'vertices':points,'triangles':faces,'colors':colors,'size':[hi[i]-lo[i] for i in range(3)]})
 print('EXTRACTED',name,len(faces),flush=True)
(base/'download/gallery-geometry.json').write_text(json.dumps(result,separators=(',',':')))
print('GALLERY_EXTRACTED',len(result),flush=True)
