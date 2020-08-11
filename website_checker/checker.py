import time
import requests
import re
from kafka import KafkaProducer


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

    def setup_kafka_producer(self):
        producer = KafkaProducer(
            bootstrap_servers=self.config['Kafka']['server-name'],
            security_protocol="SSL",
            ssl_cafile=self.config['Kafka']['ssl_ca_path'],
            ssl_certfile=self.config['Kafka']['ssl_certfile'],
            ssl_keyfile=self.config['Kafka']['ssl_keyfile'],
        )

        return producer

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

        producer = self.setup_kafka_producer()
        kafka_topic = self.config['Kafka']['topic']

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

            page_status = 'status:%s' % str(response.status_code)
            response_time = 'response-time:%s' % str(response.elapsed.total_seconds())
            self.debug_print(page_status)
            self.debug_print(response_time)
            producer.send(kafka_topic, page_status.encode('utf-8'))
            producer.send(kafka_topic, response_time.encode('utf-8'))

            if check_content:
                self.debug_print("Testing regex against the page HTML")
                pattern = re.compile(regex)
                regex_match_count = len(pattern.findall(response.text))

                regex_result = 'regex:%s' % str(regex_match_count)
                self.debug_print(regex_result)
                producer.send(kafka_topic, regex_result.encode('utf-8'))

            producer.flush()

            if self.testing:
                return 0
            time.sleep(int(interval_str))
