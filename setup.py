from pathlib import Path

from setuptools import setup, find_packages

here = Path(__file__).parent.resolve()
readme = (here / 'README.md').read_text(encoding='utf-8')
repo = 'https://github.com/joniumGit/dnsmule'
version = (here / 'src' / 'dnsmule' / '__init__.py').read_text(encoding='utf-8')
version = version.strip().splitlines(keepends=False).pop().split('=')[1].strip(" '")

# https://pypi.org/classifiers/
setup(
    name='dnsmule',
    version=version,
    url=repo,
    long_description=readme,
    license='MIT',
    description='Rule based dependency scanning and service fingerprinting via DNS',
    long_description_content_type='text/markdown',
    author='joniumGit',
    author_email='52005121+joniumGit@users.noreply.github.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Internet',
    ],
    keywords='DNS, Dependency, DNSMule',
    package_dir={
        '': 'src',
    },
    packages=find_packages(
        where='src',
        include=(
            'dnsmule',
            'dnsmule.*',
        )
    ),
    python_requires='>=3.7',
    install_requires=[
        'pyyaml',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'redis',
            'pymongo',
            'dnspython',
        ],
        'full': [
            'redis',
            'pymongo',
            'dnspython',
        ],
    },
    project_urls={
        'Bug Reports': f'{repo}/issues',
        'Source': repo,
    },
)
