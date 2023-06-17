from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='electricity-price-forecasting_day-ahead-DNN',
    version='1.0',
    description='An open-access benchmark and toolbox for electricity price forecasting',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dodofit/electricity-price-forecasting_day-ahead-DNN',
    author='Dorian Fitton',
    author_email='fittondorian@gmail.com',
    license='GNU AGPLv3',
    python_requires='>=3.6, <4',
    install_requires=['hyperopt>=0.2', 'tensorflow>=2.2', 'scikit-learn>=0.22',
                      'pandas>=1', 'numpy>=1', 'statsmodels>=0.11',
                      'matplotlib>=3', 'scipy>=1.4', 'google-cloud-bigquery>=3.11.0'],
    packages=find_packages(include=['toolbox', 'toolbox.*']),
    classifiers=[
    'Development Status :: 3 - Alpha',

    'Intended Audience :: Science/Research',
    'Topic :: Topic :: Scientific/Engineering',

    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',

    'Programming Language :: Python :: 3']
    )


