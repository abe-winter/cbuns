### roadmap for cbuns

1. fully qualified export names including version (hijack .o symbol table with pybfd).
1. factor out the substitution phase of transform.transform_file and fix its many flaws. this involves tralper improvements too.
1. create extern declarations for vars and types (not just functions) and automatically import types when used in a function. __PATH__ magic var for accessing datafiles.
1. multi-layer dependencies (libraries rely on other libraries), composed at the end (rather than .a file with 10 other .a files mashed into it)
1. factor out compiler features (preferably using the existing wrappers in setuptools / distutils, maybe in SCons):
  - builtin types
  - std include dirs
  - command line invocation & flags
1. import a small but real codebase; zlib
1. IPO (0.0.2)
1. am I using the package.exports field? use it or get rid of it.
1. treecompare with hashes.json instead of 'rebuild everything & pray no files were deleted'
1. nail down import path spec, including support for global installs & package versioning
1. release 0.0.3
1. @include() variant of #include. cbuns subs in the path and links object code.

### future goals
* easy cross-compilation, including fancy outputs like [rump](https://github.com/rumpkernel/rumprun) and [buildroot](http://buildroot.uclibc.org/)
* central web-based package manager with cloud builds and tests
* reproducible builds (byte-for-byte binaries)
* build easy exporters to high-level language FFI
* consider integration with LLVM or GCC (for better positioning in the parsing pipeline)
* support tcc for fast startup
* dynamic libs instead of static-everything
* instrumented builds for profiling & coverage

### package shortlist

* zlib and cloudflare fast zlib
* curses
* json & yaml
* sqlite or leveldb
* duktape or lua
* some kind of JIT generator
* LEX/YACC & an AST / tree-transformation module
* standard test collector
* an std lib (especially a small one) so we can eliminate #include <stdio> for a lot of cases
* libunwind

### package longlist

These are packages that aren't necessarily easy to adapt but would be nice to have or cool proof-of-concept projects.

* a linter that can handle @import (reach goal)
* a DSU system like kitsune
* kernel for a small OS like minix or busybox
* proof-of-concept build of a language (I favor python for the circularity)
* https://h2o.examp1e.net/faq.html#libh2o
  - which depends libuv and openssl
