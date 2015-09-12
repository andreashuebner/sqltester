# sqltester

## Overview/General idea
The basic idea of sql tester is to automate the writing of SQL queries to test tables 
in your data warehouse. 
Instead of writing the test queries manually, you write the test cases in a 
domain specific language and the python script will generate 
the test queries for you.

For each test case you define in the domain specific language, the python script will generate a test query.

Additionally, the script will generate an aggregation query that unions all failed tests into a final table.

Every test table will always have the following field:
**error_description**: Empty string if no issue or description of issue

The final table with all test cases ist just a union of the test results in the tables:

**error_description**: One row with error description for each test case if test cases failed.

## Getting started
You can just install sqltester with pip install sqltester, but you can also just clone the Git Repo.
For production, only the following files are required:

* sqltester.py
* _config_parser.py
* _query_generator.py
* config.cfg

### Simple Quickstart Example

Before describing the different usage options, let's do a simple quickstart example. 

Assume, you have a table **tbl_customers** with the following structure:

* account_id INT
* account_name STRING

You could now create a file with your test cases (e.g. test_cases.csv) with the
following content:
```
no duplicates on account_id in tbl_customers;

no duplicates on account_name in tbl_customers;
```
Test cases always end with ";".

Assuming that you keep the default table prefix, this will generate 
a test query to create the following tables
(all tables will end with a nine digit random number, 
so the numbers here are only examples):

**tbl_test_111111111**

**tbl_test_222222222**

**tbl_test_444444444**

After running the generated test query, you only need to check the summary
table e.g. like this:

```
select * from tbl_test_444444444 where error_description != "";
```

The final summary table will only contain failed test cases.

You can generate your test queries by calling sqltester.py like this:

python sqltester.py --input=test_cases.csv --output=test_queries.sql

The command line parameters --input and --output are the only required command line parameters.

This was only a quickstart description.

You can find a complete documentation of the available commands to describe test cases in the wiki.















