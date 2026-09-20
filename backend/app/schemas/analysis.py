from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, model_validator

class ColourSwatch(BaseModel):
    name: str
    hex: str
    rgb: str
    harmony_type: str
    reason: str

class OutfitSuggestion(BaseModel):
    look_id: int = 1
    title: str
    style: Optional[str] = "Clean casual"
    occasion: Optional[str] = "Everyday"
    top: Optional[str] = ""
    top_detail: Optional[Dict[str, Any]] = None
    bottom: Union[Dict[str, Any], str]
    shoes: Union[Dict[str, Any], str]
    layer: Optional[Union[Dict[str, Any], str]] = None
    accessories: Union[List[str], str] = []
    fabric_harmony: Optional[str] = None
    palette: Optional[List[Dict[str, str]]] = None
    explanation: str
    # Virtual Try-On image URLs
    try_on_image_url: Optional[str] = None
    image_url: Optional[str] = None
    # User-specific reason explaining why this look works for this individual
    personalization_reason: Optional[str] = None
    # Try-On Type: "actual_try_on" | "outfit_guide" | "outfit_preview" | "unavailable"
    result_type: Optional[str] = "actual_try_on"
    try_on_type: Optional[str] = "actual_try_on"
    provider: Optional[str] = "fashn_vton_local"

    @model_validator(mode="after")
    def sync_image_urls(self):
        if self.image_url and not self.try_on_image_url:
            self.try_on_image_url = self.image_url
        elif self.try_on_image_url and not self.image_url:
            self.image_url = self.try_on_image_url
        return self

class PersonalizedStyleAnalysis(BaseModel):
    garment_summary: str
    how_it_works_with_you: str
    complexion_harmony: Optional[str] = None
    silhouette_advice: Optional[str] = None
    recommended_looks_count: int = 4
    try_on_status: str = "actual_try_on"  # "actual_try_on" | "outfit_preview" | "unavailable"
    validation_message: Optional[str] = None

class VirtualTryOnResponse(BaseModel):
    success: bool
    result_type: str = "actual_try_on"  # "actual_try_on" | "outfit_preview" | "unavailable"
    image_url: Optional[str] = None
    provider: str = "fashn_vton_local"
    category: Optional[str] = None
    look: Optional[dict] = None
    error_code: Optional[str] = None
    message: Optional[str] = None

class SystemDiagnosticsResponse(BaseModel):
    gpu_available: bool
    gpu_name: Optional[str] = None
    vram_total_mb: Optional[int] = None
    vram_available_mb: Optional[int] = None
    gemini_configured: bool
    vton_configured: bool
    vton_model: str = "FASHN VTON v1.5"
    vton_ready: bool



class AnalysisResponse(BaseModel):
    clothing_type: str
    detected_colour: str
    colour_shade: str
    hex_value: str
    rgb_value: str
    confidence: float
    is_low_confidence: bool = False
    clothing_image_url: str
    user_image_url: Optional[str] = None
    recommended_colours: List[ColourSwatch]
    outfit_suggestions: List[OutfitSuggestion]
    overall_advice: str
    # Personalized Try-On and styling analysis
    personalized_analysis: Optional[PersonalizedStyleAnalysis] = None
    user_attributes: Optional[dict] = None
    try_on_available: bool = True

