import hashlib

import pytest

# Ruff最开始重新实现了Python的很多linter，之后它又重新实现了Python的formatter的事实标准：Black。

# Python的formatter有很多种，最开始流行的是autopep8
# 它是最早出现的可以自动修复格式问题的工具，基于pycodestyle
# 它可以修复PEP 8中定义的格式问题，并保持代码的原始结构。
# 但是autopep8有一些局限性，比如它只能修复PEP 8中定义的问题，不能处理其他类型的格式问题。
# 此外，autopep8有时会引入新的格式问题，尤其是在处理复杂的代码结构时。
# 使用下面的命令可以让autopep8对某个python文件进行格式化
# pipx run autopep8 example.py

# 之后出现了yapf，它是Google开发的一个formatter，基于Google的代码风格指南。
# 它借鉴了clang-format的设计和成熟的算法。有丰富的配置选项，可以根据团队的代码风格进行定制。
# yapf的目标是将代码格式化为一种统一的风格，而不是仅仅修复PEP 8中定义的问题。
# 它会尊重现有的代码格式化选择，只要和配置是一致的。

# 2018年，Black出现了。
# 它是由Python社区开发的一个formatter，目标是提供一种“无配置”的代码格式化工具。
# Black的设计理念是“格式化即决定”，它会将代码格式化为一种统一的风格，而不允许用户进行太多的配置
# 它致力于在Python生态中推广一种统一的可读的代码风格，因为代码更多地是被阅读而不是被写作。
# 它还能让代码更加writeable，让团队成员专注于代码逻辑，而不是代码格式。
# 可以把它加入到pre-commit中，并放在最后一个，这样它可以格式化linter修复后的代码


# 可以使用下面的方式让Black不对某一块代码进行格式化
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("first test value",       "61df19525cf97aa3855b5aeb1b2bcb89"),
        ("another test value",     "5768979c48c30998c46fb21a91a5b266"),
        ("and here's another one", "e766977069039d83f01b4e3544a6a54c"),
    ]
)  # fmt: skip
def frobnicate(value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()
