from setuptools import setup, find_packages

setup(
    name="tangods_phymotion",
    version="0.0.1",
    description="Tango device server written in PyTango for a Phytron phyMotion stepper motor controller using the TCP/IP network interface",
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
    url="https://github.com/MBI-Div-b/pytango-phyMotion",
    keywords=[
        "tango device",
        "tango",
        "pytango",
        "phytron",
        "phyMotion",
        "TCP/IP",
    ],
)
