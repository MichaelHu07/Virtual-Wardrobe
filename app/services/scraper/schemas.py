from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl

class NormalizedProduct(BaseModel):
    name: str
    url: HttpUrl
    brand: Optional[str] = None
    images: List[HttpUrl]
    material: Optional[str] = None
    size_chart: Optional[Dict[str, Any]] = None
    stretchiness_score: Optional[float] = None # 0.0 to 1.0
    normalized_sizes: List[str] = [] # e.g. ["S", "M", "L"]
    meta_data: Dict[str, Any] = {}

