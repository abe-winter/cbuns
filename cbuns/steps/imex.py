"imex -- 'import exports' from a cbuns package"

import argparse, os, json, pycparser, collections
from . import depgraph

# todo: support magic values like pkg.__PATH__ for read access to pkg dir (i.e. for config, data files).
#   hmm; do those files get bundled in a 'deploy package'? (what is a deploy package). how/where?

CFunction = collections.namedtuple('CFunction', 'name type args')

def scrape_c(path):
  "return objects of interest from top level of C file. for now that's: typedef, function declaration, variables"
  # todo: what are TypeDecl, Struct?
  # warning: this doesn't allow function, type and variable of same name; I think C allows some subset of those.
  toplevel = {}
  # note below: use_cpp is 'C pre-processor', not C++
  for name, child in pycparser.parse_file(path, use_cpp=True).children():
    if isinstance(child, pycparser.c_ast.FuncDef):
      func_name = child.children()[0][1].name
      decl = child.children()[0][1].children()[0][1]
      func_type = decl.type.children()[0][1].names
      args = [(arg.type.type.names, arg.name) for _, arg in decl.args.children()]
      toplevel[func_name] = CFunction(func_name, func_type, args)
    elif isinstance(child, pycparser.c_ast.Assignment):
      raise NotImplementedError
    elif isinstance(child, pycparser.c_ast.Typedef):
      raise NotImplementedError
    else:
      continue
  return toplevel

class Imexer:
  "import exporter; create export declarations for imported symbols"
  def __init__(self, package):
    self.package_dir = os.path.split(package)[0]
    self.jpack = json.load(open(package))

  def find(self, symbols):
    for dirname, subdirs, files in os.walk(self.package_dir):
      for fname in files:
        if not fname.lower().endswith('.c'): continue
        print scrape_c(os.path.join(dirname, fname))
        raise NotImplementedError
    # this has to tralp & preprocess
    raise NotImplementedError

def collect_symbols(package):
  build_order = depgraph.build_order(depgraph.deps(package))
  raise NotImplementedError

def main():
  parser = argparse.ArgumentParser(description="""imex is the 'import exports' process for cbuns.
    This analyzes the package and the used symbols and prints the extern & typedefs that would be inserted in place of @import.
    The package must be 'built' (transformed to .build/c) for this to work.""")
  parser.add_argument('package', help='path to package.json')
  parser.add_argument('symbols', help='comma-separated list of symbols; e.g. "pkg.subpkg.function_name,pkg.function2" (leave out the quotes, but pkg prefix necessary)')
  args = parser.parse_args()

  symbols = [tuple(sym.split('.')) for sym in args.symbols.split(',')]
  imexer = Imexer(args.package)
  imexer.find(symbols)
  raise NotImplementedError
