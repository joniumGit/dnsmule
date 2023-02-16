from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='dnsmule',
    version='0.0.1-dev',
    description='DNS Based Dependency Detection',
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
    keywords='DNS, Dependency',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3',
    install_requires=[
        'dnspython',
        'httpx',
        # 'redis',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/joniumGit/dnsmule',
        'Source': 'https://github.com/joniumGit/dnsmule',
    },
)
