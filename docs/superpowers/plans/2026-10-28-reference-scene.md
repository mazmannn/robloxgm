# Reference scene implementation plan

Goal: implement the four images in Desktop/ideas as a playable stylized low-poly scene, without hub buildings, with Penkun on the forest path.

User authorizes implementation directly. Preserve source map, existing combat/mining/dialog rules and mobile selection. Use deterministic Roblox geometry; no external asset uploads. Realistic fur in the moss image is adapted to faceted moss. Reference labels/storyboards are descriptive, not new gameplay commands. No extra colour variants, NPC professions, quests, portals or defensive powers implied by sheet captions.

- [x] Shared geometry and factories: faceted moss companion, copper outcrop, stump monster with sprout and mushroom. Keep query hitboxes and paw animation stable.
- [x] Server SceneBuilder: walkable hub, central tree, stone gateway, forest route, rocks/trees/fences/lanterns; zero houses or shops. Move spawn and configured targets to the scene; enemy on forest route. Preserve user's disk map.
- [x] Replace client placeholders; retain HP, selection, harvesting, respawn and merchant dialog. Copper is visual replacement with existing test currency, not a silent economy migration.
- [x] Build/tests, independent review, separate preview and editable model export. First visual pass inspected in Studio.
- [ ] Final visual approval after rounded silhouette refinement, full walk-through and real-phone performance. See docs/reference-scene.md for exact verification boundaries.

Limits: hand-built procedural models approximate the references, rather than recovering their original meshes. Static enemy remains without animation, as last explicitly requested. Scene is generated at runtime from source and can be exported as an editable model by the build tools. No main-map overwrite.
