## cbuns

cbuns is a package manager & pre-preprocessor for C. It adds an `@import` statement for C files and provides tooling. package-aware name mangling causes the linker to do a lot of the work of dependency resolution.

## why

C is ubiquitous but limited package management supports creates a number of bad effects for systems building on top of it:
1. bad modularity of code, especially for large monolithic projects (an operating system, for example). among other things, bad modularity / versioning breaks the performance advantage of incremental builds.
1. every C library you use introduces a dpkg (or yum, or rpm) dependency for your program. or even worse, a manual user install step. or you have to package the depended library with your app.
1. no central listing of C packages contributes to issues like heartbleed (nobody knew or cared where openssl was coming from) and lack of community support for critical libraries
1. C builds are all nonstandard and complicated, especially on non-unix platforms. #include doesn't give any instructions to the linker.
1. one-letter language name is hard to search (for real)
1. preprocessor based #include means the compiler has to handle big (= slow) source files
1. with IoT and web assembly on the way, and moore's law slowing down, low level langauges will be more relevant in the next decade than the last (if the tooling can catch up)
1. hard to swap out libraries when the universe changes (for example heartbleed & openssl) because libraries often introduce complicated build requirements

cbuns aims to standardize builds, replacing autoconf & makefiles for some applications. Building a small & medium C project on a platform with cbuns support should be brainless. Large projects may not be as tractable, but will hopefully be able to use some of the build infrastructure.

There are disadvantages to cbuns as well:
1. enhanced namespacing features are backwards incompatible with traditional linking. i.e. cbuns can support `zlib.compress`, meaning `compress` is the function name, but traditionally it would be `zlib_compress`.
1. lack of support for Makefiles & other complex build systems can branch key projects if this catches on.

## how

A `package.json` for your C library defines build targets (both entry points and libraries) and exported symbols ([library package.json](examples/pkgfunc/package.json), [entry point package.json](examples/consumer/package.json)).

The [`cbuns-build`](cbuns/commands/build.py) command locates `@import` commands and replaces them with `extern` declarations by parsing your code & its dependencies. The 'real C' that's produced from that pre-preprocessor is then fed to a compiler.

cbuns automatically declares exports (using `package.json`) and uses name-mangling (`cbuns_package_version_sourcefile_symbol`) to provide namespacing for imported symbols.

cbuns is written for python 2.7.

## status

There's a lot on our [roadmap](docs/roadmap.md) but for now we support:
* static libraries
* simple codebases

## getting started

```bash
# on osx, you'll need to do this to get libiberty (required for pybfd).
# warning: this downloads code from random (and non-https) mirrors
brew reinstall https://raw.github.com/Homebrew/homebrew/7059399/Library/Formula/binutils.rb

mkdir whatever
cd whatever
virtualenv env && source env/bin/activate
pip install git+https://github.com/abe-winter/cbuns.git
# also clone the repo for access to example packages
git clone https://github.com/abe-winter/cbuns.git
cbuns-build cbuns/examples/consumer main consumer
cbuns/examples/consumer/.build/target-consumer-*/consumer
```
And you should get output like:
```
pkg1func 2
pkg1func 2
```
I tested the above on my osx laptop with gcc pointing to LLVM. Do other environments work? You be the judge.

## related projects

* http://coapp.org/news/2013-03-27-The-Long-Awaited-post.html can't tell what this is but if you're using MSVC it's a good excuse to open your MSBuild XML files
* https://fedorahosted.org/gcc-python-plugin/
* https://github.com/clibs/clib
