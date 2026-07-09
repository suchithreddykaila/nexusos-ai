from app.domain.engine import QueryPlan

class QueryUnderstandingService:
    async def analyze_query(
        self, 
        query: str, 
        workspace_id: str, 
        project_id: str = None, 
        collection_id: str = None
    ) -> QueryPlan:
        # Detect basic intent keywords
        query_lower = query.lower()
        if "compare" in query_lower or "difference between" in query_lower:
            intent = "compare"
        elif "summarize" in query_lower or "summary" in query_lower:
            intent = "summarize"
        elif "explain" in query_lower or "what is" in query_lower or "how does" in query_lower:
            intent = "explain"
        elif "translate" in query_lower:
            intent = "translate"
        elif "analyze" in query_lower or "eval" in query_lower:
            intent = "analyze"
        elif "list" in query_lower or "show all" in query_lower:
            intent = "list"
        else:
            intent = "search"

        # Construct filters
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        if collection_id:
            filters["collection_id"] = collection_id

        # Determine strategy
        strategy = "hybrid"
        if len(query.split()) <= 2:
            # Short queries are better suited for keyword searches
            strategy = "keyword"

        return QueryPlan(
            original_query=query,
            intent=intent,
            workspace_id=workspace_id,
            project_id=project_id,
            collection_id=collection_id,
            filters=filters,
            strategy=strategy,
            complexity="compound" if len(query.split()) > 5 else "simple"
        )
