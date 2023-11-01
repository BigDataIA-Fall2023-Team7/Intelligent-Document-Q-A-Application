from pydantic import BaseModel
from datetime import datetime


class UserCredentialsBase(BaseModel):
    user_email: str
    user_password: str
    user_salt: bytes =None
    user_hashpassword: str =None
    # created_datetime: datetime
    # updated_datetime: datetime
    # lastlogin_datetime: datetime | None
    # active: bool

class UserCredentialsResponse(BaseModel):
    user_id: int
    user_email: str
    created_datetime: datetime
    updated_datetime: datetime
    lastlogin_datetime: datetime | None
    active: bool

class UserCredentialsCreate(BaseModel):
    user_email: str
    user_password: str

class UserCredentials(UserCredentialsCreate):
    user_id: int

    class Config:
        orm_mode = True

class UserLoginRequest(BaseModel):
    user_email: str
    user_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatHistoryBase(BaseModel):
    user_id: int
    user_question: str
    system_answer: str
    created_datetime: datetime


class ChatHistoryCreate(ChatHistoryBase):
    pass


class ChatHistory(ChatHistoryBase):
    chat_id: int

    class Config:
        orm_mode = True
        
class ReferenceItem(BaseModel):
    id: int
    form_title: str
    created_datetime: datetime
