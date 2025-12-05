import re
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup

class ContentParser:
    @staticmethod
    def extract_materials(text: str) -> Optional[str]:
        """
        Extracts material composition using regex.
        Matches patterns like "100% Cotton", "50% Polyester / 50% Cotton"
        """
        material_pattern = re.compile(r"(\d{1,3}%\s*[A-Za-z]+(?:(?:\s*[,/]\s*|\s+and\s+)\d{1,3}%\s*[A-Za-z]+)*)", re.IGNORECASE)
        matches = material_pattern.findall(text)
        if matches:
            return ", ".join(sorted(list(set(matches)), key=len, reverse=True))
        return None

    @staticmethod
    def normalize_sizes(raw_sizes: List[str]) -> List[str]:
        """
        Normalizes diverse size strings into standard S/M/L or numeric formats.
        """
        normalized = []
        mapping = {
            "small": "S", "medium": "M", "large": "L", "extra large": "XL",
            "xs": "XS", "xxl": "2XL"
        }
        
        for size in raw_sizes:
            s = size.lower().strip()
            if s in mapping:
                normalized.append(mapping[s])
            elif re.match(r"^[0-9]+$", s):
                normalized.append(s) # Keep numeric sizes as is
            else:
                normalized.append(size.upper()) # Fallback
                
        return list(set(normalized))

    @staticmethod
    def estimate_stretchiness(text: str) -> float:
        """
        Heuristic scoring for stretchiness based on keywords.
        """
        text = text.lower()
        if "spandex" in text or "elastane" in text:
            return 0.8
        if "stretch" in text:
            return 0.6
        if "rigid" in text or "100% cotton" in text:
            return 0.1
        return 0.3 # Default guess

