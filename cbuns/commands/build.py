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

def compiler_version(compiler):
  if compiler == 'gcc':
    version = subprocess.check_output(['gcc','--version'])
  else:
    raise ValueError('unk compiler', compiler)
  return hashlib.md5(version).digest().encode('hex')

def slib_dir(compiler):
  # todo: this needs an architecture hash as well as compiler version
  return 'slib-%s-%s' % (compiler, compiler_version(compiler))

def hidden_dir(d):
  return d not in ('.','..') and d.startswith('.')

def transform(pkgdir, main_file=None):
  jpack = json.load(open(os.path.join(pkgdir, 'package.json')))
  build_dir = ensure_dir(pkgdir, BUILD_DIR, 'real-c')
  c_files = []
  for dirname, subdirs, files in os.walk(pkgdir):
    if any(hidden_dir(d) for d in dirname.split(os.path.sep)):
      continue # don't recurse into dotted dirs
    if any(f.endswith('.c') or f.endswith('.h') for f in [f_.lower() for f_ in files]):
      copy_to = ensure_dir(build_dir, dirname)
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

def build_slib(pkgdir):
  print 'slib', pkgdir
  c_files = transform(pkgdir)
  lib_dir = ensure_dir(pkgdir, BUILD_DIR, slib_dir('gcc'))
  ofile = os.path.join(lib_dir, 'slib.o')
  subprocess.check_output(['gcc', '-c'] + c_files + ['-o', ofile])
  libname = os.path.split(os.path.abspath(pkgdir))[-1]
  subprocess.check_output(['ar','rcs',os.path.join(lib_dir, 'lib' + libname + '.a'),ofile])

def build_target(pkgdir, target):
  jpack = json.load(open(os.path.join(pkgdir, 'package.json')))
  libdirs = []
  libnames = []
  for dep in jpack['deps']:
    # todo: config whether to make dlibs or slibs? dlibs are only interesting for expensive global deps.
    # todo: convert dirs to a type so that global dep vs path dep is easier to manage
    build_slib(dep)
    libdirs.append(os.path.join(dep, BUILD_DIR, slib_dir('gcc')))
    libnames.append(os.path.split(dep)[-1])
  c_files = transform(pkgdir, jpack['main'][target])
  # todo: this needs an architecture hash as well as version
  build_dir = ensure_dir(pkgdir, BUILD_DIR, 'target-%s-%s' % (target, compiler_version('gcc')))
  subprocess.check_output(['gcc'] + c_files + ['-L'+ld for ld in libdirs] + ['-l'+lib for lib in libnames] + ['-o',os.path.join(build_dir,target)])

def main():
  "entry point (defined in setup.py)"
  parser = argparse.ArgumentParser(description='build libs & executables')
  parser.add_argument('package_name', help='. means ./package.json. otherwise pass the name of something in cbuns_modules or global? hmm')
  parser.add_argument('target', help='.slib, .dlib, * or the name of an entry-point. default *. entry-points starting with . need to be ".quoted", for example ".slib" can be the name of a custom entry point and won\'t be confused with .slib')
  parser.add_argument('--compiler', default='gcc')
  args = parser.parse_args()

  if args.package_name != '.': raise NotImplementedError
  if args.compiler != 'gcc': raise NotImplementedError

  if args.target == '.slib':
    build_slib(args.package_name)
  elif args.target == '.dlib': raise NotImplementedError
  else:
    build_target(args.package_name, args.target)

