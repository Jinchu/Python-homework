import time
import requests
import re

class WebsiteChecker(object):
    """ Apache Kafka producer that checks single website status based on configuration. """

    def __init__(self, config, verbose_mode, testing=False):
        self.config = config
        self.debug = verbose_mode
        self.testing = testing

    def debug_print(self, msg):
        """ Outputs message to std.out only if verbose flag is enabled. """
        if self.debug:
            print(msg)

    def monitoring_loop(self):
        """ Periodically checks the status of the target site. """
        try:
            interval_str = self.config['Website-checker']['interval']
        except KeyError:
            print("Error: interval setting missing from configuration file")
            return -1

        try:
            target = self.config['Website-checker']['target']
        except KeyError:
            print("Error: target setting missing from configuration file")
            return -1

        check_content = True
        try:
            regex = self.config['Website-checker']['regex'].strip('\'')
            self.debug_print('configured regex: %s' % regex)
        except KeyError:
            check_content = False
            regex = ""

        if not target.startswith('http'):
            print("%s  is not a valid target" % target)
            return -1

        while True:
            self.debug_print('Running checks...')
            try:
                response = requests.get(target)
            except requests.exceptions.ConnectionError:
                self.debug_print('Connection refused')
                if self.testing:
                    return 0
                time.sleep(int(interval_str))
                continue

            self.debug_print("Response status: %d" % response.status_code)
            self.debug_print("response time: %f" % response.elapsed.total_seconds())

            if check_content:
                self.debug_print("Testing regex against the page HTML")
                pattern = re.compile(regex)
                regex_match_count = len(pattern.findall(response.text))
                self.debug_print(regex_match_count)
            if self.testing:
                return 0
            time.sleep(int(interval_str))
