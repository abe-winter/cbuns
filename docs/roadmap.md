### short-term roadmap for cbuns

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
1. release 0.0.4
1. learn about autoconf and support a shortlist of its features
1. release 0.1.0

### future goals
* easy cross-compilation, including fancy outputs like [rump](https://github.com/rumpkernel/rumprun) and [buildroot](http://buildroot.uclibc.org/)
* central web-based package manager with cloud builds and tests
* test & support debuggers
* reproducible builds (byte-for-byte binaries)
* build easy exporters to high-level language FFI
* consider integration with LLVM or GCC (for better positioning in the parsing pipeline)
* dynamic libs
* instrumented builds for profiling & coverage
* support substitution of @argname function parameters for limited templating (duck typing). example: `int whatever[@type, @method](@type val);`. `@method` can be specialized to `@struct` so you're not compromising type safety. choose syntax that breaks parsing the least.
* `package.pp` field to specify third-party preprocessors (preprocessors also have to be declared in `package.deps`).
  * (todo: check out some research on compositional safety of languages).
  * with `#include` deprecated, even the default preprocessor can be disabled for many codebases (what about comments)
  * projects (example: QT) have had adoption issues in C++ because of the pain of its custom preprocessor
  * Many projects have specialized static checking needs (for example, reference correctness for python C extensions)
  * Including custom preprocessing as part of the standard build, installable like a library, can enable many advanced applications in C that used to require a higher-level language.
  * an ast-aware preprocessor is a natural way to implement an auto test-discovery system
  * rust has compiler plugins http://doc.rust-lang.org/nightly/book/compiler-plugins.html
* variable-length variable-type arglist instead of varargs (i.e. function receives an array object)
* platform-specific symlinks (i.e. platform.c links to platform-debian.c) as a replacement for #ifdef wackiness
* safety-enhanced compilers
  * SafeStack http://dslab.epfl.ch/proj/cpi/
  * http://www.barnowl.org/research/rc/
* https://hardenedbsd.org/article/shawn-webb/2015-07-06/announcing-aslr-completion

### package shortlist

* zlib
* ncurses
* json & yaml
* easiest of: sqlite, leveldb, vedis
* postgres & redis client
* duktape or lua
* LEX/YACC
* standard test collector
* provide one or more C standard libraries (especially the small ones) so we can eliminate `#include <std>` for a lot of cases
* libunwind
* linenoise
* wrapper lib for stdlib sockets
* threading, libmill (goroutines)

### package longlist

These are packages that aren't necessarily easy to adapt but would be nice to have or cool proof-of-concept projects.

* a linter that can handle `@import`/`@include`. fuzzing.
* a DSU system like [kitsune](https://github.com/kitsune-dsu) (warning: kitsune has its own compiler)
* kernel for a small OS like minix or busybox
* proof-of-concept build of a language (I favor python for the circularity)
* the [h2o webserver](https://h2o.examp1e.net/faq.html#libh2o)
  - which depends on libuv and openssl
  - openresty is another option
* the IO, layout & DOM engine of a browser (but nothing else). this would be useful for headless selenium-style testing. modular (i.e. swap out the JS system, swap out the CSS) and synchronous (for determinstic tests, for 'wait' mode).
* lda-c
* some kind of JIT generator
* an AST / tree-transformation module
* libvlc or a media library
