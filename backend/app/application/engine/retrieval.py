from typing import List
from app.domain.engine import QueryPlan
from app.domain.search import SearchResultItem
from app.domain.repositories import IAssetRepository

class RetrievalService:
    def __init__(self, asset_repo: IAssetRepository):
        self.asset_repo = asset_repo

    async def retrieve_knowledge(self, plan: QueryPlan) -> List[SearchResultItem]:
        # 1. Fetch all assets for the workspace
        all_assets = await self.asset_repo.list_assets(
            ws_id=plan.workspace_id,
            folder_id=None,
            asset_type=None
        )

        results: List[SearchResultItem] = []
        import string
        clean_query = plan.original_query.translate(str.maketrans("", "", string.punctuation))
        query_words = clean_query.lower().split()

        for asset in all_assets:
            # Enforce project/collection boundary constraints if passed in plan filters
            if plan.project_id and asset.project_id != plan.project_id:
                continue
            if plan.collection_id and asset.collection_id != plan.collection_id:
                continue

            # Calculate match score based on title and descriptions
            match_score = 0.0
            name_lower = asset.name.lower()
            
            # Substring match boost
            if plan.original_query.lower() in name_lower:
                match_score += 0.5

            # Word match checks
            matches = 0
            for word in query_words:
                if word in name_lower:
                    matches += 1
            if len(query_words) > 0:
                match_score += (matches / len(query_words)) * 0.5

            # Default description
            snippet = f"Document type: {asset.asset_type}. Stage: {asset.processing_stage}."
            if "system_metadata" in asset.details:
                size = asset.details["system_metadata"].get("size_bytes", 0)
                snippet += f" Size: {size} bytes."
            if "document_metadata" in asset.details:
                lang = asset.details["document_metadata"].get("language", "en")
                snippet += f" Language: {lang}."

            if match_score > 0.0:
                results.append(SearchResultItem(
                    title=asset.name,
                    item_type="document",
                    score=min(match_score, 1.0),
                    description=snippet,
                    redirect_url=f"/documents?asset={asset.id}",
                    metadata={
                        "asset_id": asset.id,
                        "workspace_id": asset.workspace_id,
                        "checksum": asset.checksum,
                        "details": asset.details
                    }
                ))

        # Sort results by match score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results
