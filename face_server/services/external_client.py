import requests
import os

class ExternalClient:
    def __init__(self, base_url=None):
        # Default to localhost:8080 if not provided or in env
        self.base_url = base_url or os.getenv("REST_SERVER_URL", "http://localhost:8080")

    def get_group_embeddings(self, group_id):
        """
        Fetches embeddings for a specific group.
        Expected endpoint: GET /group/{group_id}/recognize
        Expected response: JSON list of objects [{ "id": "...", "embedding": [...] }, ...] 
                           OR list of embeddings.
        """
        try:
            url = f"{self.base_url}/group/{group_id}/recognize"
            # timeout is important to avoid hanging
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching group embeddings: {e}")
            return []
