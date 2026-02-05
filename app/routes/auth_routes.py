from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user_schema import UserCreate, UserOut
from app.models.user import User
from app.db.crud import create_user, get_user_by_email
from app.core.security import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Register ---
@router.post("/auth/register", response_model=UserOut)
async def register(user: UserCreate):
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    user_obj = User(email=user.email, hashed_password=hashed_pw)
    created_user = await create_user(user_obj)
    return UserOut(id=str(created_user.id), email=created_user.email, is_active=created_user.is_active)


# --- Login ---
@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
