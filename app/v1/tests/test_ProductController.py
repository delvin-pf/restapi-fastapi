from io import StringIO

from pytest import fixture

from client import client
from app.v1.schema.product import ProductResponse, ProductFullResponse





class TestGetProducts:
	def test_get_products(self):
		response = client.get('/products?page=1')
		data = response.json()
		
		assert response.status_code == 200
		assert ProductResponse.parse_obj(data[0])
		assert len(data) <= 10
	
	def test_error_in_get_products(self):
		response = client.get('/products')
		assert response.status_code >= 400


class TestGetByID:
	def test_get_product_by_id(self):
		response = client.get('products/1')
		res_dict = response.json()
		
		assert ProductFullResponse.parse_obj(res_dict)
		assert response.status_code == 200
	
	def test_error_get_product_by_id(self):
		response = client.get('products/a')
		
		assert response.status_code >= 400


class TestSearch:
	url = '/products/search'
	
	def test_get_by_word(self):
		word = 'sham'
		response = client.get(f'{self.url}?word={word}&page=1')
		
		for data in response.json():
			name = data['name'].lower()
			
			assert word in name
	
	def test_error_get_by_word(self):
		"""Teste with length of query < 3"""
		response = client.get(f'{self.url}?word=sh&page=1')
		
		assert response.status_code == 422


product_id = StringIO()
token_str = StringIO()


class TestCreate:
	url = '/products'
	data = {
		'name': 'Shampoo 14',
		'description': 'Shampoo description',
		'price': 15.10,
		'stock': 300,
		'minStock': 20,
		'isAvaliable': True,
		'categories': [1, 2]
	}
	
	@fixture()
	def get_jwt(self) -> str:
		response = client.post('/users/login', data={
			'username': 'delvin7@gmail.com',
			'password': '123456'
		})
		return response.json()['access_token']
	
	def test_create_product(self, get_jwt):
		token = get_jwt
		header = {'Authorization': f'Bearer {token}'}
		response = client.post(self.url, json=self.data, headers=header)
		data = response.json()
	
		product_id.write(str(data['id']))
		token_str.write(token)
		
		assert response.status_code == 201
		assert ProductResponse.parse_obj(data)
		assert 'id' in data
		
	def test_error_create_product(self):
		"""Try to create product with error"""
		token = f'Bearer {token_str.getvalue()}'
		header = {'Authorization': token}
		
		data = self.data
		del data['categories']
		# without categories field
		response = client.post(self.url, json=data, headers=header)
		assert response.status_code == 422
		
		data = self.data
		data['categories'] = 2
		# category as integer
		response = client.post(self.url, json=data, headers=header)
		assert response.status_code == 422
		
		data = self.data
		data['name'] = '1000'
		# with name as a number into string
		response = client.post(self.url, json=data, headers=header)
		assert response.status_code == 422
		
		data = self.data
		data['name'] = 'Al'
		# with name's length < 3
		response = client.post(self.url, json=data, headers=header)
		assert response.status_code == 422


class TestImage:
	def test_try_get_uniexisted_image(self):
		_id = int(product_id.getvalue())
		response = client.get(f'products/{_id}/image')
		
		assert response.status_code == 422
		assert 'No image' in response.json()['detail']
		
	def test_add_image(self):
		_id = int(product_id.getvalue())
		token = token_str.getvalue()
		file = {'file': open(
			r'C:\Users\Delvin e Carol\Projects\PYTHON\FAST_API\app\ef8988884cc742fe9bf835209c3e7919-05092022173012.jpg',
			'rb'
		)}
		headers = {'Authorization': f'Bearer {token}'}
		response = client.post(f'products/{_id}/image', files=file, headers=headers)
		
		assert response.status_code == 204
		
	def test_get_image(self):
		_id = int(product_id.getvalue())
		response = client.get(f'products/{_id}/image')
		
		assert response.status_code == 200
		assert 'image' in response.headers['content-type']
		

class TestUpdate:
	url = '/products'
	categories = {'categories': [1, 2]}
	values = {
		'name': 'Shampoo',
		'description': 'Head Shampoo',
		'price': 10,
		'stock': 200,
		'minStock': 20,
		'isAvaliable': True,
	}
	
	def test_unique_value(self):
		_id = int(product_id.getvalue())
		header = {'Authorization': f'Bearer {token_str.getvalue()}'}
		response = client.put(f'{self.url}/{_id}', json=self.categories, headers=header)
		assert response.status_code == 204
	
	def test_various_values(self):
		_id = int(product_id.getvalue())
		header = {'Authorization': f'Bearer {token_str.getvalue()}'}
		response = client.put(f'{self.url}/{_id}', json=self.values, headers=header)
		assert response.status_code == 204
	
	def test_full_values(self):
		_id = int(product_id.getvalue())
		header = {'Authorization': f'Bearer {token_str.getvalue()}'}
		values = {**self.values, **self.categories}
		response = client.put(f'{self.url}/{_id}', json=values, headers=header)
		assert response.status_code == 204
	
	def test_without_values(self):
		_id = int(product_id.getvalue())
		header = {'Authorization': f'Bearer {token_str.getvalue()}'}
		response = client.put(f'{self.url}/{_id}', json=None, headers=header)
		assert response.status_code == 422


class TestDelete:
	url = '/products'
	
	def test_delete(self):
		_id = int(product_id.getvalue())
		header = {'Authorization': f'Bearer {token_str.getvalue()}'}
		
		response = client.delete(f'{self.url}/{_id}', headers=header)
		assert response.status_code == 204
	
	def test_try_delete_unexistent_product(self):
		_id = int(product_id.getvalue())
		header = {'Authorization': f'Bearer {token_str.getvalue()}'}
		
		response = client.delete(f'{self.url}/{_id}', headers=header)
		assert response.status_code == 400
		assert response.json() == {"detail": "product not found"}
