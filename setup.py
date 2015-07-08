from setuptools import setup, find_packages


install_requires = []

setup(
    name='pre_commit_apiary',
    version='0.0.1.a1',
    author='Arsenal_49',
    packges=find_packages('.', exclude=('tests*', 'testing*')),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'validate_apiary = pre_commit_hook.validate:validate'
        ]
    }
)