from typing import Any, Dict, List
from app.domain.engine import Citation

class PromptConstructor:
    def build_prompt(
        self, 
        query: str, 
        context_str: str, 
        history: List[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        system_instruction = (
            "You are NexusOS AI, the Enterprise Intelligence Operating System.\n"
            "Answer the user's query utilizing the context details below.\n"
            "CRITICAL: You MUST cite your source facts. Use format [cit_1], [cit_2] inline "
            "where you mention facts from the source context. Do not make up facts. "
            "If the context does not contain the answer, indicate that you are unsure.\n\n"
            f"=== RETRIEVED KNOWLEDGE CONTEXT ===\n{context_str}\n===================================="
        )

        messages = [
            {"role": "system", "content": system_instruction}
        ]

        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": query})
        return messages
