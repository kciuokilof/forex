import time


def repeat_on_failure(method, *args, repeat_time=5, delay=1):
    for _ in range(repeat_time-1):
        try:
            return method(*args)
        except:
            time.sleep(delay)
            continue
    return method(*args)
