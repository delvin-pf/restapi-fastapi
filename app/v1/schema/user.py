import re

from pydantic import BaseModel, validator, Field, StrictStr


example_jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'


class TokenResponse(BaseModel):
    access_token: str = Field(example=example_jwt)
    token_type: str = Field(example='bearer')


class UserResponse(BaseModel):
    id: int = Field(example=10)
    name: str = Field(example='Jhon Doe')
    

class UserCreate(BaseModel):
    name: StrictStr = Field(title='User name', min_length=5, example='Jhon Doe', strict=True)
    email: StrictStr = Field(title='User email', min_length=5, example='jhondoe@email.com')
    password: str = Field(title='User password', min_length=6, example='1a2b3c')
    isVendor: bool = Field(title='User is vendor?', example=True)
    
    @validator('email')
    def email_must_valid_email(cls, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            raise ValueError('"email" must be a valid email address')
        return email

