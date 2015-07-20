"utilities for working with packages (including directory manipulation)"

import os, hashlib, subprocess

BUILD_DIR = '.build' # todo: look up from config instead so this can be in /tmp or whatever, as the user needs
REAL_C_DIR = 'real-c'

class PackageError(StandardError): "errors relating to package defs"

def ensure_dir(*paths):
  path = os.path.join(*paths)
  if not os.path.exists(path):
    os.makedirs(path)
  if not os.path.isdir(path):
    raise TypeError("%r is not a directory" % path)
  return path

def compiler_version(compiler):
  if compiler == 'gcc':
    version = subprocess.check_output(['gcc','--version'], stderr=subprocess.STDOUT)
  else:
    raise ValueError('unk compiler', compiler)
  return hashlib.md5(version).digest().encode('hex')

def slib_dir(compiler):
  # todo: this needs an architecture hash as well as compiler version
  return 'slib-%s-%s' % (compiler, compiler_version(compiler))

def hidden_dir(d):
  return d not in ('.','..') and d.startswith('.')

def std_include_paths(compiler):
  "return list of standard include paths"
  # warning: I think this is for the aliased LLVM on osx
  # warning: parsing human-readable output is a disaster
  if compiler != 'gcc': raise ValueError('unk compiler', compiler)
  # note: no idea what the GCC args are below
  proc = subprocess.Popen(['gcc','-xc','-E','-v','-'], stdin=subprocess.PIPE, stdout=open(os.devnull, 'w'), stderr=subprocess.PIPE)
  proc.stdin.close()
  res = proc.stderr.read().splitlines()
  proc.wait()
  active = False
  includes = []
  for line in res:
    if active:
      if line.startswith('End of search list.'):
        active = False
      elif not line.startswith('#'):
        # strip because of indent, split because of stuff like '/System/Library/Frameworks (framework directory)'
        includes.append(line.strip().split()[0])
    elif line.startswith('#include'):
      active = True
  return includes
