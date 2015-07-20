import setuptools

setuptools.setup(
  name='cbuns',
  version='0.0.1',
  description='a package manager for C',
  classifiers=[
    'Programming Language :: C',
    'Topic :: System :: Archiving :: Packaging',
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Compilers',
    'Topic :: Software Development :: Code Generators',
    'Topic :: Software Development :: Pre-processors',
  ],
  keywords=['c','compiler','transpiler','package management'],
  author='Abe Winter',
  author_email='abe-winter@users.noreply.github.com',
  url='https://github.com/abe-winter/cbuns',
  license='MIT',
  entry_points={
    'console_scripts':[
      'cbuns-build=cbuns.commands.build:main',
      'cbuns-pretralp=cbuns.steps.pretralp:main',
      'cbuns-imex=cbuns.steps.imex:main',
      'cbuns-transform=cbuns.steps.transform:main',
      'cbuns-depgraph=cbuns.steps.depgraph:main',
      'cbuns-run=cbuns.commands.run:main',
    ],
  },
  packages=setuptools.find_packages(),
  install_requires=[
    'pycparser',
    'networkx',
    'path.py',
    'ply',
  ],
)
