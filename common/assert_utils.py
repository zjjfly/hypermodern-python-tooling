import traceback
from typing import Callable, Type


def assert_throw[T: Exception](
    exception_class: Type[T], callable_: Callable[[], None]
) -> None:
    if callable(callable_):
        err = None
        try:
            callable_()
        except Exception as e:
            err = e
            if type(e) is exception_class:
                traceback.print_exception(e)
                return
        raise AssertionError(
            f"{exception_class.__name__} expected, but got {type(err).__name__}"
        )
    else:
        raise ValueError(f"argument {callable_} is not a callable")
