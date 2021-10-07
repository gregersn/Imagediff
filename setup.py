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
    install_requires=['Pillow', 'PyQt5', 'Click'],
    python_requires='>=3',
    scripts=['bin/imagediff']
)
