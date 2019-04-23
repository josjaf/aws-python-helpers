from distutils.core import setup

setup(
    name='newport_helpers',
    version='0.1dev',
    packages=['stacker_custom','helpers', 'stacker_custom/destroy_hooks', 'stacker_custom/hooks', 'stacker_custom/lookups'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    author='josjaf',
    author_email='josjaf@gmail.com',
    # install_requires=[
    #     'boto3',
    #     'botocore'
    # ],
    #url='https://gitlab.com/josjaf/newport_helpers/',
)