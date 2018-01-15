from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='pyIotThingsSrv',
    version='0.0.1',
    license='MIT',
    url='https://github.com/sourceperl/iot.things.srv',
    platforms='any',
    install_requires=required,
    scripts=[
        'scripts/iot-http-srv'
    ]
)
