"transform.py -- this ingests 'cbuns code' (C with @import) at the lex level and transforms"

import argparse, os, shutil, json
from .. import pkg

def transform(pkgdir, main_file=None):
  "copy all the non-main C & H files to pkg/.build, as well as 0 or 1 main files (main_file arg)"
  jpack = json.load(open(os.path.join(pkgdir, 'package.json')))
  build_dir = pkg.util.ensure_dir(pkgdir, pkg.util.BUILD_DIR, 'real-c')
  c_files = []
  for dirname, subdirs, files in os.walk(pkgdir):
    if any(pkg.util.hidden_dir(d) for d in dirname.split(os.path.sep)):
      continue # don't recurse into dotted dirs
    if any(f.endswith('.c') or f.endswith('.h') for f in [f_.lower() for f_ in files]):
      copy_to = pkg.util.ensure_dir(build_dir, dirname)
      print 'todo: translate', copy_to, files
      for f in files:
        # warning: join() != file isn't saying they're not the same. platform slash type etc.
        # warning: this isn't nesting aware, it's making file names global.
        if f in jpack.get('main', ()) and f != main_file:
          continue
        if f.lower().endswith('.c') or f.lower().endswith('.h'):
          shutil.copy2(os.path.join(dirname, f), copy_to)
        if f.lower().endswith('.c'):
          c_files.append(os.path.join(dirname, f))
  return c_files

def main():
  parser = argparse.ArgumentParser(description='transform a C file with @imports to straight C')
  parser.add_argument('package', help='path to package.json (necessary because it defines exports)')
  parser.add_argument('path', help='path of input file')
  parser.add_argument('-o', '--out', help='path to output. if a folder, use same filename as input. if not given, use stdout')
  args = parser.parse_args()

  # 1. tralp the thing
  # 2. get exports
  # 3. write with interpolation -- we're going to want line & slice of each substitution from symbols, and line for import stmts
  raise NotImplementedError
