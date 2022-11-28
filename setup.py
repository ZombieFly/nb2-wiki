import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot-plugin-wiki",
    version="0.1.0",
    author="ZombieFly",
    author_email="xyzomfly@gmail.com",
    description="Nonebot2 插件，基于mediawiki api搜索条目",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZombieFly/nb2-wiki",
    packages=setuptools.find_packages(),
    install_requires=["beautifulsoup4", "httpx",
                      "nonebot2>=2.0.0b1", "nonebot-adapter-onebot"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
