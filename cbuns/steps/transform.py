"transform.py -- this ingests 'cbuns code' (C with @import) at the lex level and transforms"

import pycparser, argparse, collections

class ParsingError(StandardError): pass

class Tralper:
  "pre-transformation lexer pass"
  def __init__(self):
    # todo: tweak clex to supply whitespace (because we'll need to regenerate the file)
    self.clex = pycparser.c_lexer.CLexer(self.error, self.lbrace, self.rbrace, self.type_lookup)
    self.clex.build()
    self.memory = [] # line-at-a-time memory of tokens
    self.aliases = {} # {alias:import_path} for each @import stmt
    self.symbols = [] # list of ID (PERIOD ID)* symbols starting with an imported alias

  def error(self, error, line, col):
    if error == "Illegal character '@'":
      # todo: instead of parsing error strings, extend the lexer
      self.memory.append('@')
    else:
      raise ParsingError(error, line, col)

  def lbrace(self): pass
  def rbrace(self): pass

  def type_lookup(self, token):
    return False

  def check_memory(self):
    if tok_compare(self.memory, ('@', 'import', 'LPAREN', 'STRING_LITERAL', 'COMMA', 'ID', 'RPAREN', 'SEMI')):
      self.aliases[self.memory[5].value] = self.memory[3].value
    elif tok_compare(self.memory, ('@', 'import', 'LPAREN', 'STRING_LITERAL', 'RPAREN', 'SEMI')):
      self.aliases[os.path.split(self.memory[3].value)[-1]] = self.memory[3].value
    else:
      for dotted in find_dotted_ids(self.memory):
        if dotted[0].value in self.aliases:
          self.symbols.append(tuple(tok.value for tok in dotted[::2]))

  def process(self, string):
    # todo: fileobj instead of string (this can be line by line)
    self.clex.input(string)
    tok = self.clex.token()
    self.line = tok.lineno if tok else None
    while tok:
      if self.line != tok.lineno:
        self.check_memory()
        self.memory = []
        self.line = tok.lineno
      self.memory.append(tok)
      tok = self.clex.token()
    # note: I think it's safe not to check_memory here because of the conditions under which the loop can exit.

  def summary(self):
    return self.aliases, self.symbols

def find_dotted_ids(toks):
  in_id = False
  ids = []
  for tok in toks:
    if in_id:
      if tok.type not in ('ID','PERIOD'): in_id = False
      else: ids[-1].append(tok)
    else:
      if tok.type == 'ID':
        in_id = True
        ids.append([tok])
  return ids

def tok_compare(toks, specs):
  "toks is a list of LexToken|string. specs is a list of strings. return bool indicating whether they're the same"
  if len(toks) != len(specs): return False
  for tok, spec in zip(toks, specs):
    if tok == spec: continue # string comparison, like for '@'
    if spec.isupper() and tok.type == spec: continue # LexToken.type (only for UPPERCASE strings)
    if tok.value == spec: continue # LexToken.value
    return False
  return True

def pretralp():
  parser = argparse.ArgumentParser(description="pretralp is the 'pre-transformation lexer pass' for cbuns. this pre-pre-pre-processes C files, i.e. collects information on @import stmts and symbol use")
  parser.add_argument('path', help='path of file to pretralp')
  args = parser.parse_args()
  tralper = Tralper()
  tralper.process(open(args.path).read())
  print tralper.summary()

def imex():
  parser = argparse.ArgumentParser(description="imex is the 'import exports' process for cbuns. this analyzes the package and the used symbols and prints the extern & typedefs that would be inserted in place of @import")
  parser.add_argument('package', help='path to package.json')
  parser.add_argument('symbols', help='comma-separated list of symbols; e.g. "pkg.subpkg.function_name,pkg.function2" (leave out the quotes, but pkg prefix necessary)')
  args = parser.parse_args()

  symbols = [tuple(sym.split('.')) for sym in args.symbols.split(',')]
  raise NotImplementedError

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
