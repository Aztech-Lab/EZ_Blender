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
        
        # In this refactored version, we assume modder_critic_agent returns suggested_code
        if feedback.get("suggested_code"):
            updated_code = apply_suggested_code(feedback["suggested_code"], current_file)
            code_to_file(updated_code, out_file=new_file)
            
            # Note: In a real scenario, you'd need the blender_cmd and scene paths here
            # For this demo, we'll just show the logic
            # run_blender(...)
            
            current_file = new_file
            current_img = new_img
            
    return current_file, history

def main():
    parser = argparse.ArgumentParser(description="EZBlender Multi-Agent Workflow")
    parser.add_argument("--prompt", type=str, required=True, help="Task description")
    parser.add_argument("--blender_exe", type=str, default="blender", help="Path to Blender executable")
    parser.add_argument("--scene_blend", type=str, required=True, help="Path to .blend file")
    parser.add_argument("--init_script", type=str, required=True, help="Initial script to edit")
    parser.add_argument("--render_script", type=str, required=True, help="Script that handles rendering")
    parser.add_argument("--out_dir", type=str, default="./output", help="Output directory")
    parser.add_argument("--model", type=str, default="gpt-5.4-mini", help="VLM model to use")
    args = parser.parse_args()

    ensure_dir(args.out_dir)
    
    # Initialize Client
    try:
        with open("creds/openai.txt", "r") as f:
            key = f.read().strip()
        client = init_client(api_key=key)
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return

    model = args.model
    print(f"Using model: {model}")
    
    # 1. Initial Render
    init_img = os.path.join(args.out_dir, "init_render.png")
    run_blender(args.blender_exe, args.scene_blend, args.init_script, args.render_script, init_img)
    
    # 2. Planning
    planner_inputs = {
        "client": client,
        "model": model,
        "prompt": args.prompt,
        "file": get_key_from_file(args.init_script),
        "image": init_img
    }
    plan = planner_agent(planner_inputs)
    tasks = plan.get("tasks", {})
    
    # 3. Execute Sub-tasks (Modular Execution)
    results = {}
    for agent_name, task_desc in tasks.items():
        if not task_desc: continue
        
        print(f"Executing task for {agent_name}...")
        agent_inputs = {
            "client": client,
            "model": model,
            "prompt": task_desc,
            "file": get_key_from_file(args.init_script),
            "image": init_img
        }
        
        if agent_name == "modder":
            results["modder"] = modder_agent(agent_inputs)
        elif agent_name == "materials":
            results["materials"] = material_agent(agent_inputs)
        elif agent_name == "lighting":
            results["lighting"] = lighting_agent(agent_inputs)
        # elif agent_name == "camera":
        #    results["camera"] = camera_agent(agent_inputs)
        elif agent_name == "background":
            results["background"] = background_agent(agent_inputs)

    # 4. Final Assembly
    print("Assembling final script and rendering...")
    final_script_path = os.path.join(args.out_dir, "final_scene.py")
    result_img = os.path.join(args.out_dir, "result_render.png")
    
    # Start with the initial code
    final_code_segments = [get_key_from_file(args.init_script)]
    
    # Collect code from agents that use APPEND mode (Material, Lighting, etc.)
    for agent_name in ["materials", "lighting", "camera", "background"]:
        if agent_name in results and results[agent_name].get("suggested_code"):
            final_code_segments.append(f"# --- {agent_name} code ---")
            final_code_segments.append(results[agent_name]["suggested_code"])
            
    # Combine and save to a temporary file
    temp_combined_script = code_to_file(final_code_segments)
    
    # Apply modifications from 'modder' which usually edits existing lines
    if "modder" in results and results["modder"].get("suggested_code"):
        final_code = apply_suggested_code(results["modder"]["suggested_code"], temp_combined_script)
    else:
        final_code = get_key_from_file(temp_combined_script)
        
    with open(final_script_path, "w", encoding="utf-8") as f:
        f.write(final_code)
    
    # 5. Final Render
    print(f"Rendering final result to: {result_img}")
    render_result = run_blender(args.blender_exe, args.scene_blend, final_script_path, args.render_script, result_img)
    
    if not render_result.get('status'):
        print("❌ Initial final rendering failed! Attempting automatic debug...")
        # Simple Debug Loop: Try to fix failed agent code
        error_log = render_result.get('stdout', '') + render_result.get('stderr', '')
        
        fixed_code_segments = [get_key_from_file(args.init_script)]
        for agent_name in ["materials", "lighting", "camera", "background"]:
            if agent_name in results and results[agent_name].get("suggested_code"):
                print(f"Debugging {agent_name}...")
                debug_inputs = {
                    "client": client, "model": model, "name": agent_name,
                    "code": results[agent_name]["suggested_code"],
                    "error_log": error_log, "master_prompt": f"Initial Script Context:\n{get_key_from_file(args.init_script)}\n\nUser Task: {args.prompt}"
                }
                debug_reply = debug_agent(debug_inputs)
                fixed_code_segments.append(f"# --- {agent_name} fixed code ---")
                fixed_code_segments.append(debug_reply.get("suggested_code", results[agent_name]["suggested_code"]))
        
        # Re-assemble
        temp_combined_script = code_to_file(fixed_code_segments)
        if "modder" in results and results["modder"].get("suggested_code"):
            final_code = apply_suggested_code(results["modder"]["suggested_code"], temp_combined_script)
        else:
            final_code = get_key_from_file(temp_combined_script)
            
        with open(final_script_path, "w", encoding="utf-8") as f:
            f.write(final_code)
            
        print("Retrying final render after debug...")
        render_result = run_blender(args.blender_exe, args.scene_blend, final_script_path, args.render_script, result_img)

    if render_result.get('status'):
        print(f"✅ Final rendering successful: {result_img}")
    else:
        print("❌ Rendering still fails after debug. Manual check required.")
        if 'stdout' in render_result: print(f"STDOUT: {render_result['stdout'][-500:]}")
    
    print("Workflow completed. Results saved to", args.out_dir)

if __name__ == "__main__":
    main()
