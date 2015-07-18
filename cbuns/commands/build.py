"""build.py coordinates the creation of static libs, dynamic libs and executables.
It uses the helers in cbuns/steps.
"""

import argparse, json, os, subprocess, shutil, hashlib

def ensure_dir(*paths):
  path = os.path.join(*paths)
  if not os.path.exists(path):
    os.makedirs(path)
  if not os.path.isdir(path):
    raise TypeError("%r is not a directory" % path)
  return path

BUILD_DIR = '.build' # todo: look up from config instead

def build_slib(pkgdir):
  jpack = json.load(open(os.path.join(pkgdir, 'package.json')))
  build_dir = ensure_dir(pkgdir, BUILD_DIR, 'real-c')
  c_files = []
  for dirname, subdirs, files in os.walk(pkgdir):
    if any(d != '.' and d.startswith('.') for d in dirname.split(os.path.sep)):
      continue # don't recurse into dotted dirs
    if any(f.endswith('.c') or f.endswith('.h') for f in map(str.lower, files)):
      copy_to = ensure_dir(build_dir, dirname)
      print 'todo: translate', copy_to, files
      for f in files:
        if f.lower().endswith('.c') or f.lower().endswith('.h'):
          shutil.copy2(os.path.join(dirname, f), copy_to)
        if f.lower().endswith('.c'):
          c_files.append(os.path.join(dirname, f))
  version_hash = hashlib.md5(subprocess.check_output(['gcc','--version'])).digest().encode('hex')
  lib_dir = ensure_dir(pkgdir, BUILD_DIR, 'slib-gcc-' + version_hash)
  subprocess.check_output(['gcc', '-c'] + c_files + ['-o', os.path.join(lib_dir, 'slib.o')])
  libname = os.path.split(os.path.abspath(pkgdir))[-1]
  subprocess.check_output(['ar','rcs',os.path.join(lib_dir, 'lib' + libname + '.a'),os.path.join(lib_dir, 'slib.o')])
  raise NotImplementedError # resume here

def build_target(pkgdir, target):
  raise NotImplementedError # resume

def main():
  "entry point (defined in setup.py)"
  parser = argparse.ArgumentParser(description='build libs & executables')
  parser.add_argument('package_name', help='. means ./package.json. otherwise pass the name of something in cbuns_modules or global? hmm')
  parser.add_argument('target', help='.slib, .dlib, * or the name of an entry-point. default *. entry-points starting with . need to be ".quoted", for example ".slib" can be the name of a custom entry point and won\'t be confused with .slib', default='*')
  parser.add_argument('--compiler', default='gcc')
  args = parser.parse_args()

  if args.package_name != '.': raise NotImplementedError
  if args.compiler != 'gcc': raise NotImplementedError

  if args.target == '.slib':
    build_slib(args.package_name)
  elif args.target == '.dlib': raise NotImplementedError
  else:
    build_target(args.package_name, args.target)

