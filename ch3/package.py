# Python的build工具分为前端和后端
# 前端工具常用的有build、uv、pip、Rye、Hatch和PDM，还有测试自动化工具tox
# 后端工具常用的是Flit、Hatch、PDM，Poetry，uv，以及传统的后端setuptools，使用Rust开发的Maturin（比较适合打包多种C或Rust和Python混合的项目）
# 还有一个Sphinx Theme Builder，用于打包Sphinx Theme

# 一般的build过程：
# 1. 前端新建一个虚拟环境，专门用于build
# 2. 前端在虚拟环境中安装所有项目依赖的包以及build的后端
# 3. 前端导入后端用于打包的模块或者对象，然后调用其中的方法进行打包工作

# 下面是模拟后端进行build的代码
import hatchling.build as backend
requires=backend.get_requires_for_build_wheel()
print(f"requires: {requires}")
backend.build_wheel("dist")

# 可以使用Twine来publish到PyPi，可以使用TestPyPI，一个PyPI的用于测试的实例
# 下面的命令上传build产物
# pipx run twine upload --repository=testpypi dist/*
# 下面的命令可以安装TestPyPI里的包
# pipx install --index-url=https://test.pypi.org/simple random-wikipedia-article

# 可以直接安装本地的build产物，使用下面的命令
# pip install dist/*.whl
# 还可以直接安装某个源码目录，在底层实际还是会先build出wheel，然后安装

# 如果有一个entry-point script，你也可以使用pipx安装
# pipx install .

# 在开发的时候，往往会既想要package的好处，又想要能实时看到修改之后的效果而不需要反复安装，可以使用editable install
# pip，uv，pipx都支持--editable（-e）参数

# 如果是extension module的作者，可以参考cibuildwheel这个库，看它是如何build，测试多平台兼容性和CI/CD的
