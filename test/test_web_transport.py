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
                      'roles': ['staff']}

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

    @patch('src.app.api_get', mock_app.api_get_user)
    @patch('src.app.update_status_details', mock_app.update_status_details_true)
    def test_login_post_success(self):
        data_dict = {'username': self.user.username, 'password': self.user.wurd}
        result = self.app.post('/login', data=data_dict)
        # successful login redirects to /index
        self.assertTrue(">/index/</a>" in result.data)
        self.assertEqual(result.status_code, 302)

    @patch('src.app.api_get', mock_app.api_get_user_fail)
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

    @patch('src.app.api_post', mock_app.api_post_order)
    def test_submit_order_post_success(self):
        data = self.form_order
        data['input_product_list'] = (StringIO(self.default_sceneid), 'in.txt')
        result = self.client.post("/ordering/submit/",
                                  content_type='multipart/form-data',
                                  data=data)
        self.assertTrue("/ordering/order-status/bob@google.com-03072016-085432/" in result.data)
        self.assertEqual(result.status_code, 302)

    @patch('src.app.api_get', mock_app.api_get_list_orders)
    def test_get_list_orders(self):
        result = self.client.get("/ordering/status/")
        self.assertTrue("<title>ESPA -  ESPA Reports </title>" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_get', mock_app.api_get_order_status)
    def test_get_view_order(self):
        result = self.client.get("/ordering/order-status/bob@google.com-12345-9876/")
        self.assertTrue("Details for: bob@google.com-12345-9876" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_get', mock_app.api_get_reports)
    def test_get_list_reports(self):
        result = self.client.get("/reports/")
        self.assertTrue("<title>ESPA -  ESPA Reports" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_get', mock_app.api_get_show_report)
    def test_get_show_report(self):
        result = self.client.get("/reports/orders_counts/")
        self.assertTrue("<h4>orders_counts Report</h4>" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_get', mock_app.api_get_stats_all)
    def test_get_console(self):
        result = self.client.get("/console")
        self.assertTrue("<h4>ESPA Console</h4>" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.update_status_details', mock_app.update_status_details_true)
    @patch('src.app.api_post', mock_app.api_post_status)
    def test_post_statusmsg(self):
        data = {'display_system_message': 'on', 'system_message_title': 'foo',
                'system_message_body': 'bar'}
        result = self.client.post("/console/statusmsg", data=data)
        self.assertTrue("<p>You should be redirected automatically to target URL: "
                        "<a href=\"/index/\">/index/</a>" in result.data)
        self.assertEqual(result.status_code, 302)

    @patch('src.app.api_get', mock_app.api_get_system_config)
    def test_get_console_config(self):
        result = self.client.get("/console/config")
        self.assertEqual(result.status_code, 200)








