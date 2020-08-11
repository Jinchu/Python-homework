import unittest
import requests
from unittest.mock import MagicMock
import checker


class testResponse():
    def __init__(self, code, time, text):
        self.status_code = code
        self.time = time
        self.text = text

def build_200_test_response():
    """ Helper to simulate config. """
    response = testResponse(200, 0.242703, "Test Web Site LOL")
    return response

class TestCheckerErrorHandling(unittest.TestCase):

    def test_no_interval_set(self):
        test_conf = {}
        test_conf['Website-checker'] = {'target':'http://example.com'}
        web_check = checker.WebsiteChecker(test_conf, False, testing=True)
        self.assertEqual(web_check.monitoring_loop(), -1)

    def test_no_target_set(self):
        test_conf = {}
        test_conf['Website-checker'] = {'interval':'500'}
        web_check = checker.WebsiteChecker(test_conf, False, testing=True)
        self.assertEqual(web_check.monitoring_loop(), -1)

    def test_invalid_url(self):
        test_conf = {}
        test_conf['Website-checker'] = {'target':'example.com', 'interval':'500'}
        web_check = checker.WebsiteChecker(test_conf, False, testing=True)
        self.assertEqual(web_check.monitoring_loop(), -1)

class TestMonitoringLoop(unittest.TestCase):
    def test_monitoring(self):
        requests.get = MagicMock(return_value=build_200_test_response())
        test_conf = {}
        test_conf['Website-checker'] = {'target':'http://example.com', 'interval':'1'}
        web_check = checker.WebsiteChecker(test_conf, False, testing=True)
        self.assertEqual(web_check.monitoring_loop(), 0)

    def test_monitoring_regex(self):
        requests.get = MagicMock(return_value=build_200_test_response())
        test_conf = {}
        test_conf['Website-checker'] = {'target':'http://example.com', 'interval':'1',
                                        'regex':'pattern'}
        web_check = checker.WebsiteChecker(test_conf, False, testing=True)
        self.assertEqual(web_check.monitoring_loop(), 0)

if __name__ == '__main__':
    unittest.main()
