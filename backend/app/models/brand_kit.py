from dataclasses import dataclass
from typing import Optional


@dataclass
class BrandKit:
    """Represents a generated brand identity package."""

    brand_names: list[str]
    tagline: str
    description: str
    visual_identity: dict
    logo_concept: Optional[str]
    marketing_content: dict
    target_audience: str
    brand_values: list[str]

    def to_dict(self) -> dict:
        return {
            "brand_names": self.brand_names,
            "tagline": self.tagline,
            "description": self.description,
            "visual_identity": self.visual_identity,
            "logo_concept": self.logo_concept,
            "marketing_content": self.marketing_content,
            "target_audience": self.target_audience,
            "brand_values": self.brand_values,
        }
