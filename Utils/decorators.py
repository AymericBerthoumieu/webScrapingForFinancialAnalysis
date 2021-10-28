def time_elapsed(fn):
    from time import perf_counter

    def inner(*args, **kwargs):
        t0 = perf_counter()
        to_execute = fn(*args, **kwargs)
        t1 = perf_counter()
        print('{0} took {1:.8f}s to execute'.format(fn.__name__, t1 - t0))
        return to_execute

    return inner
