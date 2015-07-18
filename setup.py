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
      'cbuns-pretralp=cbuns.steps.transform:pretralp'
    ],
  },
  packages=setuptools.find_packages(),
  install_requires=[
    'pycparser',
  ],
)
