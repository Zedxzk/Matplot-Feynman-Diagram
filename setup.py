from setuptools import setup, find_packages

setup(
    name='feynplot',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['matplotlib', 'numpy'],
    entry_points={
        'console_scripts': ['feyncli=feynplot.cli.feyncli:main']
    }
)
