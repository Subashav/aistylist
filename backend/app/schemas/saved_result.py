from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, model_validator
from app.schemas.analysis import ColourSwatch, OutfitSuggestion, PersonalizedStyleAnalysis

class SavedResultCreate(BaseModel):
    clothing_image: str = ""
    user_image: Optional[str] = None
    clothing_type: str = "Garment"
    detected_colour: str = "Detected"
    colour_shade: str = "Shade"
    hex_value: str = "#4169E2"
    rgb_value: str = "65, 105, 226"
    confidence: float = 0.95
    recommendations: List[ColourSwatch] = []
    outfit_suggestions: List[OutfitSuggestion] = []
    explanations: str = ""
    personalized_analysis: Optional[PersonalizedStyleAnalysis] = None

    @model_validator(mode="before")
    @classmethod
    def handle_aliases(cls, data):
        if isinstance(data, dict):
            if "clothing_image_url" in data and not data.get("clothing_image"):
                data["clothing_image"] = data["clothing_image_url"]
            if "user_image_url" in data and not data.get("user_image"):
                data["user_image"] = data["user_image_url"]
            if "recommended_colours" in data and not data.get("recommendations"):
                data["recommendations"] = data["recommended_colours"]
            if "overall_advice" in data and not data.get("explanations"):
                data["explanations"] = data["overall_advice"]
        return data

class SavedResultResponse(BaseModel):
    id: int
    user_id: int
    clothing_image: str
    user_image: Optional[str] = None
    clothing_type: str
    detected_colour: str
    colour_shade: str
    hex_value: str
    rgb_value: str
    confidence: float
    recommendations: List[ColourSwatch]
    outfit_suggestions: List[OutfitSuggestion]
    explanations: str
    personalized_analysis: Optional[PersonalizedStyleAnalysis] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DeleteResponse(BaseModel):
    message: str
    id: int
