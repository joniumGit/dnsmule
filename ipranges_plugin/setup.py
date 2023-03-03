from pathlib import Path

from setuptools import setup, find_packages

here = Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='dnsmule_ipranges',
    version='0.0.1',
    description='Cloud Provider IPRanges Plugin for DNSMule',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/joniumGit/dnsmule',
    author='joniumGit',
    # https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
    ],
    keywords='DNS, Dependency, IP, Cloud',
    package_dir={'': 'src'},
    packages=find_packages(where='src', include=('dnsmule_ipranges', 'dnsmule_ipranges.*')),
    python_requires='>=3',
    install_requires=[
        'dnsmule',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/joniumGit/dnsmule',
        'Source': 'https://github.com/joniumGit/dnsmule',
    },
)
