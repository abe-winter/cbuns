"transform.py -- this ingests 'cbuns code' (C with @import) at the lex level and transforms"

import argparse, os, shutil, json, glob, collections, path
from .. import pkg
from . import pretralp, imex

# ImportSlice = collections.namedtuple('ImportSlice', 'path line slice')
# SymbolSlice = collections.namedtuple('SymbolSlice', 'symbol line slice')

def line_lookup(aliases, symbols):
  # warning: duplicate @import statements ruin this. raise an error in tralper.
  line2slice = collections.defaultdict(list)
  for alias, import_slice in aliases.items():
    # replace relative path with alias so we can look up extern lines
    line2slice[import_slice.line].append(import_slice._replace(path=alias))
  for symbol_slice in symbols:
    line2slice[symbol_slice.line].append(symbol_slice)
  return line2slice

def merge_slice(string, slice, interp):
  "return string replaced with interp at slice"
  return string[:slice.start] + interp + string[slice.stop:]

def transform_file(pkgdir, jpack, source, dest):
  """transform a single file. write converted source to dest. if dest is None, print result.
  returns bool indicating if file was transformed (True) or just copied (False).
  """
  tralper = pretralp.Tralper()
  tralper.process(open(source).read())
  aliases, symbols = tralper.summary() # todo: this needs slices
  unk_paths = set(val.path for val in aliases.values()) - set(jpack['deps'])
  if unk_paths:
    raise ValueError('undeclared imports', unk_paths)
  if not aliases:
    if dest is None: print open(source).read()
    else: shutil.copy2(source, dest)
    return False
  if len(aliases) != len(set(val.path for val in aliases.values())):
    raise ValueError('looks like duplicate aliases', aliases.values())
  lookup = {
    alias: imex.Imexer(
      os.path.join(pkgdir, path.path, 'package.json')
    ).find(
      {symbol.symbol for symbol in symbols if symbol.symbol[0] == alias}
    ) for alias, path in aliases.items()
  }
  line2slice = line_lookup(aliases, symbols)
  out = ''
  for i, line in enumerate(open(source)):
    if i in line2slice:
      if len(line2slice[i]) != 1: raise NotImplementedError('support multi-slice')
      slice_, = line2slice[i]
      if isinstance(slice_, pretralp.ImportSlice):
        # dedup because pkg.file.name and pkg.name can generate dupes
        # warning: this is replacing the whole line. lexpos doesn't do what I thought.
        out += '\n'.join(sorted(set(decl.line for decl in lookup[slice_.path].values()))) + '\n'
      elif isinstance(slice_, pretralp.SymbolSlice):
        # warning: this is way bad. there could be a copy of this in a string literal and we're dead
        out += line.replace('.'.join(slice_.symbol), slice_.symbol[-1])
      else:
        raise TypeError('unk type', type(slice_), slice_)
    else:
      out += line
  if dest is None: print out
  else: open(dest, 'w').write(out)
  return True

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
  
  build_dir = pkg.util.ensure_dir(pkgdir, pkg.util.BUILD_DIR, pkg.util.REAL_C_DIR)
  paths = collect_globs(pkgdir, lib_globs(jpack, target_type, target))
  # note: glob will ignore .build by default because it ignores dotted dirs unless explicitly provided
  c_files = []
  for rglob in paths:
    dest = os.path.join(build_dir, rglob.tail)
    transform_file(pkgdir, jpack, rglob.path, dest)
    if dest.lower().endswith('.c'):
      c_files.append(dest)
  return c_files

def main():
  parser = argparse.ArgumentParser(description='transform a C file with @imports to straight C')
  parser.add_argument('pkgdir', help='path to package')
  parser.add_argument('path', help='path of input file')
  parser.add_argument('-o', '--out', help='path to output. if a folder, use same filename as input. if not given, use stdout')
  args = parser.parse_args()

  transform_file(args.pkgdir, json.load(open(os.path.join(args.pkgdir, 'package.json'))), args.path, args.out)
