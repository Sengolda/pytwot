from typing import Dict, Any

class ApplicationInfo:
    """Represents an application's info.
    
    """
    def __init__(self, data: Dict[str, Any]):
        app_id = self.original_payload.get("apps").keys[0]
        self.original_payload = data
        self._payload = self.original_payload.get(app_id)

    @property
    def name(self) -> str:
        return self._payload.get("name")

    @property
    def id(self) -> int:
        return int(self._payload.get("id"))

    @property
    def url(self) -> str:
        return self._payload.get("url")