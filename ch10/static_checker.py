import inspect
import json
import sys
from urllib import request
from typing import dataclass_transform

import cattrs
import cattrs.gen
from attrs import Factory, asdict, define

from ch6.random_wikipedia_article import Article
from ch10.type_annotation import JSON

# Python的静态类型检查器首选mypy，下面的代码会让mypy报错
# import textwrap
# data = {"title": "Gegenes nostrodamus"}
# summary = data.get("extract")
# summary = textwrap.fill(summary)

# mypy默认对待没有类型标注的参数和返回值为Any类型，如果想要更严格的检查，可以在pyproject.toml中加入下面的配置：
# [tool.mypy]
# strict = true
# 在严格模式下，定义或调用没有类型标注的函数会报错。所以，一般推荐在全新的项目中使用严格模式。
# 还有一个配置也很有用，它可以打印出出问题的源码片段和错误的位置
# pretty = true

# 和ruff一样，mypy也提供了方法可以对特定的代码禁用某些检查：
# main()  # type: ignore[no-untyped-call]
# 也可以在pyproject.toml中对某些文件禁用类型检查：
# [tool.mypy."<module>"]
# ignore_errors = true


# 为什么mypy需要在安装了项目所有依赖的环境下运行？
# 因为mypy需要检查所有的类型标注，而这些类型标注可能来自第三方库。如果这些库没有安装，mypy会把这些库里的类型标注当成Any类型，从而导致类型检查不完整。
# 现在已经有很多库是有完全的类型标注的，如Rich和httpx，你可以在它们源码的根目录中找到文件py.typed，这个空文件就是表示这个库是有类型标注的。
# 还有其他类型分发的机制，比如factory-boy，它本身是没有类型标注的，但你可以安装一个叫作types-factory-boy的包来为它提供类型标注支持。
# 这种包是包含了type stubs，一种专门用来为没有类型标注的库提供类型信息的文件，通常以.pyi为后缀名。
# python标准库本身没有类型标注，但有一个叫作typeshed的项目，里面包含了标准库和一些第三方库的类型标注文件，mypy会自动使用这些类型标注文件来补充标准库的类型信息。

# 如果依赖缺失没有类型标注怎么办？可以在pyproject.toml中禁用mypy对这些依赖的检查：
# [tool.mypy.<package>]
# ignore_missing_imports = true

# 测试代码也可以使用mypy进行类型检查，这么做也可以检查是否正确使用了待测的代码，pytest和其他测试工具库

# 和TypeScript不同，Python的类型标注可以在运行时被获取，运行时类型检查是一些强大的特性的基础，一个第三方库的生态系统已经围绕它的使用建立起来了
# 解释器会把类型标注存储在__annotations_属性中，但不要直接访问它（虽然没有做限制），而是使用inspect模块中的get_annotations函数
print(inspect.get_annotations(Article))
# {'title': <class 'str'>, 'summary': <class 'str'>}

# Article虽然没有定义__init__方法，但@dataclass会自动为它生成一个__init__方法
print("__init__" in Article.__dict__)


# 相比@dataclass，更推荐使用attrs,因为它性能和功能都更强大
@define
class SomeClass:
    a_number: int = 42  # 默认值42
    list_of_numbers: list[int] = Factory(list)  # 默认值的工厂函数


sc = SomeClass(1, [1, 2, 3])
print(sc)
print(sc != SomeClass(1, [3, 2, 1]))
print(asdict(sc))
print(SomeClass())


# 这两个模块给我们的启发是：通过运行时获取的类型标注，我们可以实现一个自己的dataclass。


# @dataclass_transform装饰器告诉类型检查器这个装饰器会改变类的行为，从而让类型检查器理解这个装饰器的作用
@dataclass_transform()
def dataclass[T](cls: type[T]) -> type[T]:
    source_code = build_init(cls)
    globals = sys.modules[cls.__module__].__dict__
    locals = {}
    # compile source code on the fly
    exec(source_code, globals, locals)

    cls.__init__ = locals["__init__"]
    return cls


def build_init[T](cls: type[T]) -> str:
    annotations = inspect.get_annotations(cls)
    args: list[str] = ["self"]
    body: list[str] = []
    for name, typ in annotations.items():
        args.append(f"{name}: {typ.__name__}")
        body.append(f"    self.{name} = {name}")
    args_str = ", ".join(args)
    body_str = "\n".join(body)
    init_str = "def __init__({}) -> None:\n{}".format(args_str, body_str)
    return init_str


# 类型信息还可以用来进行运行时类型检查
def fetch(url: str) -> Article:
    with request.urlopen(url) as response:
        data: JSON = json.load(response)
    # 使用结构模式匹配
    match data:
        case {"title": str(title), "extract": str(extract)}:
            return Article(title, extract)


# 但相比这种手写的方式，推荐使用cattrs来进行JSON的序列化和反序列化，它可以自动处理类型转换和验证


def fetch2(url: str) -> Article:
    headers = {
        "User-Agent": "RandomWiki/1.0 (Contact: zjjblue@gmail.com)",
    }
    req = request.Request(url, headers=headers)

    with request.urlopen(req) as response:
        data: JSON = json.load(response)
    return cattrs.structure(data, Article)


# 如果json的字段名和类的字段名不一致，也可以使用cattrs的转换器来处理：

converter = cattrs.Converter()
converter.register_structure_hook(
    Article,
    cattrs.gen.make_dict_structure_fn(
        Article,
        converter,
        summary=cattrs.gen.override(rename="extract"),
    ),
)


def fetch3(url: str) -> Article:
    headers = {
        "User-Agent": "RandomWiki/1.0 (Contact: zjjblue@gmail.com)",
    }
    req = request.Request(url, headers=headers)

    with request.urlopen(req) as response:
        data: JSON = json.load(response)
    return converter.structure(data, Article)


print(fetch3("https://en.wikipedia.org/api/rest_v1/page/random/summary"))
# cattrs的优点是：把序列化和反序列化的逻辑和数据模型分离开来，使得代码更清晰易懂，
# 并且还可以用于dataclasses, attrs-classes, named tuples, typed dicts和一般的类型如tuple[str, int].
