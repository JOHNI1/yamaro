from setuptools import setup, find_packages

setup(
    name="yamaro_yonitakahashi",
    version="0.1.0",
    author="Yoni Takahashi",
    author_email="takahashiyoni@example.com",
    description="YAML->URDF robot definition converter that replaces xacro for ROS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JOHNI1/yamaro",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=[
        "numpy", "pyyaml"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3",
        "Operating System :: OS Independent",
    ],
)
