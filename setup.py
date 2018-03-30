from distutils.core import setup

setup(
    name='COGDumper',
    version='0.1dev',
    packages=['cogdumper', ],
    long_description=open('README.md').read(),
    install_requires=['boto3>=1.6.2', 'click>=6.7', 'requests>=2.18.4'],
    extras_require={
        'test': ['pytest', 'pytest-cov', 'codecov']}
)
