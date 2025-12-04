import traceback


def assert_throw(exception_class, callable_):
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
