import unittest
import re

from _query_generator import Evaluator

def clean_query(query_to_clean):
    ''' Helper function to clean query template from line endings and consuctive whitespaces '''
    query_to_clean = query_to_clean.replace('\n',' ')
    query_to_clean = re.sub(r'\s+',' ', query_to_clean)
    query_to_clean = query_to_clean.strip()
    return query_to_clean
class TestHelperFunctions(unittest.TestCase):
  def test_is_number_function(self):
    evaluator = Evaluator('', 'sqltester/tests/config_dummy.cfg')
    is_number = evaluator._is_number('Andreas')
    self.assertEqual(is_number, False, 'Should return False for string')
    is_number = evaluator._is_number('100Andreas')
    self.assertEqual(is_number, False, 'Should return False for number mixed with string')
    is_number = evaluator._is_number('Andreas100')
    self.assertEqual(is_number, False, 'Should return False for string mixed with number')
    is_number = evaluator._is_number(100)
    self.assertEqual(is_number, True, 'Should return true for integer')
    is_number = evaluator._is_number(100.99)
    self.assertEqual(is_number, True, 'Should return for double')

class TestReplaceTemplateVariable(unittest.TestCase):
  def test_template_with_one_variable(self):
    evaluator = Evaluator('', 'sqltester/tests/config_dummy.cfg')
    template = 'Create or replace {{table_name}} as '
    template = evaluator._replace_template_variable(template, 'table_name', 'tbl_andreas')
    self.assertEqual(template, 'Create or replace tbl_andreas as ', 'Should substitute variable')
    
  def test_template_with_several_variables(self):
    evaluator = Evaluator('', 'sqltester/tests/config_dummy.cfg')
    template = 'Create or replace {{table_name}} as {{table_name}} '
    template = evaluator._replace_template_variable(template, 'table_name', 'tbl_andreas')
    self.assertEqual(template, 'Create or replace tbl_andreas as tbl_andreas ',
      'Should substitute several variables')
    
class TestRandomNumberFunction(unittest.TestCase):
  def test_random_number_function(self):
    evaluator = Evaluator('', 'sqltester/tests/config_dummy.cfg')
    random_number_1 = evaluator._create_random_number(1, 999999999)
    random_number_2 = evaluator._create_random_number(1, 999999999)
    self.assertRegexpMatches(str(random_number_1), r'[^a-z]', 'Random number created should not ' +
      ' contain letters')
    self.assertGreaterEqual(random_number_1, 1, 'Should be greater equal minimum value')
    self.assertLessEqual(random_number_1, 999999999, 'Should be less equal maximum value')
    self.assertRegexpMatches(str(random_number_2), r'[^a-z]', 'Random number created should not ' +
      ' contain letters')
    self.assertGreaterEqual(random_number_2, 1, 'Should be greater equal minimum value')
    self.assertLessEqual(random_number_2, 999999999, 'Should be less equal maximum value')
    self.assertNotEqual(random_number_1, random_number_2, 'Both random numbers should be ' +
      ' different')
    
class TestNoDuplicateQueries(unittest.TestCase):
  
  def setUp(self):
    self.TEMPlATE_NO_DUPLICATES_FOR_TEST = """
    select
    count(*) as number_duplicates,
    case when count(*) > 0 then "Duplicates found in table {{table_name}}" else "" end as error_description
    from
    (
    SELECT {{field_names}}, COUNT(*)
    FROM {{table_name}}
    GROUP BY {{field_names}}
    HAVING COUNT(*) > 1
    )x
    ;
    """
  def test_unique_function_one_field_name(self):
    statement_to_test = 'No duplicates on account_id in tbl_customers;'
    evaluator = Evaluator(statement_to_test, 'sqltester/tests/config_dummy.cfg')
    list_created_queries = evaluator.parse()
    #The only thing we do not test here is the create table statement because of random number
    expected_template = self.TEMPlATE_NO_DUPLICATES_FOR_TEST
    expected_template = expected_template.replace('{{field_names}}', 'account_id')
    expected_template = expected_template.replace('{{table_name}}', 'tbl_customers')
    expected_template = clean_query(expected_template)
    first_created_query = list_created_queries[0]
    main_query = re.findall(r'select.+;', first_created_query, re.S)
    second_part = main_query[0]
    self.assertEqual(second_part, expected_template, 'Should generate no duplicate query correctly')
    
class TestMinimumDatasetsQueries(unittest.TestCase):
  
  def setUp(self):
    self.TEMPlATE_MINIMUM_DATASETS_FOR_TEST = """
    select
    case when number_datasets < {{minimum_datasets}} then "Expected at least {{minimum_datasets}} datasets in table
    {{table_name}}" else "" end as error_description
    from
    (
      SELECT COUNT(*) as number_datasets
      FROM {{table_name}}
      {{conditions}}
    )x
;
    """
  def test_minimum_datasets_without_condition(self):
    statement_to_test = 'at least 100 in tbl_customers; '
    evaluator = Evaluator(statement_to_test, 'sqltester/tests/config_dummy.cfg')
    list_created_queries = evaluator.parse()
    #The only thing we do not test here is the create table statement because of random number
    expected_template = self.TEMPlATE_MINIMUM_DATASETS_FOR_TEST
    expected_template = expected_template.replace('{{conditions}}', '')
    expected_template = expected_template.replace('{{table_name}}', 'tbl_customers')
    expected_template = expected_template.replace('{{minimum_datasets}}', '100')
    expected_template = clean_query(expected_template)
    first_created_query = list_created_queries[0]
    main_query = re.findall(r'select.+;', first_created_query, re.S)
    second_part = main_query[0]
    self.assertEqual(second_part, expected_template, 'Should generate minimum datasets query correctly')
    
  def test_minimum_datasets_with_condition(self):
    statement_to_test = 'at least 100 in tbl_customers where invoice_amount >= 100 and invoice_age < 30; '
    evaluator = Evaluator(statement_to_test, 'sqltester/tests/config_dummy.cfg')
    list_created_queries = evaluator.parse()
    #The only thing we do not test here is the create table statement because of random number
    expected_template = self.TEMPlATE_MINIMUM_DATASETS_FOR_TEST
    expected_template = expected_template.replace('{{conditions}}', 'where invoice_amount >= 100 and invoice_age < 30')
    expected_template = expected_template.replace('{{table_name}}', 'tbl_customers')
    expected_template = expected_template.replace('{{minimum_datasets}}', '100')
    expected_template = clean_query(expected_template)
    first_created_query = list_created_queries[0]
    main_query = re.findall(r'select.+;', first_created_query, re.S)
    second_part = main_query[0]
    print("second part")
    print(second_part)
    self.assertEqual(second_part, expected_template, 'Should generate minimum datasets query correctly')
    
class TestMinimumSumQueries(unittest.TestCase):
  def setUp(self):
    self.TEMPlATE_MINIMUM_SUM_FOR_TEST = """
    select
    case when sum_of_field < {{minimum_sum}} then "Expected sum of {{field_name}} in table
    {{table_name}} to be at least {{minimum_sum}}" else "" end as error_description
    from
    (
    SELECT SUM({{field_name}}) as sum_of_field
    FROM {{table_name}}
    {{conditions}}
    )x
    ;
    """
    
  def test_minimum_sum_without_condition(self):
    statement_to_test = 'sum of invoice_amount at least 1000 in tbl_customers;'
    evaluator = Evaluator(statement_to_test, 'sqltester/tests/config_dummy.cfg')
    list_created_queries = evaluator.parse()
    #The only thing we do not test here is the create table statement because of random number
    expected_template = self.TEMPlATE_MINIMUM_SUM_FOR_TEST
    expected_template = expected_template.replace('{{conditions}}', '')
    expected_template = expected_template.replace('{{table_name}}', 'tbl_customers')
    expected_template = expected_template.replace('{{minimum_sum}}', '1000')
    expected_template = expected_template.replace('{{field_name}}', 'invoice_amount')
    expected_template = clean_query(expected_template)
    first_created_query = list_created_queries[0]
    main_query = re.findall(r'select.+;', first_created_query, re.S)
    second_part = main_query[0]
    print("second part")
    print(second_part)
    self.assertEqual(second_part, expected_template, 'Should generate minimum sum query correctly')  

class TestAggregationQuery(unittest.TestCase):
  def setUp(self):
    self.TEMPlATE_AGGREGATION_FOR_TEST = """
    select
    error_description
    from {{table_list}}
    where error_description != ''
    ;
    """
    
  def test_aggregation_query_one_table(self):
    expected_template = self.TEMPlATE_AGGREGATION_FOR_TEST
    expected_template = expected_template.replace('{{table_list}}', 'tbl_test_1')
    expected_template = clean_query(expected_template)
    evaluator = Evaluator('', 'sqltester/tests/config_dummy.cfg')
    list_tables = ['tbl_test_1']
    returned_template = evaluator._create_aggregation_query(list_tables)
    main_query = re.findall(r'select.+;', returned_template, re.S)
    second_part = main_query[0]
    second_part = clean_query(second_part)
    print("second part")
    print(second_part)
    self.assertEqual(second_part, expected_template, 'Should generate aggregation query correctly')
    
  def test_aggregation_query_two_tables(self):
    expected_template = self.TEMPlATE_AGGREGATION_FOR_TEST
    expected_template = expected_template.replace('{{table_list}}', 'tbl_test_1,tbl_test_2')
    expected_template = clean_query(expected_template)
    evaluator = Evaluator('', 'sqltester/tests/config_dummy.cfg')
    list_tables = ['tbl_test_1','tbl_test_2']
    returned_template = evaluator._create_aggregation_query(list_tables)
    main_query = re.findall(r'select.+;', returned_template, re.S)
    second_part = main_query[0]
    second_part = clean_query(second_part)
    print("second part")
    print(second_part)
    self.assertEqual(second_part, expected_template, 'Should generate aggregation query correctly')
    

  
