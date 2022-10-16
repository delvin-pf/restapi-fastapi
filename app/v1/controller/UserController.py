from dotenv import load_dotenv
from uuid import uuid4

from playhouse.shortcuts import model_to_dict
from fastapi.responses import JSONResponse
from fastapi import status, HTTPException, UploadFile
from passlib.context import CryptContext

from app.v1.model.index import User
from app.v1.security.authorization import JWTAuthorization


load_dotenv()


class UserController:

	def __init__(self):
		self.include = [User.id, User.name, User.email, User.photo, User.isVendor]
		self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
		self.static_path = 'static'

	def store(self):
		users = list(User.select(*self.include).dicts())
		return JSONResponse(status_code=status.HTTP_200_OK, content=users)

	def login(self, form_data):
		"""Confirm user data and return JWT token if success\n
		:param form_data: form to log in"""
		
		user = self.__authenticate_user(form_data.username, form_data.password)
		if not user:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail='Incorrect username or password',
				headers={'WWW-Authenticate': 'Bearer'}
			)

		access_token = JWTAuthorization.create_access_token(data={
				'id': user.id,
				'name': user.name,
				'email': user.email,
				'isVendor': user.isVendor
			})
		return JSONResponse(status_code=200, content={
				'access_token': access_token,
				'token_type': 'bearer'
			})

	def create(self, body):
		user = User.get_or_none(User.email == body.email)
		if user:
			return JSONResponse(status_code=400, content={
				'error': 'user already exists'
			})
		passwordHash = self.pwd_context.hash(body.password.encode('utf-8'))
		
		user = User.create(
			name=body.name,
			email=body.email,
			passwordHash=passwordHash,
			isVendor=body.isVendor
		)
		return JSONResponse(status_code=status.HTTP_201_CREATED, content=model_to_dict(user, only=self.include))
	
	def image(self, user: dict, file: UploadFile):
		if not file:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='file is required')
		user = User.get_or_none(User.id == user['id'])
		if not user:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='user no exists')
		
		file_extension = file.filename.split('.')[-1]
		file_name = f'{str(uuid4().hex)}.{file_extension}'
		
		with open(fr'{self.static_path}/{file_name}', 'wb') as f:
			f.write(file.file.read())
			
		user.photo = file_name
		user.save()
		
		return JSONResponse(status_code=status.HTTP_200_OK, content={
			'file_name': file_name
		})
	
	def avaliate(self, user: dict, u_id: int, score: int):
		user = User.get_or_none(User.id == u_id)
		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
		
		new_score = ((user.score * user.ratings) + score) / (user.ratings + 1)
		user.score = new_score
		user.ratings = user.ratings + 1
		user.save()
		
		return JSONResponse(status_code=status.HTTP_200_OK, content={'score': new_score})
		
	def __authenticate_user(self, username: str, password: str):
		"""Verify if user exists and verify password\n
		:param str username: login username
		:param str password: login password
		:rtype: User | bool
		:return: User instanse if is authenticated, else False"""

		user = User.get_or_none(User.email == username)
		if not user:
			return False
		if not self.__verify_password(password, user.passwordHash):
			return False
		return user

	def __verify_password(self, plain_password, hashed_password):
		"""Compare input password with password in DB\n
		:param str plain_password: user password
		:param str hashed_password: user passwordHash in DB
		:rtype: bool
		:return: 'True' if password is correct, 'False' if wrong"""
		return self.pwd_context.verify(plain_password, hashed_password)
