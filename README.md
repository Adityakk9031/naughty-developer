# Naughty Developer — Automated DXF to 3D Model, Amenities, Interiors & 360° Virtual Tour (Level 1 + Level 2)

An end-to-end automated architectural pipeline that reads the municipal submission drawing (`drawing.dxf` / `.dwg`) for **Naughty Developer** (a 7-storey residential tower in a dense urban setting with basement + stilt parking, $2 \times \text{4BHK}$ flats per floor, entrance lobby, landscaped drive, and rooftop terrace amenities) and generates everything 100% by code:

1. **Clean 2D & Room Geometry (`outputs/extracted_geometry.json`)** — Reconstructed closed polygons for Basement parking (slab, columns, curved ramp, 2 car bays, 20 two-wheeler bays), Ground Floor Stilt Parking (5 car bays, 15 two-wheeler bays) & Entrance Lobby, 1st–7th Typical Floor slabs, 23 structural columns, walls, $0.60\text{ m}$ projections, windows, sliding doors, wall-snapped room bounds for all rooms in **Type A ($160.05\text{ m}^2$)** and **Type B ($143.18\text{ m}^2$)** flats, Terrace Amenity Zones, and Site Layout (plot boundary, $18\text{ m}$ road, 25 trees).
2. **Generated 3D Model (`outputs/naughty_developer.blend`)** — Built procedurally in headless Blender (`bpy` + `trimesh` + `shapely`) with geometry-driven furniture placement (`pipeline/furnish.py`) across both Type A and Type B flats plus all 5 amenity spaces.
3. **20 Photoreal Stills (`2560 × 1440 px`)**: each is a Blender render of the model (`outputs/ai_bases/stills/`) finished in MyArchitectAI (`pipeline/prepare_myarchitectai.py` → upload → `pipeline/import_external_stills.py`, which layout-checks each result against the model's depth map). Ten test images still carry the MyArchitectAI watermark and must be re-rendered before final delivery. `build.py render` also produces draft Cycles stills from the same cameras:
   - **6 Amenity Stills (`outputs/amenities/`)**:
     - `amenity_1_basement_parking.png` — Basement parking bays, two-wheelers, sloped ramp, safety columns & ceiling LEDs
     - `amenity_2_stilt_parking.png` — Ground-level stilt parking bays, cars, columns & soffit lighting
     - `amenity_3_entrance_lobby.png` — Ground-floor entrance lobby with bronze lifts, travertine marble, fluted wood, chandelier & seating
     - `amenity_4_landscape_drive.png` — West landscaped garden deck, timber benches, planter beds, bollards & entrance drive
     - `amenity_5_terrace_amenities.png` — Terrace slatted pergola seating lounge, kids' play area & glass fitness gym
     - `amenity_6_terrace_gym.png` — Terrace glass fitness gym pavilion
   - **10 Interior Stills (`outputs/interiors/`, 5 per flat type)**:
     - **Type A (Front 4BHK)**: `type_a_1_drawing_room.png`, `type_a_2_kitchen_dining.png`, `type_a_3_master_bedroom.png`, `type_a_4_second_bedroom.png`, `type_a_5_third_bedroom.png`
     - **Type B (Rear 4BHK)**: `type_b_1_drawing_room.png`, `type_b_2_kitchen_dining.png`, `type_b_3_master_bedroom.png`, `type_b_4_second_bedroom.png`, `type_b_5_third_bedroom.png`
   - **4 Exterior Stills (`outputs/`)**:
     - `shot_1_eye_level_day.png`, `shot_2_front_corner_dusk.png`, `shot_3_aerial_day.png`, `shot_4_entrance_closeup.png`
4. **16 Photoreal Equirectangular $360^\circ$ Panoramas (`6144 × 3072 px`, `outputs/panoramas/`)**, one per tour spot, made the same way:
   - **Building & Amenities (6)**: Entrance Gate, Entrance Lobby, Basement Parking, Garden & Stilt, Terrace Pergola & Kids' Play, Terrace Fitness Gym.
   - **Type A Interior (5)**: Drawing Room, Kitchen & Dining, Master Bedroom (SE), Second Bedroom (Mid-East), Third Bedroom (SW) & Balcony View.
   - **Type B Interior (5)**: Drawing Room, Kitchen & Dining, Master Bedroom (NE), Second Bedroom (NW), Third Bedroom (Mid-West).
5. **Interactive Web $360^\circ$ Tour, 3D Model & Stills Viewer (`viewer/index.html` + `outputs/naughty_developer.glb`)**:
   - **`360° Virtual Tour (16 Spots)`**: Opens in the 360° view: drag to look around any of the 16 spots, click **3D Hotspot Portals** to step to the next spot, or jump via the categorized list and **interactive 2D Floor/Site Minimap**. *Still Photo* switches to the room's 2560 × 1440 still.
   - **`3D Building Model (.glb)`**: Orbit/pan/zoom the full building (`<= 40 MB`), toggle Day/Dusk lighting, click any floor (including Basement B1) or flat (`Type A` / `Type B`), and slice upper floors.
   - **`Stills Gallery (20 Renders)`**: Browse all 6 Amenity, 10 Interior, and 4 Exterior renders at full $2560 \times 1440$ resolution.

---

## Name and massing

The building name (`BUILDING_NAME`) and the tower's silhouette are set in [`pipeline/design_variation.py`](pipeline/design_variation.py): floors 2-7 and the terrace twist 1° more per storey and step in 0.8% per storey, and the name is modelled on the roof, above the lobby lifts and on the entrance wall. Change the constants and run `python build.py build && python build.py export`. Ground, basement and floor 1 keep the drawn plan. The stills and 360° images in `outputs/` were rendered before this change and show the earlier massing and sign, so re-run the render pipeline (below) before publishing them.

---

## How the photoreal 360° spots are made

Every 360° spot starts as a Blender render of `outputs/naughty_developer.blend`, the model built from the CAD drawing. AI only finishes materials and lighting; it never invents the layout. (The same pipeline can finish the 20 still cameras too, by packaging without `--panos-only`; for this delivery the earlier concept stills were kept.)

```
drawing.dxf ─► extract ─► build (naughty_developer.blend) ─► render_ai_bases ─► finish_ai (GPU) ─► import_ai_results ─► viewer
                                                           beauty + exact depth   RealVisXL img2img     provenance hashes +
                                                           per spot / camera      + depth & edge        layout-match score
                                                                                  ControlNets
```

1. **Base renders (this machine, CPU, ~2.5 h)** — beauty plus an exact depth map (camera distance in cm) for all 16 spots (equirectangular) and 20 still cameras:
   ```bash
   python -m pipeline.render_ai_bases all --panos-only
   python -m pipeline.package_ai_inputs --panos-only   # -> outputs/ai_handoff/ai_inputs.zip
   ```
2. **AI finishing (free Kaggle / Colab GPU, ~2–3 h on a T4)** — upload the zip and run [`notebooks/ai_finish.ipynb`](notebooks/ai_finish.ipynb). [`pipeline/finish_ai.py`](pipeline/finish_ai.py) runs RealVisXL V5 in img2img mode with two ControlNets (xinsir depth + canny) fed from the model's depth and edges, so walls, openings and furniture stay where the model has them. For a 360° spot it pads the equirect with its own opposite edge, regenerates the 0°/360° seam, redoes ceiling and floor as undistorted cube faces, then adds detail tile by tile at 6144 × 3072. An optional style reference (IP-Adapter, weight 0.35) carries over the look of earlier images the client approved (`outputs/ai_style_refs/`). All models are licensed for commercial use (openrail++, Apache 2.0, MIT).
3. **Import and verify (this machine)**:
   ```bash
   python -m pipeline.import_ai_results path/to/ai_results.zip
   python pipeline/verify_all.py
   ```
   The import refuses any result whose base or depth hash differs from the packaged model render, scores how much of the model's geometry (depth jumps at furniture, doors, windows, wall ends) survives in each image, and writes `outputs/ai_manifest.json`. `verify_all.py` fails unless every shipped 360° panorama is in that manifest, byte-identical to the import, and scores at least 0.30 (the raw model render scores about 0.6; an unrelated photo of a similar room scores about 0).

---

## Quick Start

> **No drawing is included.** `outputs/extracted_geometry.json` (the extracted geometry) is, so `python build.py build`,
> `export` and `render` work as is. To start from your own drawing, put a DXF with the same layer scheme at
> `drawing.dxf` and run `python build.py` (see `config.json` for the layer and region maps). The extraction tests are
> skipped when `drawing.dxf` is absent.

### 1. Prerequisites & Setup

Requires **Python 3.11 – 3.13** (on macOS, Linux, or Windows). Headless Blender (`bpy`) is installed via `pip`:

```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline (One Command)

Rebuilds the geometry, model and draft Cycles renders (`outputs/extracted_geometry.json`, `outputs/naughty_developer.blend`, `outputs/naughty_developer.glb`, 20 draft stills, 16 draft panoramas) directly from `drawing.dxf`. The photoreal versions come from the three steps above.

```bash
python build.py
# or on macOS / Linux:
make all
```

### 3. Run Individual Pipeline Stages

```bash
python build.py extract                 # Stage 1: DXF -> outputs/extracted_geometry.json
python build.py build                   # Stage 2: 2D JSON -> outputs/naughty_developer.blend (with amenities & interiors)
python build.py render                  # Stage 3: Draft Cycles renders, 20 stills (2560x1440) + 16 360° panoramas (6144x3072)
python build.py render --only amenities # Render only the 6 amenity stills
python build.py render --only interiors # Render only the 10 interior stills
python build.py render --only panoramas # Render only the 16 360° panoramas
python build.py export                  # Stage 4: Export web-ready outputs/naughty_developer.glb (<= 40 MB)
```

### 4. Run the Tests (extraction + AI finishing geometry, seams and provenance)

```bash
python -m pytest -v
```

### 5. Launch the Interactive Web $360^\circ$ & 3D Viewer

```bash
python -m http.server 8090 --directory viewer
# Then open http://localhost:8090 in your browser
```
