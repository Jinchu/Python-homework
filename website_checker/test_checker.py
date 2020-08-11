import unittest
import requests
import sys
from unittest.mock import MagicMock

import checker


class testProducer():
    def __init__(self):
        self.status = 0

    def send(self, topic, value):
        if topic != 'unittest':
            print("topic [%s] does not match expected" % topic)
            sys.exit(1)

    def flush(self):
        return 2

class testResponse():
    class testElapsed():
        def total_seconds(self):
            return 0.242703

    def __init__(self, code, time, text):
        self.status_code = code
        self.elapsed = self.testElapsed()
        self.text = text

def build_200_test_response():
    """ Helper to simulate config. """
    response = testResponse(200, '0.242703', "Test Web Site LOL")
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
        test_conf['Website-checker'] = {'target':'http://exampleasdf.com', 'interval':'1',}
        test_conf['Kafka'] = {'server-name':'test-url:1324', 'ssl_ca_path':'/path/',
                              'ssl_certfile':'/path/', 'ssl_keyfile': '/path/', 'topic':'unittest'}
        web_check = checker.WebsiteChecker(test_conf, False, testing=True)
        web_check.setup_kafka_producer = MagicMock(return_value=testProducer())
        self.assertEqual(web_check.monitoring_loop(), 0)

    def test_monitoring_regex(self):
        requests.get = MagicMock(return_value=build_200_test_response())
        test_conf = {}
        test_conf['Website-checker'] = {'target':'http://example.comasdf', 'interval':'1',
                                        'regex':'pattern'}
        test_conf['Kafka'] = {'server-name':'test-url:1324', 'ssl_ca_path':'/path/',
                              'ssl_certfile':'/path/', 'ssl_keyfile': '/path/', 'topic':'unittest'}

        web_check = checker.WebsiteChecker(test_conf, False, testing=True)
        web_check.setup_kafka_producer = MagicMock(return_value=testProducer())
        self.assertEqual(web_check.monitoring_loop(), 0)

if __name__ == '__main__':
    unittest.main()
