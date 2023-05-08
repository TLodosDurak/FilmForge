from typing import List, Dict
from langchain.utilities.google_search import GoogleSearchAPIWrapper

class CustomGoogleSearchAPIWrapper(GoogleSearchAPIWrapper):
    def search_media(self, query: str, search_type: str = "image", num_results: int = 1) -> List[Dict]:
        """Run query through GoogleSearch and return media search results."""
        results = self._google_search_results(query, searchType=search_type, num=num_results)
        return results
