# Python-homework

There are some prerequisites for running this program:

- kafka-python
- libpq-dev
- psycopg2

Running the modules requires that you are in the root of this repo:

```bash
python3 website_checker -c <path to the config>
```

```bash
python3 database_writer -c <path to the config>
```

## Structure of this project

```plain-text
Python-homework <-- Root of the repo
├── website_checker <-- Root of the package 0
|   ├── __init__.py
│   ├── checker.py
│   └── test_checker.py
│
├── database_writer <-- Root of the package 1
│   ├── __init__.py
│   ├── db_writer.py
│   └── test_db_writer.py
│
├── example_website_checker.conf
├── example_database_writer.conf
└── README.md
```
