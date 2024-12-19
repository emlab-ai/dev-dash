import functools
import logging
import asyncio


def log_exceptions(log_args=False):
    """
    A decorator factory that creates a decorator to log exceptions.
    Optionally logs function arguments if log_args is True.
    Works with both synchronous and asynchronous functions.
    """
    def decorator(func):
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_exception(func, args, kwargs, e, log_args)
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                log_exception(func, args, kwargs, e, log_args)
                raise

        def log_exception(func, args, kwargs, e, log_args):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr) if log_args else ""
            # Log the exception with or without function arguments based on log_args
            logging.error(
                f"An exception occurred in {func.__name__}({signature}): {str(e)}",
                exc_info=True,
            )

        # Return the appropriate wrapper based on whether the function is asynchronous
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator



def none_if_empty(value):
    """
    Returns None if the value is empty, otherwise returns the value.
    """
    return None if value == "" else value
