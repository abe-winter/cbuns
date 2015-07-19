"transform.py -- this ingests 'cbuns code' (C with @import) at the lex level and transforms"

import argparse, os, shutil, json, glob, collections, path
from .. import pkg
from . import pretralp

def transform_file(jpack, path):
  "transform a single file"
  tralper = Tralper()
  tralper.process(open(path).read())
  aliases, symbols = tralper.summary() # todo: this needs slices
  unk_paths = set(aliases.values()) - set(jpack['deps'])
  extra_paths = set(jpack['deps']) - set(aliases.values())
  if extra_paths:
    print 'warning: packages in package.deps never used in @import()', extra_paths
  if unk_paths:
    raise ValueError('undeclared imports', unk_paths)
  raise NotImplementedError # now for each dep, parse its transformed .build/c (i.e. run imex on it)
  raise NotImplementedError # sub in changes, write output

def lib_globs(jpack, target_type, target, seen_libs=None):
  "return union of globs. assume transform_pkg already checked target_type. recursive, emits PackageError if deps are cyclic"
  seen_libs = seen_libs or set()
  if (target_type, target) in seen_libs:
    raise pkg.util.PackageError('cycle in lib_globs', (target_type, target))
  seen_libs.add((target_type, target))
  spec = jpack[target_type][target]
  return sorted(set(sum(
    [spec.get('globs', [])] + [lib_globs(jpack, 'lib', lib, seen_libs) for lib in spec.get('libs', [])],
    []
  )))

# path is relative path from CWD (i.e. join(base, tail)).
# tail gets appended to .build/c, for a result of e.g. .build/c/src/sub/file.c
RelativeGlob = collections.namedtuple('RelativeGlob', 'path base tail')

def relative_glob(basedir, glob_string):
  "return list of RelativeGlob tuples"
  # the path.Path contextmanager changes directory then rolls it back
  with path.Path('.') / basedir as subdir:
    return [
      RelativeGlob(os.path.join(basedir, relpath), basedir, relpath)
      for relpath in glob.glob(glob_string)
    ]

def collect_globs(pkgdir, globs):
  "return list of unique paths pointed to by globs"
  return set(
    path
    for glob_string in globs
    for path in relative_glob(pkgdir, glob_string)
  )

def transform_pkg(pkgdir, target_type, target):
  """copy all the non-main C & H files to pkg/.build, as well as 0 or 1 main files (main_file arg).
  return c_files, a list of relative paths to C files in build dir (i.e. the list of sources to compile).
  """
  if target_type not in ('lib','main'):
    raise ValueError('unk target_type', target_type)
  jpack = json.load(open(os.path.join(pkgdir, 'package.json')))
  
  build_dir = pkg.util.ensure_dir(pkgdir, pkg.util.BUILD_DIR, 'real-c')
  paths = collect_globs(pkgdir, lib_globs(jpack, target_type, target))
  # note: glob will ignore .build by default because it ignores dotted dirs unless explicitly provided
  c_files = []
  for rglob in paths:
    print 'todo translate:', rglob
    dest = os.path.join(build_dir, rglob.tail)
    shutil.copy2(rglob.path, dest)
    if dest.lower().endswith('.c'):
      c_files.append(dest)
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
