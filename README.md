# sqltester

## Overview/General idea
The basic idea of sql tester is to automate the writing of SQL queries to test tables 
in your data warehouse. 
Instead of writing the test queries manually, you write the test cases in a 
domain specific language and the python script will generate 
the test queries for you.

The generated queries have the following basic structure:

Test case 1 -> table_prefix_table_1

Test case 2 -> table_prefix_table_2

Test case 3 -> table_prefix_table_3

Every test table will always have the following field:
**error_description**: Empty string if no issue or description of issue

The final table with all test cases ist just a union of the test results in the tables:

**error_description**: One row with error description for each test case if test cases failed.

## Getting started
You can just install sqltester with pip install sqltester, but you can also just clone the Git Repo.
For production, only the following files are required:

* sqltester.py
* _config_parser.py
* config.cfg
* 







