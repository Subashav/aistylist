import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.saved_result import SavedResult
from app.schemas.saved_result import SavedResultCreate, SavedResultResponse, DeleteResponse
from app.schemas.analysis import ColourSwatch, OutfitSuggestion, PersonalizedStyleAnalysis
from app.utils.security import get_current_user

router = APIRouter(prefix="/saved-results", tags=["Saved Results"])

def serialize_item(item: SavedResult) -> SavedResultResponse:
    try:
        recs_data = json.loads(item.recommendations)
    except Exception:
        recs_data = []
    try:
        outfits_data = json.loads(item.outfit_suggestions)
    except Exception:
        outfits_data = []

    pers_analysis = None
    if getattr(item, "personalized_analysis", None):
        try:
            pers_dict = json.loads(item.personalized_analysis)
            pers_analysis = PersonalizedStyleAnalysis(**pers_dict)
        except Exception:
            pers_analysis = None

    return SavedResultResponse(
        id=item.id,
        user_id=item.user_id,
        clothing_image=item.clothing_image,
        user_image=item.user_image,
        clothing_type=item.clothing_type,
        detected_colour=item.detected_colour,
        colour_shade=item.colour_shade,
        hex_value=item.hex_value,
        rgb_value=item.rgb_value,
        confidence=item.confidence,
        recommendations=[ColourSwatch(**s) for s in recs_data],
        outfit_suggestions=[OutfitSuggestion(**o) for o in outfits_data],
        explanations=item.explanations,
        personalized_analysis=pers_analysis,
        created_at=item.created_at
    )

@router.post("", response_model=SavedResultResponse, status_code=status.HTTP_201_CREATED)
def save_result(
    payload: SavedResultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recs_json = json.dumps([s.model_dump() for s in payload.recommendations])
    outfits_json = json.dumps([o.model_dump() for o in payload.outfit_suggestions])
    pers_json = json.dumps(payload.personalized_analysis.model_dump()) if payload.personalized_analysis else None
    
    new_record = SavedResult(
        user_id=current_user.id,
        clothing_image=payload.clothing_image,
        user_image=payload.user_image,
        clothing_type=payload.clothing_type,
        detected_colour=payload.detected_colour,
        colour_shade=payload.colour_shade,
        hex_value=payload.hex_value,
        rgb_value=payload.rgb_value,
        confidence=payload.confidence,
        recommendations=recs_json,
        outfit_suggestions=outfits_json,
        explanations=payload.explanations,
        personalized_analysis=pers_json,
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return serialize_item(new_record)

@router.get("", response_model=List[SavedResultResponse])
def get_user_saved_results(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = (
        db.query(SavedResult)
        .filter(SavedResult.user_id == current_user.id)
        .order_by(SavedResult.created_at.desc())
        .all()
    )
    return [serialize_item(i) for i in items]

@router.get("/{result_id}", response_model=SavedResultResponse)
def get_single_saved_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = (
        db.query(SavedResult)
        .filter(SavedResult.id == result_id, SavedResult.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved recommendation not found."
        )
    return serialize_item(item)

@router.delete("/{result_id}", response_model=DeleteResponse)
def delete_saved_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = (
        db.query(SavedResult)
        .filter(SavedResult.id == result_id, SavedResult.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved recommendation not found."
        )
    db.delete(item)
    db.commit()
    return DeleteResponse(message="Saved recommendation deleted successfully.", id=result_id)
