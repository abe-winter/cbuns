"transform.py -- this ingests 'cbuns code' (C with @import) at the lex level and transforms"

import argparse

def transform():
  parser = argparse.ArgumentParser(description='transform a C file with @imports to straight C')
  parser.add_argument('package', help='path to package.json (necessary because it defines exports)')
  parser.add_argument('path', help='path of input file')
  parser.add_argument('-o', '--out', help='path to output. if a folder, use same filename as input. if not given, use stdout')
  args = parser.parse_args()

  # 1. tralp the thing
  # 2. get exports
  # 3. write with interpolation -- we're going to want line & slice of each substitution from symbols, and line for import stmts
  raise NotImplementedError
