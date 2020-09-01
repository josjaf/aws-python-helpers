from distutils.core import setup
import glob

setup(
    name='newport_helpers',
    version='0.103',
    packages=['newport_helpers/',
              ],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    author='josjaf',
    author_email='josjaf@gmail.com',
    # install_requires=[
    #     'boto3>=1.9.134',
    #     'botocore>=1.12.134',
    #     'jmespath>= 0.9.4'
    #     'GitPython>=2.1.11'
    # ],
    # url='https://gitlab.com/josjaf/newport_helpers/',
)
