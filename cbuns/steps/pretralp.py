"pre-transformation lexer pass"

import pycparser, argparse, collections

class ParsingError(StandardError): pass

def find_dotted_ids(toks):
  "helper for check_memory"
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
    if spec.isupper() and tok.type == spec: continue # LexToken.type (only for UPPERCASE strings)
    if tok.value == spec: continue # LexToken.value
    return False
  return True

ImportSlice = collections.namedtuple('ImportSlice', 'path line slice')
SymbolSlice = collections.namedtuple('SymbolSlice', 'symbol line slice')

def mk_lextoken(type, value, lineno, lexpos):
  "because LexToken doesn't have a constructor. also why doesn't pycparser use ply from pypi?"
  tok = pycparser.ply.lex.LexToken()
  tok.type, tok.value, tok.lineno, tok.lexpos = type, value, lineno, lexpos
  return tok

def toklist2slice(toklist):
  "error if toklist is empty"
  a, b = toklist[0], toklist[-1]
  return slice(a.lexpos, b.lexpos + len(b.value))

class Tralper:
  "pre-transformation lexer pass"
  def __init__(self):
    # todo: tweak clex to supply whitespace (because we'll need to regenerate the file)
    self.clex = pycparser.c_lexer.CLexer(self.error, self.lbrace, self.rbrace, self.type_lookup)
    self.clex.build()
    self.memory = [] # line-at-a-time memory of tokens
    self.aliases = {} # {alias:ImportSlice} for each @import stmt
    self.symbols = [] # list of SymbolSlice for ID (PERIOD ID)* symbols starting with an imported alias

  def error(self, error, line, col):
    if error == "Illegal character '@'":
      # todo: instead of parsing error strings, extend the lexer
      self.memory.append(mk_lextoken('AMPERSAND', '@', line, col))
    else:
      raise ParsingError(error, line, col)

  def lbrace(self): pass
  def rbrace(self): pass

  def type_lookup(self, token):
    return False

  def check_memory(self):
    "look at the token-list for a line, grab relevant tokens"
    if tok_compare(self.memory, ('AMPERSAND', 'import', 'LPAREN', 'STRING_LITERAL', 'COMMA', 'ID', 'RPAREN', 'SEMI')):
      pkg_path = self.memory[3].value[1:-1] # i.e. strip quotes
      self.aliases[self.memory[5].value] = ImportSlice(
        pkg_path,
        self.memory[0].lineno - 1, # -1 because parsing is 1-based
        toklist2slice(self.memory)
      )
    elif tok_compare(self.memory, ('AMPERSAND', 'import', 'LPAREN', 'STRING_LITERAL', 'RPAREN', 'SEMI')):
      pkg_path = self.memory[3].value[1:-1] # i.e. strip quotes
      self.aliases[os.path.split(pkg_path)[-1]] = ImportSlice(
        pkg_path,
        self.memory[0].lineno - 1, # -1 because parsing is 1-based
        toklist2slice(self.memory)
      )
    else:
      for dotted in find_dotted_ids(self.memory):
        if dotted[0].value in self.aliases:
          self.symbols.append(SymbolSlice(
            tuple(tok.value for tok in dotted[::2]),
            dotted[0].lineno - 1, # -1 because parsing is 1-based
            toklist2slice(dotted)
          ))

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

def main():
  "called via setup.py entry-point"
  parser = argparse.ArgumentParser(description="pretralp is the 'pre-transformation lexer pass' for cbuns. this pre-pre-pre-processes C files, i.e. collects information on @import stmts and symbol use")
  parser.add_argument('path', help='path of file to pretralp')
  args = parser.parse_args()
  tralper = Tralper()
  tralper.process(open(args.path).read())
  print tralper.summary()
