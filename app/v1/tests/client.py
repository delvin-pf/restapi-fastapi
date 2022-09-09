import os
import sys
sys.path.insert(0, f'{os.getcwd()}')

from app.v1.main import app

from fastapi.testclient import TestClient


client = TestClient(app)
