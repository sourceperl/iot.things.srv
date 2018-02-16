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
    packages=[
        'thingview'
    ],
    include_package_data=True,
    zip_safe=False,
    scripts=[
        'scripts/iot-http-srv',
        'scripts/iot-dispatcher-srv',
        'scripts/iot-tx-pulse-srv',
        'scripts/iot-mongodump-srv',
        'scripts/iot-thingview-srv',
        'scripts/iot_check_index'
    ]
)
