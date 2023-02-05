from src.session import Session, engine
from src.models.model import Base
from src.main import app
from datetime import datetime
from src.commands.signup_specialist import SignupSpecialist
from sqlalchemy.orm import close_all_sessions
import json
import string
import random

class TestUserRoutes():
  SPECIALIST_NAME = "Pedro"
  SPECIALIST_EMAIL = "Pedro Cabra"
  SPECIALIST_CITY = "Buenos Aires"
  SPECIALIST_PHONE = "11123333"
  SPECIALIST_PASSWORD = "123456"
  SPECIALIST_SPECIALTY = "Cardiology"
  BASE_PATH = '/specialist'
  letters = string.ascii_lowercase

  def setup_method(self):
    Base.metadata.create_all(engine)
    self.session = Session()

  def test_create_specialist(self):
    with app.test_client() as test_client:
      response = test_client.post(
        self.BASE_PATH, json={
          'name': self.SPECIALIST_NAME,
          'email': self.SPECIALIST_EMAIL,
          'birth_day': datetime.now().date().isoformat(),
          'city': self.SPECIALIST_CITY,
          'phone': self.SPECIALIST_PHONE,
          'password': self.SPECIALIST_PASSWORD,
          "specialty": self.SPECIALIST_SPECIALTY
        }
      )
      response_json = json.loads(response.data)
      assert response.status_code == 201
      assert 'name' in response_json
      assert 'email' in response_json
      assert 'token' in response_json
      assert 'password' not in response_json

  def test_create_user_missing_fields(self):
    with app.test_client() as test_client:
      response = test_client.post(
        self.BASE_PATH, json={}
      )
      assert response.status_code == 400

  def test_create_existing_email(self):
    data = {
      "name": self.SPECIALIST_NAME,
          'email': self.SPECIALIST_EMAIL,
          'birth_day': datetime.now().date().isoformat(),
          'city': self.SPECIALIST_CITY,
          'phone': self.SPECIALIST_PHONE,
          'password': self.SPECIALIST_PASSWORD,
          "specialty": self.SPECIALIST_SPECIALTY
    }
    SignupSpecialist(data.copy()).execute()

    with app.test_client() as test_client:
      response = test_client.post(
        self.BASE_PATH, json=data
      )
      assert response.status_code == 412
  
  def test_login_specialist(self):
    signup_data = {
      'name': self.SPECIALIST_NAME,
      'email': self.SPECIALIST_EMAIL,
      'birth_day': datetime.now().date().isoformat(),
      'city': self.SPECIALIST_CITY,
      'phone': self.SPECIALIST_PHONE,
      'password': self.SPECIALIST_PASSWORD,
      "specialty": self.SPECIALIST_SPECIALTY
    }
    SignupSpecialist(signup_data.copy()).execute()

    with app.test_client() as test_client:
      response = test_client.post(
        self.BASE_PATH + '/login', json={
          'email': self.SPECIALIST_EMAIL,
          'password': self.SPECIALIST_PASSWORD
        }
      )
      response_json = json.loads(response.data)
      assert response.status_code == 201
      assert 'access_token' in response_json

  def test_login_specialist_without_fields(self):
    with app.test_client() as test_client:
      response = test_client.post(
        self.BASE_PATH+'/login', json={}
      )
      assert response.status_code == 400

  def test_login_specialist_invalid_password(self):
    signup_data = {
      'name': self.SPECIALIST_NAME,
      'email': self.SPECIALIST_EMAIL,
      'birth_day': datetime.now().date().isoformat(),
      'city': self.SPECIALIST_CITY,
      'phone': self.SPECIALIST_PHONE,
      'password': self.SPECIALIST_PASSWORD,
      "specialty": self.SPECIALIST_SPECIALTY
    }
    SignupSpecialist(signup_data.copy()).execute()

    with app.test_client() as test_client:
      response = test_client.post(
        self.BASE_PATH + '/login', json={
          'email': self.SPECIALIST_EMAIL,
          'password': ''.join(random.choice(self.letters) for i in range(5))
        }
      )
      assert response.status_code == 401

  def teardown_method(self):
    close_all_sessions()
    Base.metadata.drop_all(bind=engine)