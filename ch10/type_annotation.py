from __future__ import annotations

import math
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Self, Sequence, cast

from typing_extensions import Protocol

from common.assert_utils import assert_throw

# Python是动态类型语言，但它处于静态类型和动态类型之间有一个有趣的中间地带。

number = input("Enter a number: ")
number = float(number)
result = math.sqrt(number)

print(f"The square root of {number} is {result}.")

# Python中，变量只是值的名字。变量没有类型，值才有类型。
# 所以上面的代码中，变量number最初引用一个字符串值，后来引用一个浮点数值。
# 但和Perl不同，Python不会自动转换类型。必须显式地调用float()函数将字符串转换为浮点数。
# 这种设计使得Python代码更清晰，更易于理解。

try:
    math.sqrt("1.21")
except TypeError as e:
    print(f"Error: {e}")
# 上面的代码尝试计算字符串"1.21"的平方根，结果引发TypeError异常。
# 这表明Python不会隐式地将字符串转换为数字。但这种类型检查也有两个限制：
# 1. 这种类型检查不是在解释时进行的，而是在运行时进行的。
# 2. 这种类型检查是由代码员显式地编写的，而不是由编译器隐式地插入的。

# Python作为动态类型语言，支持鸭子类型。
# 鸭子类型的好处是，不用强制调用者必须实现某个特定的接口，只需要其有某些方法或属性即可。
# 但这样也有缺点，它会让代码非常难阅读，你需要不断沿着方法的调用链不断地追踪代码，才能弄清楚某个对象的真实类型。
# 把方法的参数和返回值的类型写明会极大的解决这个问题，传统上这通过文档字符串来实现
# 但遗憾的是，文档字符串往往会过时，或者根本就没有写，更重要的是，没有正式的语言以一种明确的，可验证的方式来描述类型
# 也没有工具来强制保证这些类型签名，它们也只是美好的愿望而已。


# 这个问题对于几百行代码的小程序不算大问题，但对于达到上百万行的代码库是不容忽视的。
# 所以那些大公司在2010年代开始研发静态检查工具。这种工具可以在不执行代码的情况下进行类型检查
# 静态检查器可以推理出变量的类型，如果程序员可以在代码中显式地标明类型，它的功能会更强大
# 过去几年中，Python有了一种在源码中表示方法和变量的类型的方法，叫作类型标注
def format_lines(lines: list[str], indent: int = 0) -> str:
    prefix = " " * indent
    return "\n".join(f"{prefix}{line}" for line in lines)


# 类型标注目前已经成了Python丰开发工具和库的丰富生态系统的基础
# 它虽然不会影响运行时代码的行为，但会被存储在__annotations__这个属性中
print(format_lines.__annotations__)
# 虽然可以在运行时使用这个属性来做一些很酷的事情，但它最大的作用是被静态检查器使用
# 有了它们，才可以做到不运行代码也可以检查代码的正确性

# 你不需要使用类型标注就可以享受其带来的好处，因为很多库的源码中已经使用了它
# 你对库的错误使用，或者库升级导致的break changes等，静态检查器会在你运行代码之前就警告你
# IDE和编辑器可以利用类型标注来为你带来更好的开发体验，如自动完成，提示和类型浏览等。
# 你还可以在运行时利用它进行数据验证或序列化

# 如果你在自己的代码中加入类型标注，之前提到的好处都有，并且你会发现更容易对代码进行推理，
# 重构代码也不会引入一些微妙的错误，这可以构建一个清晰的软件架构。如果你是库的作者，
# 类型让你指明了用户可以依赖的接口契约，而你可以自由地改进实现

# 使用类型标注的挑战是，要对现有的代码进行重构让其具有typability。
# 比如把深度嵌套的原始类型和高度动态的对象替换为更加简单的，可预测的类型
# 还有一点就是目前Python的类型语言还处于快速演进中，需要适应这种快速变化

# 变量标注
answer: int = 42
# 除了内置的类型bool、int、float、str和bytes，还可以使用标准的容器类，如list、tuple、set或dict
lines: list[str] = []
# 内置的容器类就是泛型类的例子，泛型类指的是接受一个或多个类型参数的类
fruits: dict[str, int] = {
    "banana": 3,
    "apple": 2,
    "orange": 1,
}
# 元组相比其他容器是特殊的，它可以传入固定数量的类型参数
pair: tuple[str, int] = ("banana", 3)
coordinates: tuple[float, float, float] = (4.5, 0.1, 3.2)
# 元组还可以用来表示不可变的任意长度的序列，这种情况要使用省略号表示零个或多个相同的类型
numbers: tuple[int, ...] = (1, 2, 3, 4, 5)


# 自定义的class也是一种类型
class Parrot:
    pass


class NorwegianBlue(Parrot):
    pass


parrot: Parrot = NorwegianBlue()

# 子类型关系
# Python不要求赋值声明的左右两边的类型完全一致，只需要右边的值的类型是左边的类型标注的子类型就行
# 但Python的类型系统比Java的更宽泛，因为它支持结构子类型，如int的tuple就是object的tuple的
# 类型规则也支持类型具有某种一致性的情况下也可以赋值，这让我们可以使用int给float类型的变量赋值
# Any这个类型和所有类型都具有一致性

# union类型。可以是用|连接多个类型，这是新的类型其范围涵盖其组成类型
user_id: int | str = "nobody"  # or 65534
# 它最常用的是用于optional类型，表示一个值要么是某个类型，要么是None
description: str | None = None
# union类型是子类型关系的有一个例子，union中的每个类型都是union类型的子类型
# 严格来说，None是一个NoneType类型的值，但通常我们直接用None来表示NoneType类型，这也是Python允许的
# 如果你试图访问None的某个属性，会报错：AttributeError: 'NoneType' object has no attribute '...'
# 好消息是，当你试图使用可能会是None的变量的时候，静态检查器会发出警告
# 如何让静态检查器知道某个变量不是None呢？可以使用断言语句
if description is not None:
    for line in description.splitlines():
        print(f"    {line}")

# 这种方式被称作type narrowing。 它可以让静态检查器推理出某个变量在某个代码路径中的更具体的类型
# 两外还有两种常见的类型缩小方式，一种是使用assert和isinstance()函数
description = "A lovely parrot."
assert isinstance(description, str)
for line in description.splitlines():
    print(f"    {line}")
# 另一种是使用cast函数，如果你已经知道某个变量有正确的类型
description_str = cast(str, description)
# 实际上在运行时，cast函数什么都不做。它只是用于告诉静态检查器某个值是某个特定的类型

# 渐进类型化
# 在Python中，object是所有类型的超类型，这听着很强大，但其实从行为上来说，object是所有值的最小分母，所以你只能对它做非常有限的操作
# 因此，下面的代码就会让静态检查器发出警告
number: object = 2
print(number + number)  # error: Unsupported left operand type for +
# 与之相反的是Any，它可以表示任意类型，所以你可以对Any类型的值做任何操作，它也是一种避开类型检查的方式
number: Any = NorwegianBlue()
assert_throw(TypeError, lambda: number + number)  # valid, but crashes at runtime!
# 所以当你在阅读代码时，看到Any类型的变量，你就要提高警惕了，因为它可能在相当程度上让类型检查失效，因为Any类型调用任何方法或属性返回的也是Any类型
# Any是渐进类型化的一个重要工具，它允许你逐步地为代码添加类型标注。
# 渐进类型化的价值有二：1.在可预见的未来，类型化的代码和非类型化的代码将会共存 2.Python的强大一部分来自于其动态，对于像动态组装或修改的类，很难对其应用严格的类型


# 函数标注
# 函数的参数类型的标注和变量的标注一样，但返回值类型的标注要使用->符号，因为:已经被用来表示函数体的开始
def add(a: int, b: int) -> str:
    return a + b


# 函数体中没有return语句的函数会隐式地返回None，所以它们的返回值类型要标注为None
def greet(name: str) -> None:
    print(f"Hello, {name}!")


# 类型检查器对于没有return语句的函数会默认其返回Any类型，同样的没有标注类型的参数也会被认为是Any类型
# 这非常有效地让类型检查器对于这个函数失效了


def run(*args: str, check: bool = True, **kwargs: Any) -> None:
    subprocess.run(args, check=check, **kwargs)


# 上面这个函数中，*args表示接受任意数量的位置参数，这些参数会被收集到一个tuple中，并且它们的类型都是str
# **kwargs表示接受任意数量的关键字参数，这些参数会被收集到一个dict中，并且它们的类型都是Any


# Python中，可以使用yield语句定义生成器函数，生成器的行为除了迭代之外还有其他，如果只用于迭代，可以标注它的返回值类型为Iterator[T]
def fibonacci() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


for i in fibonacci():
    if i > 100:
        break
    print(i)
# Python中，函数也可以用Callable类型表示，它有两个类型参数，一个是参数类型的list，另一个是返回值类型
Serve = Callable[[str, str], str]


# 标注类型
# 对于变量和函数的规则也可以应用于类型的实例变量和方法，self参数可以忽略。
# 类型检查器可以通过__init__方法的参数类型标注来推理出类的实例变量的类型
class Swallow:
    def __init__(self, velocity: float) -> None:
        self.velocity = velocity


# dataclasses模块可以从带有装饰器@dataclass的任何类型的类型标注中生成经典的方法定义
@dataclass
class Swallow2:
    velocity: float


# dataclass风格的类不止比手写的更加简洁，还会赋予类型其他运行时行为，如基于类的属性来比较实例的相等性或对它们进行排序
# 当你标注类型时，通常会碰到提取引用的问题（即在类型定义中引用类型本身）
# 这时可以使用字符串来表示类型名称，静态检查器会正确地解析它们
@dataclass
class Point:
    x: float
    y: float

    def distance(self, other: "Point") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


# 或者可以隐式地对所有的类型标注进行字符串化
@dataclass
class Point2:
    x: float
    y: float

    def distance(self, other: Point2) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


print(Point2(1.0, 2.0).distance(Point2(4.0, 6.0)))


# 还有第三种方法，但它不能处理所有的提前引用的情况，因为如果有类继承了Point3，那么Self表示的是这个子类型，
# 所以distance方法就不能计算子类和Point3实例之间的距离了
@dataclass
class Point3:
    x: float
    y: float

    def distance(self, other: Self) -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


print(Point3(1.0, 2.0).distance(Point3(4.0, 6.0)))

# 类型别名，它可以让代码自我描述，并在类型变得笨重的时候增强代码的可读性
type UserID = int | str
# 它还可以用来表示通常的方式无法表达的类型，如JSON这样的inherently recursive data type
type JSON = None | bool | int | float | str | list[JSON] | dict[str, JSON]
# 递归类型别名是提前引用的另一个例子，所以可以使用字符串化的方式来定义它
TypeJSON = None | bool | int | float | str | list["TypeJSON"] | dict[str, "TypeJSON"]


# 泛型
# 内置的容器类型如list、dict和tuple都是泛型类的例子
# 你也可以定义自己的泛型函数或类型
def first[T](values: Iterable[T]) -> T:
    for value in values:
        return value
    raise ValueError("empty list")


assert first([1, 2, 3]) == 1
# [T]这样的泛型是从3.12版本开始支持的，之前的版本要使用typing模块中的TypeVar来定义泛型类型变量
from typing import TypeVar

U = TypeVar("U")


def second(seq: Sequence[U]) -> U:  # Function is generic over the TypeVar "U"
    return seq[1]


assert second(["a", "b", "c"]) == "b"


# Protocol，作用和scala的结构类型一样，可以用来定义鸭子类型的接口契约
# 类型只要实现了Protocol中定义的方法和属性，就被认为是这个Protocol的子类型，不需要显式继承它
class Joinable(Protocol):
    def join(self) -> None: ...


def join_all(joinables: Iterable[Joinable]) -> None:
    for task in joinables:
        task.join()


# 上面的一些类型特性只能在Python的3.9及更高版本中使用，如果是使用更早的版本，可以使用typiny-extensions模块来获得这些特性
