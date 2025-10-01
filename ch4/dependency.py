# 要指定依赖的版本的下限，因为：
# 1. 依赖的包本身会有其他的依赖，它们可能会对版本有额外的限制
# 2. 应用有时候也不会安装在隔离的环境，而是安装在系统层面
# 3. 下限可以帮助你发现依赖树中版本冲突

# 但不要指定上限，出非你确实知道这个版本和程序不兼容
# 防止依赖版本变化导致的程序失败，使用lock file是更好的方式
# 如果某个依赖发布的某个版本包含严重的bug，可以使用awesome >=1.2,!= 1.3.1这样的方式来exclude某个版本
# 但exclude某个版本的问题是：依赖解析器可以决定降级你的库的版本到没有这个exclusion，并升级那个有问题的依赖，lock file可以避免这个问题
# 只有当确定某个版本升级永久性的破坏了兼容性，才会指定依赖的上界

# 版本声明支持下面几种操作符：
# ==：版本必须在标准化之后是相等的。末尾的0会被去掉
# !=：和==相反
# <=,>= ：进行词典顺序的比较，预发行版本会先于最终发行版本，即1.0.0a1 < 1.0.0
# >,< ：和上面的类似，但不包含相等的版本
# ~= ：如写的是~=x.y，则要求版本大于等于x.y且小于x.(y+1)，如果写的是~=x.y.z，则要求版本大于等于x.y.z且小于x.(y+1).0
# === ：用于非标准格式的版本的比较
# 上面的操作符中，==支持通配符，尽管只能写在末尾，如1.2.*，===只在版本是非标准格式的时候使用
# 对于预发布版本，版本声明一般会排除它们，只有三种情况它们是有效的：
# 1. 它们已经被安装了
# 2. 没有别的版本满足
# 3. 使用>=显式地指定，如>= 1.0.0rc1

# 有的时候，依赖会提供一些额外的包，这一些包通常是对其功能的增强和扩展，这种情况下，需要使用httpx[http2]这样的语法来安装，实际会安装h2这个包来实现HTTP2协议的编解码
# 但对于httpx来说，h2这个依赖并不是必须的，只有在用户安装httpx[http2]的时候才会需要，也就是说h2是一个可选依赖。
# 下面是httpx的pyproject.toml中声明可选依赖的方法：
# [project]
# name = "httpx"
#
# [project.optional-dependencies]
# http2 = ["h2>=3,<5"]
# brotli = ["brotli"]

# 在代码中使用可选依赖：
try:
    import h2
except ModuleNotFoundError:
    h2 = None
if h2 is not None:
    print(h2.__version__)

# 可以使用env marker指定适用于特定的操作系统，处理器架构，python实现和版本的依赖。
# 一个例子就是importlib.metadata，这个是python3.8之后才加入标准库的模块
# 那么如果使用的版本低于3.8，该怎么办呢？幸运的是很多标准库的新增内容会以第三方库的形式进行向后兼容。
# importlib-metadata这个库就提供了和importlib.metadata一样的功能
# 所以，如果你的库要用到importlib.metadata，则需要考虑兼容那些使用3.8以下的版本的用户
# 可以在dependencies里加入下面的这一项：
# "importlib-metadata>=6.7.0; python_version < '3.8'"
# 然后在使用的时候检查版本，根据版本使用标准库的importlib.metadata或importlib_metadata
import sys
if sys.version_info >= (3, 8):
    from importlib.metadata import metadata
else:
    from importlib_metadata import metadata

# env marker支持的相等和比较操作符和版本声明支持的一致，还可以使用in或not in来匹配是否包含某个子字符串
# 还可以把多个env marker结合起来使用，下面是例子：
# [project]
# dependencies = ["""                                                         \
#   awesome-package; python_full_version <= '3.8.1'                           \
#     and (implementation_name == 'cpython' or implementation_name == 'pypy') \
#     and sys_platform == 'darwin'                                            \
#     and 'arm' in platform_version                                           \
# """]

# 对于仅在开发时需要的依赖，除了PEP735的方案在pyproject.toml中加入[tool]之外，常用的方式是使用可选依赖或requirements文件
# 使用可选依赖的好处：1. 不会默认安装，所以不会污染用户的环境 2.可以为这些依赖进行分组，如test，doc等 3. 可以使用和其他依赖一样的依赖规范，包括版本限制和env marker
# 但使用可选依赖也有点违和，因为它的初衷是为了让用户可以安装一些提供额外功能的模块，而不是为了让开发者维护开发依赖的
# 对于uv用户，可以使用dependency group：
# uv add --dev pytest
# uv sync --group dev
# 如果不想安装某个group的依赖，可以使用uv sync --no-dev

# requirements文件一般是一个txt文件，每一行是一个依赖，
# 可以写文件路径或URL，还可以在前面加一个-e来表示editable install
# 同样可以加全局选项，如-r来引用另一个requirements文件，--index-url来使用除了PyPI之外的index服务
# 这个文件也支持python风格的注释
# 但这种方法管理开发依赖的弊端是：1.不是Python的打包标准，也不可能是 2.会让项目显得杂乱

# 要保证生产环境安装的包和开发测试的时候安装的包的版本是一致的，否则可能会导致代码的兼容性和安全性问题
# 第三方库的变动会导致发生不一致：
# 1. 某个依赖在你部署之前发布了新版本
# 2. 在现存的release中上传了新的artifact。比如，维护人员会在新的Python版本发布的时候上传新的wheel
# 3. 维护者删除或撤回某个版本。撤回（yanking）会导致包无法使用pip安装，除非使用==指定这个版本
# 开发和生产环境的不一致也会导致这种情况：
# 1. env marker的解析结果不同，例如生产环境使用了更低版本的Python
# 2. wheel的兼容性标签导致安装器选择了一个不同的版本，如开发使用的Arm芯片的Mac，但生产环境是x86-64的Linux
# 3. 使用不同的安装器，因为它们解析依赖的方式可能是不同的
# 4. 工具的配置或状态的不同，如使用不同的index URL来安装包
# 所以，需要对依赖进行锁定，一般是使用一个lock file。Python的打包标准中目前少了这一块，但很多工具实现了自己的lock file
# 一种常用的做法是使用requirements文件来冻结依赖，可以使用pip freeze或uv pip freeze命令
# 注意，在冻结依赖的时候要保证当前环境和部署环境一致，即操作系统，处理器架构，Python版本和实现都要一致
# 冻结依赖的问题是：
# 1. 每次requirements文件更新之后都要重新安装一遍依赖
# 2. 很容易在不经意间污染requirements文件，如果你临时安装了一个包，但之后没有恢复环境
# 3. 冻结的时候不会记录包的hash值，这无法防止包被劫持

# 还可以使用pip-tools的pip-compile和pip-sync，前者可以根据pyproject.toml导出requirement文件，后者可以从requirement文件应用于某个环境
# uv提供了这两个命令的替代：uv pip compile和uv pip sync
# 也可以指定python的版本和输出的文件：uv pip compile --python-version=3.12 pyproject.toml -o requirements.txt
# pip和uv的导出命令产生的requirement文件会包含生成这个文件时使用的命令，和freeze不同的是，里面不会包含你自己的工程
# 可以加上--generate-hashes 来记录每个包的hash值，这样可以防止on-path attack。
# 但加上hash也可能会让pip拒绝安装包，要么所有的包都有hash，要么都没有。
# 还可以使用--no-deps和--no-cache来加固，前者可以保证只安装requirement文件里的包，后者防止安装器重用本地下载的构建的包

# 在生产环境运行的应用最好是一周检查一次依赖更新，处于活跃开发期的甚至可以每天都检查，可以使用Dependabot或Renovate这样的工具
# 如果不这么做，一个安全问题可能就会让你升级多个依赖的主版本，也可能包括Python的版本

