"pp -- wrapper for ply.cpp, a C preprocessor. not used for anything, delete."

from . import util
from ply import cpp, lex

def pp(fname, compiler='gcc'):
  preprocessor = cpp.Preprocessor(lex.lex(cpp))
  map(preprocessor.add_path, util.std_include_paths(compiler))
  preprocessor.parse(open(fname).read(), fname)
  tok = preprocessor.token()
  ret = []
  while tok:
    ret.append(tok)
    tok = preprocessor.token()
  return ret
