from setuptools import setup, find_packages


install_requires = ['six']

setup(
    name='pre_commit_apiary',
    version='0.0.1.a1',
    author='Arsenal_49',
    packages=find_packages('.', exclude=('tests*', 'testing*')),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'validate_apiary = pre_commit_hook.validate:validate'
        ]
    }
)
