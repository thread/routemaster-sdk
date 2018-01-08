from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='routemaster_sdk',
    version='0.0.1',
    url='https://github.com/thread/routemaster_sdk',
    description="SDK for Routemaster (state machines as a service).",
    long_description=long_description,

    author="Thread",
    author_email="tech@thread.com",

    keywords=(
    ),
    license='MIT',

    packages=find_packages(),
    include_package_data=True,

    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business',
    ),

    install_requires=(
        'requests',
    ),

    setup_requires=(
        'pytest-runner',
    ),

    tests_require=(
        'pytest',
        'tox',
        'pytest-cov',
    ),
)
