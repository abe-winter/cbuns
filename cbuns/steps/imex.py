"imex -- 'import exports' from a cbuns package"

import argparse, os, json
from . import depgraph

# todo: support magic values like pkg.__PATH__ for read access to pkg dir (i.e. for config, data files).
#   hmm; do those files get bundled in a 'deploy package'? (what is a deploy package). how/where?

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

def collect_symbols(package):
  build_order = depgraph.build_order(depgraph.deps(package))
  raise NotImplementedError

def imex():
  parser = argparse.ArgumentParser(description="""imex is the 'import exports' process for cbuns.
    this analyzes the package and the used symbols and prints the extern & typedefs that would be inserted in place of @import.
    the package must be 'built' (transformed to .build/c) for this to work.""")
  parser.add_argument('package', help='path to package.json')
  parser.add_argument('symbols', help='comma-separated list of symbols; e.g. "pkg.subpkg.function_name,pkg.function2" (leave out the quotes, but pkg prefix necessary)')
  args = parser.parse_args()

  symbols = [tuple(sym.split('.')) for sym in args.symbols.split(',')]
  imexer = Imexer(args.package)
  raise NotImplementedError
