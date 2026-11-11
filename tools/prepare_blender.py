"""Run with Blender --background --python tools/prepare_blender.py."""
import bpy, pathlib, json
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1]/'assets'/'meshes'
results=[]
for name in ['MossCompanion','Penkun','CopperOutcrop']:
    target=ROOT/name
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=str(target/(name+'.obj')),forward_axis='NEGATIVE_Z',up_axis='Y',use_split_groups=True)
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert objects, 'No imported geometry'
    for obj in objects:
        bpy.context.view_layer.objects.active=obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(False)
    for mat in bpy.data.materials:
        mat.use_nodes=True
        shader=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if shader:
            shader.inputs['Roughness'].default_value=.9
            shader.inputs['Metallic'].default_value=0
    scene=bpy.context.scene
    scene.unit_settings.system='NONE'
    scene['source_axes']='OBJ Y up, front -Z; Blender Z up after import'
    scene['source_scale']='1 Blender unit corresponds to 1 Roblox stud; no automatic rescale'
    scene['status']='Editable reconstruction; no rig or gameplay integration yet'
    bounds=[obj.matrix_world@Vector(p) for obj in objects for p in obj.bound_box]
    center=sum(bounds,Vector())/len(bounds)
    bpy.ops.object.camera_add(location=center+Vector((6,10,5)))
    camera=bpy.context.object;camera.name='PreviewCamera'
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=6.5;scene.camera=camera
    for pos,power,size in [((3,5,7),350,5),((-4,2,4),180,5)]:
        bpy.ops.object.light_add(type='AREA',location=pos)
        light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size
        light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
    scene.world=bpy.data.worlds.new('StudioWorld');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.29,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
    scene.render.engine='CYCLES';scene.cycles.samples=16
    scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
    scene.render.filepath=str(target/(name+'-blender.png'))
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.wm.save_as_mainfile(filepath=str(target/(name+'.blend')))
    bpy.ops.render.render(write_still=True)
    results.append({'name':name,'meshes':len(objects),'materials':len(bpy.data.materials),'blend':name+'.blend'})
(ROOT/'blender-import-report.json').write_text(json.dumps(results,indent=2))
print('BLENDER_IMPORT_OK',json.dumps(results))
