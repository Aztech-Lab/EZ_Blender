import os
from concurrent.futures import ThreadPoolExecutor
from .utils import (
    init_client, run_blender, ensure_dir, get_key_from_file, 
    code_to_file, apply_suggested_code
)
from ..agents import (
    planner_agent, modder_agent, material_agent, 
    lighting_agent, camera_agent, background_agent, debug_agent
)

class EZBlenderWorkflow:
    def __init__(self, args):
        self.args = args
        self.client = None
        self.model = args.model
        self.results = {}
        self.init_img = None
        self.final_script = None
        self.result_img = None

    def initialize(self):
        """Phase 1: Setup environment and client"""
        ensure_dir(self.args.out_dir)
        print(f"[*] Initializing workflow with model: {self.model}")
        try:
            with open("creds/openai.txt", "r") as f:
                key = f.read().strip()
            self.client = init_client(api_key=key)
            return True
        except Exception as e:
            print(f"❌ Initialization Error: {e}")
            return False

    def run_initial_render(self):
        """Phase 2: Initial Render"""
        self.init_img = os.path.join(self.args.out_dir, "init_render.png")
        print(f"[*] Capturing initial state: {self.init_img}")
        run_blender(self.args.blender_exe, self.args.scene_blend, 
                    self.args.init_script, self.args.render_script, self.init_img)
        return self.init_img

    def plan(self):
        """Phase 3: Generate plan"""
        print("[*] Generating execution plan...")
        planner_inputs = {
            "client": self.client, "model": self.model, "prompt": self.args.prompt,
            "file": get_key_from_file(self.args.init_script), "image": self.init_img
        }
        try:
            plan = planner_agent(planner_inputs)
            self.tasks = plan.get("tasks", {})
            return self.tasks
        except Exception as e:
            print(f"❌ Planning Error: {e}")
            return {}

    def _call_agent(self, agent_name, task_desc):
        """Internal helper to call a single agent"""
        print(f"[*] Starting {agent_name} Agent...")
        agent_inputs = {
            "client": self.client, "model": self.model, "prompt": task_desc,
            "file": get_key_from_file(self.args.init_script), "image": self.init_img
        }
        if agent_name == "modder": return agent_name, modder_agent(agent_inputs)
        if agent_name == "materials": return agent_name, material_agent(agent_inputs)
        if agent_name == "lighting": return agent_name, lighting_agent(agent_inputs)
        if agent_name == "background": return agent_name, background_agent(agent_inputs)
        return None, None

    def execute_sequential(self):
        """Classic sequential execution logic"""
        for name, desc in self.tasks.items():
            if not desc: continue
            name, res = self._call_agent(name, desc)
            if name: self.results[name] = res

    def execute_parallel(self):
        """New multi-threaded execution logic"""
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._call_agent, name, desc) 
                       for name, desc in self.tasks.items() if desc]
            for future in futures:
                name, res = future.result()
                if name: self.results[name] = res

    def assemble_and_render(self):
        """Phase 5: Final code assembly and rendering"""
        print("[*] Assembling final script...")
        self.final_script = os.path.join(self.args.out_dir, "final_scene.py")
        self.result_img = os.path.join(self.args.out_dir, "result_render.png")
        
        code_segments = [get_key_from_file(self.args.init_script)]
        for name in ["materials", "lighting", "background"]:
            if name in self.results and self.results[name].get("suggested_code"):
                code_segments.append(f"# --- {name} code ---")
                code_segments.append(results[name]["suggested_code"])
        
        temp_combined = code_to_file(code_segments)
        if "modder" in self.results and self.results["modder"].get("suggested_code"):
            final_code = apply_suggested_code(self.results["modder"]["suggested_code"], temp_combined)
        else:
            final_code = get_key_from_file(temp_combined)
            
        with open(self.final_script, "w", encoding="utf-8") as f:
            f.write(final_code)
            
        print(f"[*] Rendering result to: {self.result_img}")
        return run_blender(self.args.blender_exe, self.args.scene_blend, 
                           self.final_script, self.args.render_script, self.result_img)

    def auto_debug(self, last_result):
        """Phase 6: Context-aware auto debug"""
        print("❌ Rendering failed! Attempting automatic debug...")
        error_log = last_result.get('stdout', '') + last_result.get('stderr', '')
        script_context = get_key_from_file(self.args.init_script)
        
        fixed_code_segments = [get_key_from_file(self.args.init_script)]
        for name, res in self.results.items():
            if name == "modder" or not res.get("suggested_code"): continue
            print(f"[*] Debugging {name}...")
            debug_inputs = {
                "client": self.client, "model": self.model, "name": name,
                "code": res["suggested_code"], "error_log": error_log, 
                "master_prompt": f"Context:\n{script_context}\n\nTask: {self.args.prompt}"
            }
            debug_reply = debug_agent(debug_inputs)
            fixed_code_segments.append(f"# --- {name} fixed code ---")
            fixed_code_segments.append(debug_reply.get("suggested_code", res["suggested_code"]))
            
        temp = code_to_file(fixed_code_segments)
        final_code = apply_suggested_code(self.results.get("modder", {}).get("suggested_code", ""), temp)
        
        with open(self.final_script, "w", encoding="utf-8") as f:
            f.write(final_code)
            
        print("[*] Retrying after debug...")
        return run_blender(self.args.blender_exe, self.args.scene_blend, 
                           self.final_script, self.args.render_script, self.result_img)
