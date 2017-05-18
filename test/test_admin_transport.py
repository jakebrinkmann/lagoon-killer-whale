"""
    Purpose: Test the admin (staff_only) functionality
"""

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
                      'roles': ['active', 'staff']}

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

    @patch('src.app.api_up', mock_app.api_up_show_report)
    def test_get_show_report(self):
        result = self.client.get("/reports/orders_counts/")
        self.assertTrue("<h4>orders_counts Report</h4>" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_up', mock_app.api_up_stats_all)
    def test_get_console(self):
        result = self.client.get("/admin_console")
        self.assertTrue("<h4>ESPA Console</h4>" in result.data)
        self.assertEqual(result.status_code, 200)

    @patch('src.app.api_up', mock_app.api_up_system_config)
    def test_get_console_config(self):
        result = self.client.get("/admin_console/config")
        self.assertEqual(result.status_code, 200)

    @patch('src.app.update_status_details', mock_app.update_status_details_true)
    @patch('src.app.api_up', mock_app.api_post_status)
    def test_post_statusmsg(self):
        data = {'display_system_message': 'on', 'system_message_title': 'foo',
                'system_message_body': 'bar'}
        result = self.client.post("/admin_console/statusmsg", data=data)
        self.assertTrue("<p>You should be redirected automatically to target URL: "
                        "<a href=\"/index/\">/index/</a>" in result.data)
        self.assertEqual(result.status_code, 302)