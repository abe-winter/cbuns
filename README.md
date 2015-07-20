## cbuns

cbuns is a package manager & pre-preprocessor for C. It adds an `@import` statement for C files and provides tooling.

## why

C is ubiquitous but limited package management supports creates a number of bad effects for systems building on top of it:
1. bad modularity of code, especially for large projects.
1. every C library you use introduces a dpkg (or yum, or rpm) dependency for your program
1. no central listing of C packages contributes to issues like heartbleed and lack of community support for critical libraries
1. C builds are all nonstandard and complicated, especially on non-unix platforms.

cbuns aims to standardize builds, replacing autoconf & makefiles for some applications. Building a small & medium C project on a platform with cbuns support should be brainless. Large projects may not be as tractable, but will hopefully be able to use some of the build infrastructure.

## how

A `package.json` for your C library defines build targets (both entry points and libraries) and exported symbols ([library package.json](examples/pkgfunc/package.json), [entry point package.json](examples/consumer/package.json)).

The [`cbuns-build`](cbuns/commands/build.py) command locates `@import` commands and replaces them with `extern` declarations by parsing your code & its dependencies. The 'real C' that's produced from that pre-preprocessor is then fed to a compiler.

cbuns automatically declares exports (using `package.json`) and uses name-mangling (`cbuns_package_sourcefile_symbol`) to provide namespacing for imported symbols.

cbuns is written for python 2.7.

## status

There's a lot on our [roadmap](docs/roadmap.md) but for now we support:
* static libraries
* simple codebases

## getting started

```python
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
