import unittest

from _query_generator import Evaluator

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

