import os
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.hash import pbkdf2_sha256

# UserCredentials CRUD operations

def get_user_credentials(db: Session, user_id: int):
    return db.query(models.UserCredentials).filter(models.UserCredentials.user_id == user_id).first()

def get_user_credentials_by_email(db: Session, user_email: str):
    return db.query(models.UserCredentials).filter(models.UserCredentials.user_email == user_email).first()

def create_user_credentials(db: Session, user: schemas.UserCredentialsCreate):
    user_salt = os.urandom(16)  # Generate a random salt
    user_hashpassword = pbkdf2_sha256.using(salt=user_salt).hash(user.user_password)

    db_user = models.UserCredentials(user_email=user.user_email, user_salt=user_salt, user_hashpassword=user_hashpassword)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password: str, salt: bytes, hashed_password: str) -> bool:
    return pbkdf2_sha256.using(salt=salt).verify(plain_password, hashed_password)

# ChatHistory CRUD operations

def get_chat_history(db: Session, chat_id: int):
    return db.query(models.ChatHistory).filter(models.ChatHistory.chat_id == chat_id).first()

def get_chat_history_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ChatHistory).filter(models.ChatHistory.user_id == user_id).offset(skip).limit(limit).all()

def create_chat_history(db: Session, chat: schemas.ChatHistoryCreate):
    db_chat = models.ChatHistory(**chat.dict())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat
