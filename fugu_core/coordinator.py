"""
coordinator.py
Implements the lightweight Coordinator Model (~7B).
Handles prompt decomposition, dynamic role assignment, and recursive self-correction.
"""

import time
from typing import Dict, Any
from .agents import ThinkerAgent, WorkerAgent, VerifierAgent

class Coordinator:
    """
    Central hub for multi-agent orchestration.
    Directs traffic between Thinker, Worker, and Verifier.
    """
    
    def __init__(self, max_retries: int = 3):
        # Setup the agent pool
        # In a real scenario, these would connect to specific APIs or local weights
        self.thinker = ThinkerAgent(model_name="Fugu-Reasoning-Core")
        self.worker = WorkerAgent(model_name="Fugu-Code-Generator")
        self.verifier = VerifierAgent(model_name="Fugu-Critic")
        
        # Maximum number of recursive self-correction loops
        self.max_retries = max_retries

    def orchestrate(self, prompt: str) -> Dict[str, Any]:
        """
        Main orchestration loop based on the Conductor methodology.
        """
        print("[Coordinator] Received prompt. Decomposing tasks...")
        
        iteration = 0
        is_resolved = False
        final_result = ""
        reasoning_tree = []

        while iteration < self.max_retries and not is_resolved:
            iteration += 1
            print(f"\n--- Orchestration Loop: Iteration {iteration} ---")
            
            # Step 1: Think (Planning)
            plan = self.thinker.process(prompt)
            reasoning_tree.append({"step": "think", "output": plan})
            
            # Step 2: Work (Execution)
            draft = self.worker.process(plan)
            reasoning_tree.append({"step": "work", "output": draft})
            
            # Step 3: Verify (Validation & Self-Correction)
            verification_result = self.verifier.process(draft)
            reasoning_tree.append({"step": "verify", "output": verification_result})
            
            if verification_result["is_valid"]:
                print("[Coordinator] Verification passed. Merging context...")
                final_result = verification_result["final_content"]
                is_resolved = True
            else:
                print(f"[Coordinator] Error detected by Verifier: {verification_result['feedback']}")
                print("[Coordinator] Triggering recursive self-correction...")
                # Append feedback to the prompt for the next iteration to fix the error
                prompt = f"Original task: {prompt}\nFeedback to fix: {verification_result['feedback']}"
                time.sleep(1) # Simulate processing delay

        if not is_resolved:
            print("[Coordinator] Warning: Max retries reached without passing verification.")
            final_result = draft # Fallback to the last draft
            
        return {
            "status": "success" if is_resolved else "partial_success",
            "content": final_result,
            "reasoning_tree": reasoning_tree,
            "iterations": iteration
        }
