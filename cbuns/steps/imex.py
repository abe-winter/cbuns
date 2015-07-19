"imex -- 'import exports' from a cbuns package"

import argparse, os, json

class DepGraph:
  "dependency graph; collect declared deps from up the chain"
  # 1. create depgraph
  # 2. pretralp each one to create the complete list of symbols
  # 3. run imex in order (deepest deps to newest)
  # 4. (external to this, the results are used by transform)

class Imexer:
  "import exporter; create export declarations for imported symbols"
  def __init__(self, package):
    self.package_dir = os.path.split(package)[0]
    self.jpack = json.load(open(package))

  def find(self, symbols):
    # this has to tralp & preprocess
    raise NotImplementedError

def imex():
  parser = argparse.ArgumentParser(description="imex is the 'import exports' process for cbuns. this analyzes the package and the used symbols and prints the extern & typedefs that would be inserted in place of @import")
  parser.add_argument('package', help='path to package.json')
  parser.add_argument('symbols', help='comma-separated list of symbols; e.g. "pkg.subpkg.function_name,pkg.function2" (leave out the quotes, but pkg prefix necessary)')
  args = parser.parse_args()

  symbols = [tuple(sym.split('.')) for sym in args.symbols.split(',')]
  imexer = Imexer(args.package)
  raise NotImplementedError
