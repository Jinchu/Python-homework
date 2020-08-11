import sys
import argparse
import db_writer
from configparser import ConfigParser


def set_arguments():
    """ Function for argument parser """
    parser = argparse.ArgumentParser(
        description = 'Consume status info from Kafka and write it to a DB')
    parser.add_argument('-c', dest = 'config', type = str,
                        help = 'Path to the configuration file. Mandatory')
    parser.add_argument('-v', dest = 'debug', action = 'store_true',
                        help = 'Enable verbose output. Optional')
    parser.set_defaults(debug=False)

    arguments = parser.parse_args()
    if arguments.config is None:
        parser.print_help()
        return None, None

    return arguments, parser

def main():

    args, parser = set_arguments()
    if args is None:
        return -1

    config = ConfigParser()
    try:
        config.read(args.config)
    except:
        print('ERROR: File %s in not a valid configuration.' % args.config)
        return -1

    writer = db_writer.DatabaseWriter(config, args.debug)
    consumer = writer.setup_kafka_consumer()

    writer.monitoring_loop(consumer)

    return 0


if __name__ == "__main__":
    sys.exit(main())
