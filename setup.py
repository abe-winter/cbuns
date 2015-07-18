import setuptools

setuptools.setup(
  name='cbuns',
  version='0.0.1',
  description='a package manager for C',
  classifiers=[
  ],
  keywords=['c','compiler','transpiler','package management'],
  author='Abe Winter',
  author_email='abe-winter@users.noreply.github.com',
  url='https://github.com/abe-winter/cbuns',
  license='MIT',
  entry_points={
    'console_scripts':[
      'cbuns-build=cbuns.commands.build:main',
      'cbuns-trex=cbuns.steps.transform:trex'
    ],
  },
  packages=setuptools.find_packages(),
  install_requires=[
    'pycparser',
  ],
)
