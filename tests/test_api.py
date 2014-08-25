import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User, Role, Post, Comment
from test_client2 import TestClient


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

        user = User(email='admin@example.com', username='admin', confirmed=True, password='admin', name='Admin')
        user.role = Role.query.filter_by(name='Administrator').first()
        db.session.add(user)
        db.session.commit()
        self.user = user
        self.client2 = TestClient(self.app, user.generate_auth_token(3600), '')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.get_engine(self.app).dispose()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['error'] == 'not found')

    def test_user_does_not_exist(self):
        response = self.client.get(
            '/api/v1.0/users/%d' % 900,
            headers=self.get_api_headers(self.user.email, 'admin'))
        self.assertEqual(response.status_code, 404)

    def test_user_does_not_exist_404(self):
        response = self.client2.get(
            '/api/v1.0/users/%d' % 900)
        self.assertEqual(response.status_code, 404)
