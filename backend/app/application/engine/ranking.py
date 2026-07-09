from typing import List
from app.domain.search import SearchResultItem

class RankingEngine:
    async def rerank_results(self, items: List[SearchResultItem]) -> List[SearchResultItem]:
        reranked = []
        for item in items:
            score = item.score
            
            # Recency boost placeholder check
            meta = item.metadata
            if meta and "details" in meta:
                details = meta["details"]
                # If chunking or OCR completed, boost confidence rating
                if details.get("pipeline_status", {}).get("status") == "completed":
                    score += 0.1
                # If summary is present, boost priority
                if "ai_metadata" in details:
                    score += 0.05

            item.score = min(score, 1.0)
            reranked.append(item)
            
        # Re-sort
        reranked.sort(key=lambda x: x.score, reverse=True)
        return reranked
