import subprocess


def run(command, args=[], force=False):
    if force:
        args.insert(0, "--force")
    subprocess.run([command, *args])


subprocess.run = print
run("myscript.py", force=True)
# ['myscript.py', '--force']
run("myscript.py")
# ['myscript.py', '--force']

# 上面的run有一个bug，当调用的时候没有传args，但force=True的时候，会修改默认的list
# 而默认值是所有调用共用的，所以后续没有传args的调用都会包含--force这个参数
# Ruff这样的linter就可以发现这种bug，在当前文件夹使用pipx run ruff check --extend-select B，会输出：
# B006 Do not use mutable data structures for argument defaults
#  --> lint.py:6:23
#   |
# 6 | def run(command, args=[], force=False):
#   |                       ^^
# 7 |     if force:
# 8 |         args.insert(0, "--force")
#   |
# help: Replace with `None`; initialize within function

# 在Python的历史上，最开始流行的linter是Pylint和Flake8.
# 前者会对代码进行详尽的检查，使用其自带的数百多个检查。
# 后者自身其实不包含任何检查，只是为其他linter提供了插件系统，实现插件的linter都可以被其调用
# 它默认会使用Pyflakes来检查语法和潜在的bug，使用pycodestyle来保证遵从PEP8 code style，还有McCabe用于复杂度检查（默认不启用）
# 最近几年哟三个新的linter冒出头了，它们分别是：Black，mypy，Ruff
# Black是一个code formatter，运行它它可以帮你直接帮你格式化代码，这让很多检查style的工具变得毫无意义
# mypy则是一个类型检查器，比如检查是否使用正确类型的值调用函数
# Ruff是使用Rust编写的工具，速度非常快

# Ruff重新实现了Flake8的很多插件，Pylint, pyupgrade, Bandit以及isort等
# 使用pipx install ruff安装，并使用ruff check对代码进行检查
# 使用ruff rule F541可以让它解释某个规则检查的是什么
# 使用ruff linter可以查看内置的所有linter
# 可以在pyproject.toml中的tool.ruff.lint.select中选择要启用的规则的前缀

# F开头的是Pyflake的规则，这些规则查出的几乎可以确定算是错误，如没有使用的import。它里面没有code style相关的检查
# E和W是Pycodestyle的规则，检查是否有违反PEP 8的代码。Ruff启用的规则是Pycodestyle的子集，因为code formatter已经可以省去其中的很多检查
# PEP 8不止是代码格式的推荐，而且还会推荐一些让代码的可读性更高的格式，如if x is not None是比if not x is None的可读性更高
# 如果没有使用code formatter，可以启用所有前缀是E和W的规则，它们的自动修复可以帮助确保最小限度的符合PEP 8，但相对来说，autopep8格式化工具更完整

# 有一个保留的规则前缀ALL，它会启用所有的规则，但需要谨慎使用，因为当uv升级之后，它会使用新加入的规则
# 还需要注意的是：有一些插件需要配置才能产生有用的结果，有些规则和其他规则有冲突

# 还有一个配置tool.ruff.lint.extend-select可以在默认启用的规则基础上添加额外的规则，但首先应该考虑使用select，因为它是自包含的，显式的。

# 对于legacy项目，如果一开始不知道要用哪些插件，可以先运行ruff check --statistics --select ALL查看统计的结果数据
# 然后，如果某些插件过于noisy，可以暂时禁用，使用--ignore参数，如--ignore  ANN,D就会禁用flake8-annotations和pydocstyle
# 如果某个插件发现的东西是对你有用的，可以在pyproject.toml永久开启它

# tool.ruff.lint.ignore可以不跳过某些规则，语法和select一致，它在需要某个插件的绝大部分规则，但想要跳过某几个的时候特别有用
# tool.ruff.lint.per-file-ignores可以配置某个文件或文件夹中的文件需要跳过的规则
# 但跳过某些规则应该作为最后的手段，更好的方法是使用下面这样的注释，这样既可以暂时对该行代码停用某些规则，又可以标记有问题的代码方便后续的修改
a=1
if not a is None: # noqa: E714
    print("No arguments given")
# 可以使用ruff check --add-noqa来自动给有问题的代码添加noqa注释，但一般需要先在select中配置几个具体的规则来限定范围
# 还可以使用规则RUF100这个规则来自动删除已经不再需要的noqa注释

