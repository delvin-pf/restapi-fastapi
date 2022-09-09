from fastapi import APIRouter, Depends, UploadFile
from fastapi.security import OAuth2PasswordRequestForm as OAuth2

from ..controller.UserController import UserController as UC
from ..schema.user import UserResponse, UserCreate, TokenResponse
from ..security.authorization import oauth2_scheme, JWTAuthorization


router = APIRouter(prefix='/users', tags=['users'])

UserController = UC()


@router.post('/', response_model=UserResponse)
def createUser(body: UserCreate):
	"""Create a new user"""
	return UserController.create(body)


@router.post('/login', response_model=TokenResponse)
def login(form_data: OAuth2 = Depends()):
	return UserController.login(form_data)


@router.post('/photo/{user_id}')
def uploadPhoto(file: UploadFile, token: str = Depends(oauth2_scheme)):
	user = JWTAuthorization.verify_token(token)
	return UserController.image(user, file)
	
