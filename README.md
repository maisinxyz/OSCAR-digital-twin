# OSCAR digital twin — handoff pack
- CLAUDE_CODE_PROMPT.md  → paste into Claude Code (Opus 5.5 main + 1 Sonnet 5.5 subagent)
- assets/oscar.glb       → web-ready 3D model (separated named parts; NO physics, NO springs)
- assets/renders/*.webp  → Blender Cycles renders (placeholders/fallbacks) + meta.json (projected anchor points)
- blender/oscar_model.py → Blender (bpy) source. Export GLB: python oscar_model.py --export 1 --out ../assets/oscar.glb
- blender/oscar_render.py, run_all.sh, post.py → how the renders were made
- docs/rubric/           → project + syllabus PDFs (Claude Code reads these first)
- docs/INPUTS.md         → YOU fill this in before starting
Setup: copy this folder to a new git repo, run `claude` in it, `/model opus`, paste the prompt.
