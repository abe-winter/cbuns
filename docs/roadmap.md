### roadmap for cbuns

1. fully qualified export names (need to work with libtool to make this happen).
1. factor out the substitution phase of transform.transform_file and fix its many flaws. this involves tralper improvements too.
1. create extern declarations for vars and types (not just functions) and automatically import types when used in a function. __PATH__ magic var for accessing datafiles.
1. factor out compiler features (preferably using the existing wrappers in setuptools / distutils):
  - builtin types
  - std include dirs
  - command line invocation & flags
1. import a small but real codebase; zlib
1. am I using the package.exports field? use it or get rid of it.
1. dynamic libs instead of static-everything

### future goals
* easy cross-compilation, including stuff like [rump](https://github.com/rumpkernel/rumprun) and [buildroot](http://buildroot.uclibc.org/)
* central web-based package manager with cloud builds and tests
* reproducible builds
* build easy exporters to high-level language FFI
* be a layer on LLVM or GCC (for better positioning in the parsing pipeline)
* support tcc for fast startup

### package shortlist

* duktape or lua
* zlib and cloudflare fast zlib
* some kind of JIT generator
* any AST module
* curses
* standard test collector
* sqlite or leveldb
* json & yaml
* alternative std libs (including small ones)

### package longlist

These are packages that aren't low-hanging-fruit to adapt but would be nice to have.

* a linter that can handle @import (reach goal)
* libunwind
* a DSU system like kitsune
* a small OS like minix or busybox
* libuv (may be tough because of platform issues, lots of #ifdef blocks)
* proof-of-concept build of a language (I favor python for the circularity)
* a web server (openresty?)
