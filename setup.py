from distutils.core import setup
import glob

static = ['newport_helpers']
packages = packages = glob.glob('stacker_custom/*/')
final_packages = []
for package in packages:
    if '__pycache__' in package: continue
    final_packages.append(package)
final = static + final_packages
setup(
    name='newport_helpers',
    version='0.1dev',
    packages=final,
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    author='josjaf',
    author_email='josjaf@gmail.com',
    install_requires=[
        'boto3>=1.9.134',
        'botocore>=1.12.134',
        'jmespath>= 0.9.4'
    ],
    # url='https://gitlab.com/josjaf/newport_helpers/',
)
