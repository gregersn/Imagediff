from setuptools import setup, find_packages
setup(
    name='imagediff',
    version='1.0.0.dev1',
    description='A utility to compare folders of images',
    url='TBD',
    author='Greger Stolt Nilsen',
    author_email='dev@gregerstoltnilsen.net',
    license='MIT',
    packages=find_packages(include=['imagediff']),
    install_requires=['Pillow>=8.3.2', 'PyQt5>=5.15.4', 'Click>=8.0.1'],
    python_requires='>=3',
    scripts=['bin/imagediff']
)
