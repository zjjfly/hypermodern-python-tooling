import importlib.metadata
import importlib.util
import pprint
import sys

import httpx

# Python环境包括解释器，标准库以及安装的第三方库

# 使用sys模块获取当前的环境信息
print(f"language version: {sys.version_info.major}.{sys.version_info.minor}")
print(f"implementation name: {sys.implementation.name}")
print(f"implementation version: {sys.implementation.version}")
print(f"interpreter location: {sys.executable}")
print(f"environment location: {sys.prefix}")
print(f"lists of directories to search for modules : {sys.path}")
print(f"built-in modules: {sys.builtin_module_names}")

package_files = (str(j) for i in range(0, 10) if i > 2 for j in range(0, i) or [])

print(list(package_files))

# 可以使用python -m sysconfig打印解释器的详细元数据

# Python模块是可以通过import引入的对象的容器
# 标准库的模块位于python安装目录下的Lib（Windows）或lib/python3.x中
# 第三方库的模块在venv的site-packages中

# Python中的模块有多种形式：
# 简单模块：最简单的形式，包含Python源代码的单个文件。import string会执行string.py中的文件，并把结果绑定到本地作用域的string变量
# 包：带有__init__.py的文件夹被认为是包，它使得模块的层级结构成为可能。import email.message会加载email包中的message模块
# 命名空间包：没有__init__.py的文件夹被认为是命名空间包，一般用于把模块放在一个公共的命名空间中，如公司名称
# 扩展模块：包含有从底层语言（如C）编译而来的native代码的模块，如math模块。它们是带有让你在python中把它们作为模块导入的切入点的share library
# 内置模块：标准库中的有些模块会预载到解释器的，如sys和builtins，下面的代码可以列出所有的内置模块（也包括冻结模块）
print(f"built-in modules: {sys.builtin_module_names}")
# 冻结模块：标准库中的有些模块虽然是pyton编写的，但它们的字节码会嵌入到解释器中，这些模块就是冻结模块。
# 最开始只有importlib的核心部分，最新的python版本中会冻结所有在解释器启动的时候导入的模块

# 解释器会把纯Python模块编译为字节码，当第一次加载它们的时候。字节码会被存放在以.pyc结尾的文件中，这些文件位于每个包的__pycache__中

# 使用importlib可以获取模块的ModuleSpec，其中的字段origin存放了其源文件或dynamic library的位置，或者固定的字符串'built-in'或'frozen'

print("stdlib modules:")
for name in sorted(sys.stdlib_module_names):
    if spec := importlib.util.find_spec(name):
        print(f"{name:20} {spec.origin}")

# importlib还可以获取环境中安装的第三方包的元数据，如作者，license，版本等
print("Installed packages:")
distributions = importlib.metadata.distributions()
for distribution in sorted(distributions, key=lambda d: d.name):
    print(f"{distribution.name:30} {distribution.version}")

# per-user环境是可以用于为当前用户安装第三方库，但很少会用到它，因为它有下面几个缺点：
# 1. 它没有和全局环境隔离，所以还是可以引入系统级的第三方库，如果它没被per-user的覆盖的话
# 2. per-user环境之间也没有隔离
# 3. 如果python安装被标记为受外部管理，那么无法安装第三方库到per-user环境

# 相比per-user环境，更推荐的是虚拟环境，这也是目前的最佳实践。
# Python解释器怎么知道目前在虚拟环境？它是通过其父目录里是否存在pyvenv.cfg文件来判断的。
# 当解释器知道现在处于虚拟环境，则它会知道该去哪里找安装的第三方库。
# 这个文件中的home键的值是Python的安装路径，这可以帮助解释器找到标准库。
# 虚拟环境在创建的时候可以使用--system-site-packages参数让它可以访问系统级的第三版库

# 还有一些Python程序可以直接安装使用（如Black和Hatch），但这些应用相比库会有更多的依赖，而且依赖的库的版本可能不尽相同
# 所以需要把它们安装在不同的环境中，但如果为它们建很多虚拟环境，又显得很麻烦，这时可以使用pipx。
# 它的原理其实就是为每一个应用建一个虚拟环境，然后在一个统一的目录里使用symbol link链接安装的应用的entry script
# 这有赖于entry script里面有相关的环境的解释器的全路径，所以不论把它放在哪里都是可以执行的

# import声明实际上会被解释器翻译为调用importlib的__import__方法
# importlib还提供了一个import_module函数来导入那些只能在运行时确定的模块
# 把import系统放在标准库中可以让我们自定义导入机制，只要你实现自定义的MetaPathFinder，并注册到sys.path_hooks

# 导入模块的函数的返回是一个types.ModuleType对象，任何模块中的全局变量都会变成这个对象的属性，所以可以使用module.var来访问
pprint.pprint(sys.__dict__)
# 底层的原理是：模块的属性存放在其的__dict__中，在导入模块的时候，会执行模块的代码并把__dict__作为全局命名空间，这样代码中定义的全局变量就会被放在__dict__中。
# exec(code,module.__dict__)

# 模块中有一些特殊的变量，如__name__存放了模块的完全限定名称
print(f"Full qualified name: {sys.__name__}")
# __spec__存放了模块的spec，它是一个ModuleSpec对象
print(f"Spec: {sys.__spec__}")
# package还有一个属性__path__，它的值是一个list，存放了用于查找子模块的位置。
# 一般情况下它只包含一个元素：存放__init__.py的文件的目录。如果是命名空间包，则会有多个
print(f"Path: {httpx.__path__}")

# 模块在第一次被导入之后，会被存放到sys.modules中，可以看作是对已导入模块的缓存，key是模块的全限定名。
# 后续如果还有对这个模块的导入会直接从这个缓存中获取。这样做有下面几个好处：
# 1.加快后续导入速度
# 2.因为导入的之后会执行代码，而代码可能带来副作用，只导入一次保证了副作用也只会发生一次
# 3.可以实现递归导入，如模块a导入模块b，模块b中又要导入模块a，导入系统会在执行代码之前先把模块a放入sys.modules中，
# 然后在导入b的时候就可以从缓存中拿到部分初始化的模块，这样就避免了无限循环

# 在实现层面，模块导入分为两个部分：finder和loader。
# find是找到模块并生成一个ModuleSpec，load则是根据ModuleSpec产生一个ModuleType对象，并执行其代码
# ModuleSpec是这两个步骤之间的纽带，它其中保持了模块的名称，位置以及相关的loader。

# Finder被注册在sys.meta_path中，导入模块的时候会尝试使用其中的所有Finder的find_spec方法，直到其中的某个Finder返回一个带着loader的ModuleSpec
# 然后loader的create_module会根据ModuleSpec初始化一个Module对象，并把它传入loader的exec_module方法来加载模块。
# Python预置了三个Finder：
# 1.importlib.machinery.BuiltinImporter，用于加载built-in模块
# 2.importlib.machinery.FrozenImporter，用于加载frozen模块
# 3.importlib.machinery.PathFinder，用于查找和加载sys.path中的模块

# PathFinder是import系统的中心，它负责导入所有没有被嵌入解释器的模块。
# 在内部，它使用了二级的Finder（被称为path entry finder），每个path entry finder负责sys.path的一个目录。
# 标准库提供了两个path entry finder：zipimport.zipimporter和importlib.machinery.FileFinder，前者用于zip包内的模块的查找，后者用于文件目录
# 模块一般是放在文件系统的目录里，所以最常用的是FileFinder，它会根据文件的后缀来决定用哪个loader来加载
# 有三种loader：
# 1.importlib.machinery.SourceFileLoader，用于纯Python模块
# 2.importlib.machinery.SourcelessFileLoader，用于字节码模块
# 3.importlib.machinery.ExtensionFileLoader，用于二进制扩展模块
# zipimporter的工作方式类似，但它不支持二进制扩展模块，因为操作系统不支持从zip包加载share lib

# sys.path是怎么来的？这分为两步：
# 1. 使用内部逻辑初始化module path，这部分的代码在CPython的getpath.py
# 2. 解释器导入标准库的site模块，这个模块会扩充module path，加入环境中的site packages

# 初始的module path有下面三类，按照顺序分别是：
# 1. 当前目录或Python脚本所在的目录。这样做虽然方便，但也潜藏着安全问题，攻击者可以把python文件放在目录中来覆盖标准库的，
# 为了避免这种情况，3.11之后可以使用—P参数或环境变量PYTHONSAFEPATH来从sys.path中去掉当前目录或脚本所在的目录。更好的方法是使用虚拟环境

# 2. PYTHONPATH环境变量里的目录，基于同样的原因，尽量避免这种方法而是使用虚拟环境

# 3. 标准库的位置，有lib/python3x.zip，lib/python3.x，lib/python3.x/lib-dynload等。
# Python通过一些关键的文件来定位当前的环境和标准库的位置，主要是pyvenv.cfg和os.py

# sys.path余下的目录被称为site packages，是高度可定制的，由site模块负责
# 主要有两个路径，一个是per-user的site package，一个是环境的site package。
# site模块提供了一些用于定制的hooks：
# 1. .pth文件，这个文件中可以包含若干需要加入sys.path的目录，还可以使用import导入模块
# 一些打包工具使用它来实现editable install，
# 2. sitecustomize模块。在上述的对sys.path的设置之后，会试图导入site-packages目录下的sitecustomize模块。
# 它一般是不存在的，需要用户自己添加，放一些第三方包相关的定制逻辑
# 3. usercustomize模块。当有per-user环境的时候，会尝试导入这个模块，这里面一般放用户特定的定制逻辑

# 使用python -m site可以打印出module path以及per-user环境相关的一些信息
# sys.path = [
#     '/Users/zijunjie/PycharmProjects/hypermodern-python-tooling',
#     '/Users/zijunjie/.local/share/uv/python/cpython-3.13.1-macos-aarch64-none/lib/python313.zip',
#     '/Users/zijunjie/.local/share/uv/python/cpython-3.13.1-macos-aarch64-none/lib/python3.13',
#     '/Users/zijunjie/.local/share/uv/python/cpython-3.13.1-macos-aarch64-none/lib/python3.13/lib-dynload',
#     '/Users/zijunjie/PycharmProjects/hypermodern-python-tooling/.venv/lib/python3.13/site-packages',
# ]
# USER_BASE: '/Users/zijunjie/.local' (exists)
# USER_SITE: '/Users/zijunjie/.local/lib/python3.13/site-packages' (doesn't exist)
# ENABLE_USER_SITE: False

# 到目前为止，module path好像很复杂。但可以用下面的话来简单地总结：解释器先在sys.path的目录里查找模块，首先是标准库，然后是存放第三方包的site-packages目录
# 如果仔细考察，这个简单的说法是不准确的，但有一种方式可以保证其准确性，那就是在运行脚本的时候加入-P和-I这两个参数，前者在module path中去掉当前目录或脚本所在目录，
# 后者在module path去掉per-user环境的路径，以及PYTHONPATH中相关的路径。
# python -IPm site
# sys.path = [
#     '/Users/zijunjie/.local/share/uv/python/cpython-3.13.1-macos-aarch64-none/lib/python313.zip',
#     '/Users/zijunjie/.local/share/uv/python/cpython-3.13.1-macos-aarch64-none/lib/python3.13',
#     '/Users/zijunjie/.local/share/uv/python/cpython-3.13.1-macos-aarch64-none/lib/python3.13/lib-dynload',
#     '/Users/zijunjie/PycharmProjects/hypermodern-python-tooling/.venv/lib/python3.13/site-packages',
# ]
# USER_BASE: '/Users/zijunjie/.local' (exists)
# USER_SITE: '/Users/zijunjie/.local/lib/python3.13/site-packages' (doesn't exist)
# ENABLE_USER_SITE: False
