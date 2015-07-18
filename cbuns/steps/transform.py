"transform.py -- this ingests 'cbuns code' (C with @import) at the lex level and transforms"

import pycparser, argparse

class ParsingError(StandardError): pass

class Trexer:
  "transforming lexer"
  def __init__(self):
    self.clex = pycparser.c_lexer.CLexer(self.error, self.lbrace, self.rbrace, self.type_lookup)
    self.clex.build()
    self.memory = []

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
    print self.memory

  def process(self, string):
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
    raise NotImplementedError

def tok_compare(toks, specs):
  "toks is a list of LexToken|string. specs is a list of strings. return bool indicating whether they're the same"
  if len(toks) != len(specs): return False
  for tok, spec in zip(toks, specs):
    if tok == spec: continue # string comparison, like for '@'
    if spec.isupper() and tok.type == spec: continue # LexToken.type (only for UPPERCASE strings)
    if tok.value == spec: continue # LexToken.value
    return False
  return True

def trex():
  parser = argparse.ArgumentParser(description="trex is the 'transforming lexer' for cbuns. this pre-pre-pre-processes C files, i.e. collects information on @import stmts")
  parser.add_argument('path', help='path of file to trex')
  args = parser.parse_args()
  trexer = Trexer()
  trexer.process(open(args.path).read())
  print trexer.summary()

