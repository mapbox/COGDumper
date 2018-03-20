from distutils.core import setup

setup(
    name='COGDumper',
    version='0.1dev',
    packages=['cogdumper', ],
    long_description=open('README.md').read(),
    install_requires=open('requirements.txt').read().splitlines()
)
