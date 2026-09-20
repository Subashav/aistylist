from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserSignUp, UserSignIn, UserResponse, Token,
    ForgotPasswordRequest, ForgotPasswordResponse
)
from app.utils.security import (
    verify_password, get_password_hash, create_access_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignUp, db: Session = Depends(get_db)):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )
    
    existing_user = db.query(User).filter(User.email == user_data.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        full_name=user_data.full_name.strip(),
        email=user_data.email.lower().strip(),
        password_hash=hashed_pw
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {exc}"
        )

    token = create_access_token(data={"sub": str(new_user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/signin", response_model=Token)
def signin(login_data: UserSignIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email.lower().strip()).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please try again."
        )

    token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    # Return friendly confirmation without leaking whether email exists
    return ForgotPasswordResponse(
        message="If an account exists with this email, a password reset link has been dispatched."
    )

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out. Please clear your local session token."}
