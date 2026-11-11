# Mesh reconstruction — first editable pass

Медная руда пересобрана отдельно: [CopperOutcropV2](CopperOutcropV2/README.md). Открывайте `CopperOutcropV2/CopperOutcropV2.blend`; папка `CopperOutcrop` сохранена как предыдущая версия.

## Новая библиотека окружения

Актуальная пересборка окружения находится в [EnvironmentV2](EnvironmentV2/README.md).
В ней 19 заново построенных объектов, включая четыре дома и четыре специализированных здания/лавки.
Открывайте `EnvironmentV2/EnvironmentLibraryV2.blend` для просмотра всего набора.
Рендеры: `EnvironmentV2/catalog.png` и `EnvironmentV2/architecture.png`.
Папка `Environment` сохранена как предыдущая версия. Ни один из этих наборов ещё не заменил модели в игре.
Описанные ниже три модели персонажей/руды относятся к отдельному первому проходу и этой пересборкой не изменялись.

## Blender ready files

Created and rendered successfully with installed Blender 5.2.3 LTS:
`MossCompanion.blend`, `Penkun.blend`, `CopperOutcrop.blend`.
Open these directly. Geometry and materials are embedded, so no OBJ import setup is needed.
Components are individual selectable mesh objects. Camera and preview lighting are included.
The OBJ coordinate conversion places the face towards Blender +Y; Blender Z is up.
Use Material Preview to see colours while editing. These are editable sources, not rigged final game assets.

Rebuild all blend files using:
`"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python tools/prepare_blender.py`

This rebuild replaces generated blend files. Save manual edits under another name before running it.
Blender reported sandbox-denied user thumbnail/extension cache writes; project blend files and renders were saved successfully.

Sources reconstructed from the three PNG character/resource sheets in Desktop/ideas. Approximate, not extracted meshes. Palette and anatomy still need visual refinement against references. World scenery is handled separately.

- MossCompanion.obj: moss body, cream face, eyes, blush, mouth, feet, separate paw groups and branch antlers.
- Penkun.obj: bark panels, cut surface, growth rings, face, branch arms/fingers, legs, leaves and mushroom.
- CopperOutcrop.obj: faceted stone groups with separate copper inclusions.
- palette.mtl: shared diffuse colours; keep beside OBJ files. No image textures required.
- *-views.png/svg: generated geometry proofs (front, 3/4, back), not Roblox screenshots. The simple painter renderer can show triangle sorting artefacts at intersections.

Units are Roblox studs; Y up; front faces -Z. OBJ groups preserve editable components. Vertices at matching coordinates are welded. No rig, UV texture painting, LODs or animation clips yet. Glow is not embedded in diffuse OBJ materials.

Regenerate: `python tools/create_mesh_assets.py`. Previews: `tools/render_mesh_previews.py` using a Python environment with Pillow.

Import OBJ into a 3D editor with Y-up orientation and the adjacent MTL. Check normals, intersections, scale and groups before converting for Roblox. These meshes have NOT yet replaced the procedural Roblox models, and no mesh assets have been uploaded. Test the importer/material handling and rig before switching gameplay.

Next work: reference comparison and sculptural refinement (moss silhouette/antlers, stump face and tapered bark, irregular rock masses and copper veins), proper render for approval, then rig/import and phone performance checks.

## Folder layout

Each model has its own directory: MossCompanion/, Penkun/, CopperOutcrop/. All its OBJ, blend, backup and preview files live together. Shared materials are in shared/palette.mtl; OBJ files reference ../shared/palette.mtl. Open the blend file inside the matching model folder.
