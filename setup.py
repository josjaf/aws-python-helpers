from distutils.core import setup
import glob

setup(
    name='newport_helpers',
    version='0.102',
    packages=['stacker_custom', 'newport_helpers', 'stacker_custom/destroy_hooks', 'stacker_custom/hooks',
              'stacker_custom/lookups', 'stacker_custom/hooks/post', 'stacker_custom/stacker_blueprints',
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
