from setuptools import find_packages, setup
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

LONG_DESCRIPTION = 'mpu 6050'
DESCRIPTION = 'mpu 6050'
VERSION = '0.0.5'

# Setting up
setup(
    name="mpu6050",
    version=VERSION,
    author="YuryStrelkov (Yury Strelkov)",
    author_email="<ghost_strelkov@mail.ru>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['cgeo', 'smbus'],
    keywords=['mpu 6050', 'Accelerometer', 'Six axis accelerometer', 'Accelerometer mpu 6050'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ])
