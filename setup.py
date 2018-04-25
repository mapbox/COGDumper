from distutils.core import setup

# Parse the version from the pxmcli module.
with open('cogdumper/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue

setup(
    name='cogdumper',
    version=version,
    packages=['cogdumper', ],
    long_description=open('README.md').read(),
    install_requires=['boto3>=1.6.2', 'click>=6.7', 'requests>=2.18.4'],
    extras_require={'test': ['pytest', 'pytest-cov', 'codecov']},
    entry_points={
      'console_scripts': [
        'cogdumper = cogdumper.scripts.cli:cogdumper'
      ]
    }
)
