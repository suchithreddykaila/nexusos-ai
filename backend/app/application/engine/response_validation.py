import re
from typing import List
from app.domain.engine import Citation, EngineResponse

class ResponseValidationService:
    async def validate_response(self, response: EngineResponse) -> EngineResponse:
        # Check if LLM response mentions inline citation tags that actually exist
        mentioned_tags = re.findall(r"\[(cit_\d+)\]", response.response_text)
        
        # Filter down citations to only ones that were actually referenced in the response
        valid_citations = [cit for cit in response.citations if cit.id in mentioned_tags]
        
        # If the LLM returned mentions but no citations are loaded, flag validation issue
        if mentioned_tags and not valid_citations:
            logger_message = "Citations misalignment: inline citations mentioned but no matching sources found."
            response.validated = False

        response.citations = valid_citations
        return response
