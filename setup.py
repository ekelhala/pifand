from setuptools import setup, find_packages

setup(
    name="pifan",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "pifan-daemon = pifan.app:start",
            "pifanctl = pifanctl.pifanctl:main"
        ]
    },
    include_package_data=True,
    data_files=[
        ("/etc/pifan", ["config/config.toml"]),
        ("/lib/systemd/system", ["service/pifan.service"])
    ],
    author="Emil Kelhälä",
    author_email="emil.kelhala@protonmail.com",
    license="GPL"
)