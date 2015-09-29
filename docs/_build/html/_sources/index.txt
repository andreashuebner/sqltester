sqltester - Documentation
************************
General idea
===================

The general idea of sqltester is to make it easy to generate test queries
for your tables in your database by expressing the test cases in a simplified, domain-specific
language.

Example:
Assume, you have a table **tbl_customers** with the following structure:
account_id INT
account_name STRING
invoice_amount INT

Then you could express test cases like this:::

  no duplicates on account_id in tbl_customers;
  at least 100 in tbl_customers;
  sum of invoice_amount at least 1000 in tbl_customers;

sqltester will generate a SQL query for each of the test cases and additionally one final
aggregation query with a union of all test tables.

Each of the generated test tables will have a field **error_description** that is either an
empty string or a string describing the failed test.

For the final test, you will just need to check the final aggregation table for datasets with 
*where error_description != ""*.

If you don't get any results, then all test cases have passed, otherwise one or several
tests have failed and the error description(s) will show you which ones.

Additionally, you can customize sqltester to use different sql expressions for certain test
cases, to generate a custom query after each test case (e.g. to grant access to tables) etc.

Language specification
===================

Testing for duplicates
----------------




