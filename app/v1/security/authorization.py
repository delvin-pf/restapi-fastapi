import os
from dotenv import load_dotenv
from datetime import timedelta, datetime

from fastapi import HTTPException, status
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')


class JWTAuthorization:

	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail='Could not validate credentials'
	)
	SECRET_KEY = os.environ.get('SECRET_KEY')
	ALGORITHM = os.environ.get('ALGORITHM')

	@classmethod
	def create_access_token(cls, data: dict):
		"""Create JWT token\n
		:param dict data: data to encode in JWT
		:rtype: str
		:return: JWT token"""

		to_encode = data.copy()
		expire = datetime.utcnow() + timedelta(minutes=120)
		to_encode.update({'exp': expire})
		encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
		return encoded_jwt

	@classmethod
	def verify_token(cls, token):
		"""Verify if token is valid\n
		:param str token: JWT token
		:rtype: dict
		:return: dictionary with token data"""
		
		if not token:
			raise cls.credentials_exception
		try:
			payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
			u_id = payload.get('id')
			u_name = payload.get('name')
			u_email = payload.get('email')
			u_isVendor = payload.get('isVendor')
			
			if not u_id or not u_name or not u_email:
				raise cls.credentials_exception
			user: dict = {
				'id': u_id,
				'name': u_name,
				'email': u_email,
				'isVendor': u_isVendor
			}
		except JWTError:
			raise cls.credentials_exception
		return user


