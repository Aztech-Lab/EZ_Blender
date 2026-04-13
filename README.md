# EZBlender: Efficient 3D Editing with Plan-and-ReAct Agent
The official implementation of the paper [EZBlender: Efficient 3D Editing with Plan-and-ReAct Agent](https://openaccess.thecvf.com/content/WACV2026W/VALED/html/Wang_EZBlender_Efficient_3D_Editing_with_Plan-and-ReAct_Agent_WACVW_2026_paper.html)


## Updates
- 4/10/2026: We are currently packaging the entire workflow into a skill for AI agents.
- 4/1/2026: We are currently working on the EZBench that benchmarking the ability of 3D editing among Models/Agents. 
- 3/27/2026: We re-constructed the code using Codex CLI. 
- 1/7/2026: Our paper is selected as the best paper.
- 1/1/2026: Our paper is accepted by WACV2026@VALED.

EZBlender is a lightweight, modular framework for automating 3D scene editing in Blender using Vision-Language Models (VLMs). It employs a multi-agent architecture where a central **Planner** decomposes high-level user prompts into specific sub-tasks for specialized agents (**Modder**, **Material**, **Lighting**, **Camera**, etc.).

## Key Features

- **Multi-Agent Pipeline**: Intelligent task decomposition and execution.
- **Vision-Feedback Loop**: Autonomous refinement based on visual output analysis.
- **Modular Design**: Easily extendable with new agent roles or VLM providers.
- **Automatic Debugging**: Integrated error analysis and code fixing.

## Architecture

1.  **Planner**: Receives the prompt and current scene state, then creates a task list.
2.  **Specialized Agents**: 
    - `Modder`: Handles geometry and shape keys.
    - `Material`: Manages shaders and textures.
    - `Lighting`: Adjusts scene illumination.
    - `Camera`: Optimizes camera placement.
3.  **Refinement Loop**: The `Modder Critic` evaluates results and iterates until satisfied.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/EZBlender.git
    cd EZBlender
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment Variables**:
    Set your OpenAI credentials:
    ```bash
    /creds/openai.txt
    ```

## Quick Start

Run the main workflow with a text prompt. Note that the assets are located in the `blenderalch/` directory:

```bash
python main.py \
    --prompt "Make the object extremely bright glowing neon green" \
    --blender_exe "/path/to/blender" \
    --scene_blend "blenderalch/starter_blends/lotion.blend" \
    --init_script "blenderalch/blender_scripts/lighting_examples/lotion.py" \
    --render_script "blenderalch/blender_base/lighting_adjustments.py" \
    --out_dir "./output/test_run"
```

## Acknowledgement
We sincerely appreciate the authors of [BlenderAlchemy](https://github.com/ianhuang0630/BlenderAlchemyOfficial),
since EZBlender is a streamlined evolution of the BlenderAlchemy project. 
We have distilled the prompting logic from the original work into this lightweight, multi-agent framework, while preserving the original assets and research heritage within the `blenderalch/` directory. 

## Contributing


## Citation
If you find this project helpful to your research, please consider citing [BibTeX]():
```bibtex
@InProceedings{Wang_2026_WACV,
    author    = {Wang, Hao and Zhu, Wenhui and Tang, Shao and Wang, Zhipeng and Dong, Xuanzhao and Li, Xin and Chen, Xiwen and Bastola, Ashish and Huang, Xinhao and Wang, Yalin and Razi, Abolfazl},
    title     = {EZBlender: Efficient 3D Editing with Plan-and-ReAct Agent},
    booktitle = {Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision (WACV) Workshops},
    month     = {March},
    year      = {2026},
    pages     = {1343-1352}
}
```
