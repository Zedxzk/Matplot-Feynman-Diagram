from setuptools import setup, find_packages

setup(
    name="pyfeynplot",
    version="0.1.0",
    author="Zedxzk",
    author_email="Zedxzk@gmail.com",
    description="Matplot-Feynman-Diagram",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zedxzk/Matplot-Feynman-Diagram/tree/main",
    packages=find_packages(include=["feynplot", "feynplot_gui", "feynplot_gui.*"]),  # 确保包含子包
    # package_dir={"": "."},  # 可以不设置，默认就是当前目录
    include_package_data=True,
    install_requires=[
        "matplotlib>=3.7.2",
        "mplhep>=0.3.59",
        "numpy>=1.23",
        "Pygments>=2.19",
        "PySide6>=6.9",
        "PySide6-Addons>=6.9",
        "PySide6-Essentials>=6.9",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "feynplot-gui = feynplot_gui.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
    ],
)
