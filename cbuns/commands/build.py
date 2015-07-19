"""build.py coordinates the creation of static libs, dynamic libs and executables.
It uses the helpers in cbuns/steps.
"""
# todo: all subprocess invocations of compilers should be wrapped in classes; I assume there are py libs to do this already.

import argparse, json, os, subprocess, shutil, hashlib
from .. import pkg, steps

def build_slib(pkgdir):
  c_files = steps.transform.transform(pkgdir)
  lib_dir = pkg.util.ensure_dir(pkgdir, pkg.util.BUILD_DIR, pkg.util.slib_dir('gcc'))
  ofile = os.path.join(lib_dir, 'slib.o')
  subprocess.check_output(['gcc', '-c'] + c_files + ['-o', ofile])
  libname = os.path.split(os.path.abspath(pkgdir))[-1]
  # todo: ensure this matches jpack.name
  subprocess.check_output(['ar','rcs',os.path.join(lib_dir, 'lib' + libname + '.a'),ofile])

def build_target(pkgdir, target):
  jpack = json.load(open(os.path.join(pkgdir, 'package.json')))
  libdirs = []
  libnames = []
  for dep in jpack['deps']:
    # todo: config whether to make dlibs or slibs? dlibs are only interesting for expensive global deps.
    # todo: convert dirs to a type so that global dep vs path dep is easier to manage
    build_slib(dep)
    libdirs.append(os.path.join(dep, pkg.util.BUILD_DIR, slib_dir('gcc')))
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

  if args.compiler != 'gcc': raise NotImplementedError

  if args.target == '.slib':
    build_slib(args.package_name)
  elif args.target == '.dlib': raise NotImplementedError
  else:
    build_target(args.package_name, args.target)

