import unittest
import re

from _query_generator import Evaluator

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
  def clean_query(self, query_to_clean):
    ''' Helper function to clean query template from line endings and consuctive whitespaces '''
    query_to_clean = query_to_clean.replace('\n',' ')
    query_to_clean = re.sub(r'\s+',' ', query_to_clean)
    query_to_clean = query_to_clean.strip()
    return query_to_clean
  
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
    expected_template = self.clean_query(expected_template)
    expected_template = expected_template.replace('{{field_names}}', 'account_id')
    expected_template = expected_template.replace('{{table_name}}', 'tbl_customers')
    first_created_query = list_created_queries[0]
    main_query = re.findall(r'select.+;', first_created_query, re.S)
    second_part = main_query[0]
    self.assertEqual(second_part, expected_template, 'Should generate no duplicate query correctly')
    
    

