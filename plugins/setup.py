from pathlib import Path

from setuptools import setup, find_packages

here = Path(__file__).parent.resolve()
readme = (here / 'README.md').read_text(encoding='utf-8')
repo = 'https://github.com/joniumGit/dnsmule'
version = (here / 'src' / 'dnsmule_plugins' / '__init__.py').read_text(encoding='utf-8')
version = version.strip().splitlines(keepends=False).pop().split('=')[1].strip(" '")

# https://pypi.org/classifiers/
setup(
    name='dnsmule-plugins',
    version=version,
    url=repo,
    long_description=readme,
    license='MIT',
    description='Plugins for DNSMule',
    long_description_content_type='text/markdown',
    author='joniumGit',
    author_email='52005121+joniumGit@users.noreply.github.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Internet',
    ],
    keywords='DNS, Dependency, IP, Cloud',
    package_dir={
        '': 'src',
    },
    packages=find_packages(
        where='src',
        include=(
            'dnsmule_plugins',
            'dnsmule_plugins.*',
        )
    ),
    python_requires='>=3.7',
    install_requires=[
        'dnsmule',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'cryptography',
        ],
        'full': [
            'cryptography',
        ]
    },
    project_urls={
        'Bug Reports': f'{repo}/issues',
        'Source': repo,
    },
)
