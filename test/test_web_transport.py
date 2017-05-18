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
            with c.session_transaction() as sess:
                sess['logged_in'] = True
                sess['user'] = self.user

            self.client = c

    def tearDown(self):
        pass

    def test_login_get(self):
        result = self.app.get('/login')
        self.assertEqual(result.status_code, 200)
        self.assertTrue('Ordering Interface </title>' in result.data)

    @patch('src.app.api_up', mock_app.api_up_user)
    @patch('src.app.update_status_details', mock_app.update_status_details_true)
    def test_login_post_success(self):
        data_dict = {'username': self.user.username, 'password': self.user.wurd}
        result = self.app.post('/login', data=data_dict)
        # successful login redirects to /index
        self.assertTrue(">/index/</a>" in result.data)
        self.assertEqual(result.status_code, 302)

    @patch('src.app.api_up', mock_app.api_up_user_fail)
    def test_login_post_fail(self):
        data_dict = {'username': self.user.username, 'password': self.user.wurd}
        result = self.client.post('/login', data=data_dict)
        self.assertEqual(result.status_code, 401)

    def test_get_logout(self):
        result = self.client.get('/logout')
        # results in a redirect to the login page
        self.assertTrue(">/login</a>" in result.data)
        self.assertEqual(result.status_code, 302)

    def test_get_index(self):
        result = self.client.get('/index/')
        self.assertTrue("<title>ESPA - LSRD</title>" in result.data)
        self.assertEqual(result.status_code, 200)

    def test_get_new_order(self):
        result = self.client.get("/ordering/new/")
        self.assertTrue("<p>New Bulk Order</p>" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_up', mock_app.api_post_order)
    def test_submit_order_post_success(self):
        data = self.form_order
        data['input_product_list'] = (StringIO(self.default_sceneid), 'in.txt')
        result = self.client.post("/ordering/submit/",
                                  content_type='multipart/form-data',
                                  data=data)
        self.assertTrue("/ordering/order-status/bob@google.com-03072016-085432/" in result.data)
        self.assertEqual(result.status_code, 302)

    @patch('src.app.api_up', mock_app.api_up_list_orders)
    def test_get_list_orders(self):
        result = self.client.get("/ordering/status/")
        self.assertTrue("<title>ESPA -  ESPA Reports </title>" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_up', mock_app.api_up_order_status)
    def test_get_view_order(self):
        result = self.client.get("/ordering/order-status/bob@google.com-12345-9876/")
        self.assertTrue("Details for: bob@google.com-12345-9876" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_up', mock_app.api_up_reports)
    def test_get_list_reports(self):
        result = self.client.get("/reports/")
        self.assertTrue("<title>ESPA -  ESPA Reports" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_up', mock_app.api_up_rss_feed)
    def test_get_rss_feed(self):
        result = self.client.get("/ordering/status/bob@gmail.com/rss/")
        self.assertEquals(result.status_code, 200)









