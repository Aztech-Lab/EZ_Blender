import os
import time
import json
import argparse
from ezblender import (
    init_client, run_blender, ensure_dir, copy_script, get_key_from_file, 
    code_to_file, apply_suggested_code,
    planner_agent, modder_agent, modder_critic_agent, material_agent, 
    lighting_agent, camera_agent, background_agent, debug_agent
)
from ezblender.core.executor import (
    execute_sequential, execute_parallel, 
    assemble_final_script, run_final_render
)

def model_refine(client, model, prompt, initial_file, initial_img, output_path, max_rounds=5):
    current_img = initial_img
    current_file = initial_file
    history = []
    
    for i in range(max_rounds):
        print(f'--- Refinement Round {i} ---')
        inputs = {
            "client": client,
            "model": model,
            "prompt": prompt,
            "file": get_key_from_file(current_file),
            "image": current_img,
            "role": "modder_edit"
        }
        
        feedback = modder_critic_agent(inputs)
        history.append(feedback)
        
        if feedback.get('end_flag'):
            print("Refinement satisfied or early stop triggered.")
            break

        # Apply changes
        new_file = os.path.join(output_path, f"refine_{i}.py")
        new_img = os.path.join(output_path, f"refine_{i}.png")
        
        if feedback.get("suggested_code"):
            updated_code = apply_suggested_code(feedback["suggested_code"], current_file)
            code_to_file(updated_code, out_file=new_file)
            current_file = new_file
            current_img = new_img
            
    return current_file, history

def initialize_workflow(args):
    """Ensures output directories and initializes the AI client."""
    ensure_dir(args.out_dir)
    print(f"[*] Initializing workflow with model: {args.model}")
    try:
        with open("creds/openai.txt", "r") as f:
            key = f.read().strip()
        return init_client(api_key=key)
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return None

def generate_execution_plan(client, model, prompt, init_script, init_img):
    """Generates a task list using the Planner Agent."""
    print("[*] Generating execution plan...")
    planner_inputs = {
        "client": client, "model": model, "prompt": prompt,
        "file": get_key_from_file(init_script), "image": init_img
    }
    try:
        plan = planner_agent(planner_inputs)
        tasks = plan.get("tasks", {})
        if not tasks:
            print("⚠️ Warning: Planner returned an empty task list.")
        return tasks
    except Exception as e:
        print(f"❌ Planning Error: {e}")
        return {}

def execute_agent_workflow(client, model, prompt, tasks, args, init_img):
    """Routing to parallel or sequential executors and then assembling result."""
    if getattr(args, 'parallel', True):
        print("[*] Mode: Parallel Multi-threading")
        results = execute_parallel(tasks, client, model, args.init_script, init_img)
    else:
        print("[*] Mode: Sequential Single-threading")
        results = execute_sequential(tasks, client, model, args.init_script, init_img)

    # Use the decoupled modular functions from executor.py
    final_script = assemble_final_script(args.init_script, results, args.out_dir)
    render_result, result_img = run_final_render(
        args.blender_exe, args.scene_blend, final_script, 
        args.render_script, args.out_dir
    )
    
    return render_result, results, final_script, result_img

def run_auto_debug(client, model, prompt, results, last_render_result, args, final_script_path, result_img):
    """
    Attempts to fix failing code using the Debug Agent and retries rendering.
    """
    print("❌ Rendering failed! Attempting automatic debug...")
    error_log = last_render_result.get('stdout', '') + last_render_result.get('stderr', '')
    script_context = get_key_from_file(args.init_script)
    
    fixed_code_segments = [get_key_from_file(args.init_script)]
    for agent_name in ["materials", "lighting", "camera", "background"]:
        if agent_name in results and results[agent_name].get("suggested_code"):
            print(f"[*] Debugging {agent_name}...")
            debug_inputs = {
                "client": client, "model": model, "name": agent_name,
                "code": results[agent_name]["suggested_code"],
                "error_log": error_log, 
                "master_prompt": f"Context:\n{script_context}\n\nTask: {prompt}"
            }
            debug_reply = debug_agent(debug_inputs)
            fixed_code_segments.append(f"# --- {agent_name} fixed code ---")
            fixed_code_segments.append(debug_reply.get("suggested_code", results[agent_name]["suggested_code"]))
    
    temp_combined = code_to_file(fixed_code_segments)
    if "modder" in results and results["modder"].get("suggested_code"):
        final_code = apply_suggested_code(results["modder"]["suggested_code"], temp_combined)
    else:
        final_code = get_key_from_file(temp_combined)
        
    with open(final_script_path, "w", encoding="utf-8") as f:
        f.write(final_code)
        
    print("[*] Retrying final render after debug...")
    return run_blender(args.blender_exe, args.scene_blend, final_script_path, args.render_script, result_img)

def main():
    parser = argparse.ArgumentParser(description="EZBlender Multi-Agent Workflow")
    parser.add_argument("--prompt", type=str, required=True, help="Task description")
    parser.add_argument("--blender_exe", type=str, default="blender", help="Path to Blender executable")
    parser.add_argument("--scene_blend", type=str, required=True, help="Path to .blend file")
    parser.add_argument("--init_script", type=str, required=True, help="Initial script to edit")
    parser.add_argument("--render_script", type=str, required=True, help="Script that handles rendering")
    parser.add_argument("--out_dir", type=str, default="./output", help="Output directory")
    parser.add_argument("--model", type=str, default="gpt-5.4-mini", help="VLM model to use")
    parser.add_argument("--parallel", action="store_true", default=True, help="Run agents in parallel")
    args = parser.parse_args()

    client = initialize_workflow(args)
    if not client: return

    # 1. Initial Render
    init_img = os.path.join(args.out_dir, "init_render.png")
    run_blender(args.blender_exe, args.scene_blend, args.init_script, args.render_script, init_img)
    
    # 2. Planning
    tasks = generate_execution_plan(client, args.model, args.prompt, args.init_script, init_img)
    if not tasks: return
    
    # 3. Execution & Initial Render
    render_result, results, final_script, result_img = execute_agent_workflow(client, args.model, args.prompt, tasks, args, init_img)
    
    # 4. Auto-Debug if necessary
    if not render_result.get('status'):
        render_result = run_auto_debug(client, args.model, args.prompt, results, render_result, args, final_script, result_img)

    # 5. Final Status
    if render_result.get('status'):
        print(f"✅ Workflow Successful: {result_img}")
    else:
        print("❌ Workflow failed even after debug.")
    
    print(f"Results saved to {args.out_dir}")

if __name__ == "__main__":
    main()
