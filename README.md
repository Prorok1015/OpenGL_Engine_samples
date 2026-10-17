# OpenGL_Engine samples

Test 3D models for the [OpenGL_Engine](https://github.com/Prorok1015/OpenGL_Engine) editor (import, rendering, materials).
Connected to the engine as an optional submodule at `Editor/res/samples` (not fetched by default, not used by CI).

```bash
# inside the engine checkout
git submodule update --init --checkout Editor/res/samples
```

| Folder | Format | Source / license |
|---|---|---|
| `backpack/` | OBJ + PBR textures | Berk Gedik (Sketchfab), modified by Joey de Vries — see `backpack/source_attribution.txt` |
| `getaur/` | glTF | Lars Maes (Sketchfab), CC-BY-4.0 — see `getaur/license.txt` |
| `train/` | glTF | Jesper Landin (Sketchfab), Sketchfab Standard license — see `train/license.txt` |
| `helicopter/` | GLB + textures | source/license not recorded |
