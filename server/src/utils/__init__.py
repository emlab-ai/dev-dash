import logging
import functools

def log_exceptions(log_args=False):
    """
    A decorator factory that creates a decorator to log exceptions.
    Optionally logs function arguments if log_args is True.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                args_repr = [repr(a) for a in args]                      
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  
                signature = ", ".join(args_repr + kwargs_repr) if log_args else ""
                # Log the exception with or without function arguments based on log_args
                logging.error(f"An exception occurred in {func.__name__}({signature}): {str(e)}", exc_info=True)
                # Re-raise the caught exception after logging it
                raise
        return wrapper
    return decorator
