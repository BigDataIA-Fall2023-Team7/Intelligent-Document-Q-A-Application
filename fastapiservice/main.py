from fastapi.responses import JSONResponse
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from . import crud, models, schemas
from .schemas import UserLoginRequest 
from .database import SessionLocal, engine
from fastapi import Query
#from jose import JWTError
from .jwt_utils import create_access_token, verify_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import VectorDatabaseStats

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/')
def info():
    return JSONResponse(content={'message':'API is working'}, status_code=200)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.UserCredentialsResponse)
def register_user(user: schemas.UserCredentialsCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_credentials_by_email(db, user_email=user.user_email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")

    created_user = crud.create_user_credentials(db=db, user=user)
    return created_user

@app.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = crud.get_user_credentials_by_email(db, user_email=form_data.username)
    if db_user is None or not crud.verify_password(form_data.password, db_user.user_salt, db_user.user_hashpassword):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Generate and return a JWT token on successful login
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Create a dependency to get the current user based on the JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(credentials: str = Depends(oauth2_scheme)):
    token_data = verify_token(credentials)
    if token_data is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token_data

@app.get("/chatAnswer", response_model=list[schemas.ChatHistory])
def get_chat_history(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user_email = current_user["sub"]  # Extract user_email from the JWT token

    try:
        db_user = crud.get_user_credentials_by_email(db, user_email)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = db_user.user_id  # Get the user_id from the database

    chat_history = db.query(models.ChatHistory).filter(models.ChatHistory.user_id == user_id).order_by(models.ChatHistory.created_datetime.desc()).all()
    return chat_history


# Add the /showReference endpoint
@app.get("/showReference", response_model=list[schemas.ReferenceItem])
def show_reference(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    reference_data = (
        db.query(models.Reference)
        .with_entities(models.Reference.id, models.Reference.form_title, models.Reference.created_datetime)
        .all()
    )
    return reference_data

@app.get("/pineconeForms",response_model=list[schemas.VectorDatabaseStatsItem])
def get_pinecone_forms(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    response_data = (
        db.query(models.VectorDatabaseStats)
        .with_entities(models.VectorDatabaseStats.form_name, models.VectorDatabaseStats.recent_activity)
        .all()
    )
    return response_data