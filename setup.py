from setuptools import setup

setup(
    name="tangods_phymotion",
    version="1.0.0",
    description="Tango device server written in PyTango for a Phytron \
        phyMotion stepper motor controller using the TCP/IP network interface",
    author="Daniel Schick",
    author_email="schick@mbi-berlin.de",
    python_requires=">=3.6",
    entry_points={"console_scripts": ["PhyMotion = tangods_phymotion:main"]},
    license="MIT",
    packages=["tangods_phymotion"],
    install_requires=[
        "pytango",
        "socket",
    ],
    url="https://github.com/MBI-Div-b/pytango-PhyMotion",
    keywords=[
        "tango device",
        "tango",
        "pytango",
        "phytron",
        "phyMotion",
        "TCP/IP",
    ],
)
