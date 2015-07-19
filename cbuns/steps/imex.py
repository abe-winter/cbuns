"imex -- 'import exports' from a cbuns package"

import argparse, os, json, pycparser, collections
from . import depgraph
from .. import pkg

# todo: support magic values like pkg.__PATH__ for read access to pkg dir (i.e. for config, data files).
#   hmm; do those files get bundled in a 'deploy package'? (what is a deploy package). how/where?

class ImexImportError(StandardError): pass
class UnkSymbolError(ImexImportError): pass
class AmbiguityError(ImexImportError): pass

class ExportObject(object): "base class"

# yeah, no chance this will ever be complete; the compiler needs to tell us about this. or just create a reasonable union and let the compiler complain.
BUILTIN_TYPES = {'int', 'char', '*', 'float'}

class CFunction(ExportObject):
  "function declaration"
  def __init__(self, name, type, args):
    self.name, self.type, self.args = name, type, args
  
  @property
  def types(self):
    "return list of unique types used by the function declaration"
    return set(sum([self.type]+[types for types, arg in self.args], []))

  @property
  def cline(self):
    "return C code (extern decl) to patch in somewhere"
    return 'extern %s %s(%s);' % (
      ' '.join(self.type),
      self.name,
      ', '.join('%s %s' % (' '.join(types), arg) for types, arg in self.args)
    )

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

  def all_symbols(self):
    "helper for self.find(). returns a bunch of dictionaries"
    name_usage = collections.defaultdict(list)
    full_lookups = {}
    direct_lookups = {}
    for dirname, subdirs, files in os.walk(self.package_dir):
      if any(pkg.util.hidden_dir(d) for d in dirname.split('/')): # skip hidden directories
        # warning: splitting by '/' not platform-safe
        continue
      for fname in files:
        if not fname.lower().endswith('.c'): continue
        fullpath = os.path.join(dirname, fname)
        # warning below: platform-unsafe delimiter (and other horrors)
        prefix = tuple(filter(None, os.path.split(fullpath[len(dirname):])[0].split('/'))) + (os.path.splitext(fname)[0],)
        res = scrape_c(fullpath)
        for name, value in res.items():
          # note below: overwriting here results in an extra name_usage entry. (there's also the 'folder + object same name' case)
          direct_lookups[(name,)] = value
          full_lookups[prefix + (name,)] = value
          name_usage[name].append(fullpath)
    
    return full_lookups, direct_lookups, name_usage

  def find(self, symbols):
    "return dict {symbol:list_of_c_lines}"
    # todo: all_symbols should return a DAG of functions & types
    # we also need 'original package' annotations to know mangled import names
    full, direct, name2file = self.all_symbols()
    lines = {}
    for symbol in symbols:
      relative_symbol = symbol[1:] # strip out the package name. does this need to be checked? depends on source.
      decl = None
      if relative_symbol in full:
        decl = full[relative_symbol]
      elif relative_symbol in direct:
        if len(name2file[relative_symbol[-1]]) > 1:
          raise AmbiguityError(self.package_dir, symbol, name2file[relative_symbol])
        decl = direct[relative_symbol]
      else:
        raise UnkSymbolError(self.package_dir, symbol)
      if decl is None:
        # ug.
        raise RuntimeError('local "decl" was never set')
      if set(decl.types) - BUILTIN_TYPES:
        raise NotImplementedError('todo: include non-builtin types', set(decl.types) - BUILTIN_TYPES)
      lines[symbol] = DeclLine(decl.name, decl.cline)
    return lines

DeclLine = collections.namedtuple('DeclLine', 'name line')

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
  for sym, dline in imexer.find(symbols).items():
    print sym, dline
