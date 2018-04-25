"""Setup."""
from setuptools import setup, find_packages

# Parse the version from the pxmcli module.
with open('cogdumper/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue

inst_reqs = ['boto3>=1.6.2', 'click>=6.7', 'requests>=2.18.4']
extra_reqs = {'test': ['pytest', 'pytest-cov', 'codecov']}

setup(
    name='cogdumper',
    version=version,
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    python_requires='>=3',
    keywords='CloudOptimized Geotiff',
    url='https://github.com/mapbox/COGDumper',
    classifiers=[
      'Intended Audience :: Information Technology',
      'Intended Audience :: Science/Research',
      'Programming Language :: Python :: 3.6',
      'Topic :: Scientific/Engineering :: GIS'],
    author=u"Norman Barker",
    author_email='norman.barker@mapbox.com',
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=inst_reqs,
    extras_require=extra_reqs,
    entry_points={
      'console_scripts': [
        'cogdumper = cogdumper.scripts.cli:cogdumper'
      ]
    }
)
