---
name: ezblender
description: >
  Run EZBlender multi-agent 3D editing in Blender from a natural-language prompt.
  Plans with a Planner agent, then dispatches Modder / Material / Lighting / Background
  (and optional Camera) to edit Python scene scripts and re-render. Use when the user
  wants Blender scene editing, shape-key edits, material/lighting changes, product-shot
  restyling, cyberpunk neon looks, muscular body edits, facial expression edits,
  Plan-and-ReAct 3D editing, or runs /ezblender.
metadata:
  short-description: "Plan-and-ReAct multi-agent Blender 3D editing"
  author: EZBlender
compatibility: Requires Blender, Python 3.10+, OpenAI API key in creds/openai.txt
argument-hint: '"edit description" [--preset body|face|lotion|wood|roses] [--out DIR]'
---

# EZBlender Skill

Automate **text-driven 3D editing** in Blender using the EZBlender Plan-and-ReAct multi-agent pipeline.

## When this skill applies

- User asks to edit a Blender scene / product render / character with a text prompt
- Mentions shape keys, materials, lighting, neon/cyberpunk, gold metal, facial expression
- Wants to run or debug `main.py` under the EZBlender package
- Invokes `/ezblender`

## Package root

Resolve the EZBlender package root before any command:

1. Prefer current working directory if it contains `main.py` + `ezblender/` + `blenderalch/`
2. Else use `github/EZBlender` relative to the BlenderAlchemyOfficial repo root
3. Else ask the user for the path

All paths below are relative to that package root unless absolute.

## Prerequisites (check once)

1. **Blender executable** available (`blender` on PATH, or a full path such as `E:/2025/Blender/blender/blender.exe`).
2. **API key** in `creds/openai.txt` (single line; OpenAI `sk-...` or Azure key). Never commit or print the full key.
3. **Python deps**: `pip install -r requirements.txt` (minimum: `openai`, `Pillow`, `pyyaml`, `loguru`).
4. Working directory = package root when launching `main.py` (relative asset paths depend on this).

If Blender or the key is missing, stop and tell the user what to set — do not invent paths or keys.

## Workflow (always follow this order)

### 1. Clarify the edit

Extract or confirm:

| Field | Meaning |
|-------|---------|
| `prompt` | Natural-language goal (required) |
| `preset` or asset trio | Which blend + init script + render script |
| `out_dir` | Where to write results (default `./output/<slug>`) |
| `model` | VLM id (default from `main.py`, often `gpt-5.4-mini`) |
| `parallel` | Prefer parallel agent fan-out (default on) |
| `blender_exe` | Path to Blender |

If the user only gives a prompt, pick the best **preset** from `references/presets.md` and state the choice briefly.

### 2. Map prompt → assets

Use the preset table in [references/presets.md](references/presets.md). Quick rules:

- Body / muscular / thin / fat / proportions → **body**
- Face / smile / frown / expression / wink → **face**
- Bottle / product / gold / neon / cyberpunk lighting → **lotion**
- Wood → marble / BSDF material nodes → **wood**
- Geometry nodes roses → **roses**

Do not invent new `.blend` paths that are not under `blenderalch/`.

### 3. Run the pipeline

```bash
python main.py \
  --prompt "<USER_PROMPT>" \
  --blender_exe "<BLENDER_EXE>" \
  --scene_blend "<SCENE_BLEND>" \
  --init_script "<INIT_SCRIPT>" \
  --render_script "<RENDER_SCRIPT>" \
  --model "<MODEL>" \
  --parallel \
  --out_dir "<OUT_DIR>"
```

On Windows PowerShell you may use the helper:

```powershell
.\.agents\skills\ezblender\scripts\run_ezblender.ps1 `
  -Prompt "<USER_PROMPT>" `
  -Preset body `
  -BlenderExe "<BLENDER_EXE>" `
  -OutDir "./output/run_001"
```

Long-running: Blender + VLM can take several minutes. Use a high shell timeout (e.g. 10–30 min). Prefer background execution only if the user wants to keep chatting.

### 4. Verify outputs

After the run, confirm these exist under `out_dir`:

| File | Meaning |
|------|---------|
| `init_render.png` | Baseline render before edit |
| `final_scene.py` | Assembled Blender Python after agents |
| `result_render.png` | Final render (success marker) |

Success criteria:

- Process exit code 0 **and**
- `result_render.png` exists and is non-trivial size (> ~10 KB)

If only `init_render.png` exists, the pipeline failed after planning/render — inspect console stderr and `final_scene.py`.

Open `result_render.png` (read/view image) and briefly describe whether it matches the prompt. If clearly wrong, suggest a refined prompt or a second run with a tighter task.

### 5. Optional follow-ups

- **Re-run with a sharper prompt** if the visual is partial (e.g. “pure gold metal, roughness 0, metallic 1”).
- **Inspect `final_scene.py`** for agent blocks (`# --- materials ---`, lighting, modder assignments).
- **Do not** modify `creds/` or commit API keys.
- **Do not** delete user `output/` folders unless asked.

## Architecture cheat-sheet (for debugging)

```
prompt + init render
  → Planner  → tasks JSON (modder / materials / lighting / background / camera / …)
  → execute_parallel or execute_sequential
  → assemble_final_script (+ try/except isolation per agent)
  → Blender render → result_render.png
  → on failure: debug_agent per agent code, re-render once
```

Known gaps to keep in mind:

- Planner may emit `camera` / `postprocess`; executor currently wires **modder, materials, lighting, background** most reliably.
- Material/lighting agents may be text-only; stronger visual results often need clear material/lighting language in the prompt.
- `model_refine` / modder critic exist in code but are not always on the default `main.py` path.

## Failure playbook

| Symptom | Action |
|---------|--------|
| `Initialization Error` / missing key | Fix `creds/openai.txt` or env; never hardcode secrets in scripts |
| Blender not found | Pass absolute `--blender_exe` |
| `result_render.png` missing | Read stderr; open `final_scene.py`; re-run with simpler prompt |
| Empty or broken agent code | Re-run sequential if parallel race suspected; tighten prompt to one domain (material-only or shape-only) |
| Wrong scene type | Switch preset (body vs lotion vs face) |

## What not to do

- Do not reimplement the multi-agent loop from scratch when `main.py` can run.
- Do not path into root research code (`ez_agent.py` / `exp/`) unless the user explicitly wants the old experiment stack.
- Do not upload secrets, full API keys, or private blend files to external services.
- Do not claim paper metrics/benchmarks unless you re-run eval code; this skill is for **interactive editing demos**.

## Example invocations

**Muscular character**

```bash
python main.py \
  --prompt "Make the character an extremely muscular professional bodybuilder with bulging biceps and chest" \
  --blender_exe "blender" \
  --scene_blend "blenderalch/starter_blends/body_shapekeys.blend" \
  --init_script "blenderalch/blender_scripts/shapekeys_examples/bodyshape.py" \
  --render_script "blenderalch/blender_base/bodyshape_shapekeys.py" \
  --out_dir "./output/body_muscular"
```

**Gold product**

```bash
python main.py \
  --prompt "Turn the entire object into a shiny, reflective pure gold material like a trophy" \
  --blender_exe "blender" \
  --scene_blend "blenderalch/starter_blends/lotion.blend" \
  --init_script "blenderalch/blender_scripts/lighting_examples/lotion.py" \
  --render_script "blenderalch/blender_base/lighting_adjustments.py" \
  --out_dir "./output/lotion_gold"
```

**Cyberpunk lighting**

```bash
python main.py \
  --prompt "Midnight cyberpunk theme with glowing purple and cyan neon rim lights" \
  --blender_exe "blender" \
  --scene_blend "blenderalch/starter_blends/lotion.blend" \
  --init_script "blenderalch/blender_scripts/lighting_examples/lotion.py" \
  --render_script "blenderalch/blender_base/lighting_adjustments.py" \
  --parallel \
  --out_dir "./output/lotion_cyber"
```

## Response style

When finishing a run for the user:

1. State preset + out_dir used  
2. Link/path to `init_render.png` and `result_render.png`  
3. One short visual comparison sentence  
4. Next-step options (reprompt, different preset, inspect script)
