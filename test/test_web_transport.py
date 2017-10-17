#!/usr/bin/env python

import unittest
from mock import patch
from mock import MagicMock

from flask import request
from StringIO import StringIO
from src.app import espaweb
from src.mocks import app as mock_app
from src.utils import User


class ApplicationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = espaweb.test_client()
        self.app.testing = True
        self.default_sceneid = 'LE70270292003144EDC00'
        self.form_order = mock_app.form_order

        user_parms = {'email': 'foo@gmail.com',
                      'username': 'foo',
                      'wurd': 'bar',
                      'roles': ['active']}

        self.user = User(**user_parms)

        with espaweb.test_client() as c:
            c.set_cookie(self.app.config['HTTP_HOST'], 'EROS_SSO_None_secure', 'TestingTesting')
            with c.session_transaction() as sess:
                sess['logged_in'] = True
                sess['user'] = self.user
                sess['stat_backlog_depth'] = 1000

            self.client = c

    def tearDown(self):
        pass

    def test_login_get_fail(self):
        result = self.app.get('/login')
        self.assertEqual(result.status_code, 404)

    def test_index_get_public(self):
        result = self.app.get('/index')
        self.assertEqual(result.status_code, 200)
        self.assertIn('Login', result.data)
        
    def test_index_get_cookie(self):
        result = self.cilent.get('/index')
        self.assertEqual(result.status_code, 200)
        self.assertIn('Logout', result.data)

    def test_get_index(self):
        result = self.client.get('/index/')
        self.assertIn("<title>ESPA - LSRD</title>", result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.cache.get', lambda y: None)
    @patch('src.app.api_up', mock_app.api_up_user_fail)
    def test_login_post_fail(self):
        data_dict = {'username': self.user.username, 'password': self.user.wurd}
        result = self.client.post('/login', data=data_dict)
        self.assertEqual(result.status_code, 401)

    @patch('src.app.api_up', mock_app.api_up_user)
    @patch('src.app.update_status_details', mock_app.update_status_details_true)
    def test_get_logout(self):
        result = self.client.get('/logout')
        # results in a redirect to the login page
        self.assertIn(">/login</a>", result.data)
        self.assertEqual(result.status_code, 302)
        self.assertIn('login', result.headers['Location'])
        data_dict = {'username': self.user.username, 'password': self.user.wurd}
        result = self.client.post('/login', data=data_dict)
        # successful login redirects to /index
        self.assertIn(">/index/</a>", result.data)
        self.assertEqual(result.status_code, 302)
        self.assertIn('Location', result.headers)
        self.assertIn('index', result.headers['Location'])

    def test_get_new_order(self):
        result = self.client.get("/ordering/new/")
        self.assertIn("<p>New Bulk Order</p>", result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_up', mock_app.api_post_order)
    def test_submit_order_post_success(self):
        data = self.form_order
        data['input_product_list'] = (StringIO(self.default_sceneid), 'in.txt')
        result = self.client.post("/ordering/submit/",
                                  content_type='multipart/form-data',
                                  data=data)
        self.assertIn("/ordering/order-status/bob@google.com-03072016-085432/", result.data)
        self.assertEqual(result.status_code, 302)

    @patch('src.app.api_up', mock_app.api_up_list_orders)
    def test_get_list_orders(self):
        result = self.client.get("/ordering/status/")
        title = "<title>ESPA -  Orders for {} </title>".format(self.user.email)
        self.assertIn(title, result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_up', mock_app.api_up_order_status)
    def test_get_view_order(self):
        result = self.client.get("/ordering/order-status/bob@google.com-12345-9876/")
        self.assertIn("Details for: bob@google.com-12345-9876", result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_up', mock_app.api_up_reports)
    def test_get_list_reports_admin_only(self):
        result = self.client.get("/reports/")
        self.assertIn('index', result.data)
        self.assertEqual(result.status_code, 302)

    @patch('src.app.api_up', mock_app.api_up_rss_feed)
    def test_get_rss_feed(self):
        result = self.client.get("/ordering/status/bob@gmail.com/rss/")
        self.assertEquals(result.status_code, 200)









