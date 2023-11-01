from datetime import datetime
from sqlalchemy import Table, Boolean, Column, ForeignKey, Integer, String, DateTime, VARBINARY
from sqlalchemy.orm import relationship

from .database import Base

class UserCredentials(Base):
    __tablename__ = "UserCredentials"

    user_id = Column(Integer, primary_key=True, index=True)
    #user_password= Column(String)
    user_email = Column(String, unique=True, index=True)
    user_salt = Column(VARBINARY(16))
    user_hashpassword = Column(String)
    created_datetime = Column(DateTime, default=datetime.utcnow)
    updated_datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lastlogin_datetime = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)

    # Define the relationship from UserCredentials to ChatHistory
    chats = relationship("ChatHistory", back_populates="owner")

class ChatHistory(Base):
    __tablename__ = "ChatHistory"

    chat_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("UserCredentials.user_id"))
    user_question = Column(String, index=True)
    system_answer = Column(String, index=True)
    created_datetime = Column(DateTime, default=datetime.utcnow)

    # Define the relationship from ChatHistory to UserCredentials
    owner = relationship("UserCredentials", back_populates="chats")
    
class Reference(Base):
    __tablename__="Reference"
    
    id = Column(Integer, primary_key=True, index=True)
    form_title = Column(String, index=True)
    created_datetime = Column(DateTime, default=datetime.utcnow)
    
