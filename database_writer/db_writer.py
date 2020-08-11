import psycopg2
from psycopg2.extras import RealDictCursor
from kafka import KafkaConsumer

class DatabaseWriter(object):
    """ Apache Kafka consumer that writes website status to a DB. """
    def __init__(self, config, verbose_mode, testing=False):
        self.config = config
        self.debug = verbose_mode
        self.testing = testing

    def debug_print(self, msg):
        """ Outputs message to std.out only if verbose flag is enabled. """
        if self.debug:
            print(msg)

    def setup_kafka_consumer(self):
        consumer = KafkaConsumer(
            self.config['Kafka']['topic'],
            auto_offset_reset="earliest",
            bootstrap_servers=self.config['Kafka']['server-name'],
            client_id="demo-client-1",
            group_id="demo-group",
            security_protocol="SSL",
            ssl_cafile=self.config['Kafka']['ssl_ca_path'],
            ssl_certfile=self.config['Kafka']['ssl_certfile'],
            ssl_keyfile=self.config['Kafka']['ssl_keyfile'],
        )
        self.debug_print("Consumer: %s" % str(consumer))

        return consumer

    def insert_measurement_to_db(self, measurement):
        """ Inserts the given measurement in to the DB set in the configuration. Returns negative
        integer in case of an error."""

        db_uri = self.config['Postgre']['server-uri']
        table = self.config['Postgre']['table-name']

        db_conn = psycopg2.connect(db_uri)
        cursor = db_conn.cursor(cursor_factory=RealDictCursor)

        sqlCreateTable = "CREATE TABLE ExampleMeasurements (id varchar(128), measurement varchar(128));"
        cursor.execute(sqlCreateTable)

        sqlInsertRow = "INSERT INTO %s values('%s', '%s')" % (table, measurement[0], measurement[1])
        self.debug_print(sqlInsertRow)
        try:
            cursor.execute(sqlInsertRow)
        except psycopg2.errors.UndefinedTable:
            print("Table %s does not exist in the database" % table)
            return -1
        return 1

    def monitoring_loop(self, consumer):
        """ Periodically fetch the status from Kafka. """

        while True:
            raw_msgs = consumer.poll(timeout_ms=8000)
            for tp, msgs in raw_msgs.items():
                for msg in msgs:
                    decoded = msg.value.decode('utf-8')
                    # self.debug_print(decoded)
                    measurement = decoded.split(':')

                    if self.insert_measurement_to_db(measurement) < 0:
                        return
