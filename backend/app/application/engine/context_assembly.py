from typing import List, Dict, Any, Tuple
from app.domain.search import SearchResultItem
from app.domain.engine import Citation

class ContextAssemblyService:
    async def assemble_context(
        self, 
        items: List[SearchResultItem], 
        token_budget: int = 4000
    ) -> Tuple[str, List[Citation]]:
        assembled_parts = []
        citations = []
        current_len = 0

        for i, item in enumerate(items):
            asset_id = item.metadata.get("asset_id", "unknown")
            asset_name = item.title
            
            # Format context chunk snippet
            snippet = f"Source {i+1}: [{asset_name}]\n{item.description}\n"
            chunk_len = len(snippet)
            
            if current_len + chunk_len > token_budget:
                break
                
            assembled_parts.append(snippet)
            current_len += chunk_len

            # Create citation object mapping
            citations.append(Citation(
                id=f"cit_{i+1}",
                asset_id=asset_id,
                asset_name=asset_name,
                snippet=item.description,
                confidence_score=item.score
            ))

        context_string = "\n".join(assembled_parts) if assembled_parts else "No relevant documents found in workspace context."
        return context_string, citations
