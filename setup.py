from distutils.core import setup

setup(name='sqltester',
      description = "A python script to generate test queries for tests on data base tables using domain specific language",
      version='1.1.9',
      author='Andras Huebner',
      author_email='andreas.huebnerh@gmail.com',
      url='http://www.sqltester.com',
      package_dir={'sqltester': 'sqltester'},
      packages=['sqltester', 'sqltester.utils', 'sqltester.tests'],
      package_data = {
        '': ['*.sql', '*.cfg'],
        
    }
  )