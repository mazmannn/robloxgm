# Blender environment kit

Reference: Desktop/ideas/Концепт фэнтезийного хаба с воротами.png. Nineteen editable low-poly reconstructions; these are approximations of the image, not its source 3D files. Blender 5.2.3 LTS.

Each named folder contains a `.blend`, a `.glb` with embedded materials and a rendered `.png`. Models use Z up and face -Y in Blender; dimensions are authored in Roblox studs. Cameras/lights in blend files are for preview only and are excluded from GLB exports. Mesh details remain individually editable. No rig, interiors, collision setup or Roblox asset upload is included.

- WayfarerTree, BiomeGate: central tree landmark and stone gateway with banners.
- Pine, BroadleafTree: evergreen and broadleaf trees.
- RockCluster1/2/3: three irregular rock groups.
- Lantern, Fence, Paving, Bridge: modular route props.
- HouseBrown/Red/Blue/Green: four house palette variants sharing a base structure, based on the empty houses pictured in the PNG. Roof shingles, timber, windows, door, steps and chimney are separate parts. Individual architectural differences from the PNG still need manual refinement.
- Forge, Alchemist, PetKeeper, ResourceStall: functional-looking building/market variants with forge/anvil, cauldron, canopy/crates and stall. No gameplay logic is attached.

Open `EnvironmentLibrary.blend` to inspect all models together, grouped in collections on a spaced grid. This is an asset library, not the gameplay map. `catalog.png` shows all previews. `manifest.json` lists dimensions and paths; `verification.json` records reopened meshes and triangle counts.

Nothing from this kit has been placed in the game hub. In particular, houses remain assets only, as requested earlier. Existing map and character blend files were preserved.

Rebuild using Blender background scripts `tools/create_environment_blender.py`, then `tools/assemble_environment_library.py`. Render catalog with `tools/environment_contact_sheet.py` in Python with Pillow. Generator rebuilds overwrite generated files: save manual edits under a new name before rebuilding. A single model can be rebuilt with `-- --only BiomeGate` after the script arguments.

Visual QA inspected house, tree and gate renders; the initial disconnected cube arch was replaced with fitted mesh voussoirs. Structural QA reopens every blend, checks finite mesh coordinates, material slots, PNG presence and GLB headers. Mobile performance, import scale/material fidelity in Studio and final resemblance to the reference need separate review.
