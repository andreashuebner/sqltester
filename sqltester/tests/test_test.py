import unittest
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from sqltester_parser import hello_world

class TestHello(unittest.TestCase):
    def test_hello(self):
      returnValue = hello_world()
      self.assertEqual(returnValue, 'hello world', 'Should return hello world')
