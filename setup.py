from distutils.core import setup
setup(name='thresholdmailhandler',
    version='1.0',
    description="Python logging handler that will buffer message logs and bulk email the buffer if a log level is reached or exceeded",
    author="Liviu Manea",
    url="https://github.com/mlmarius/thresholdmailhandler",
    license="MIT",
    install_requires=['pytz'],
    packages=['thresholdmailhandler'],
    zip_safe=False
)
