"""Helper decorators."""

import os
import pickle
import time


def cached(cache_filename=None, ttl=None):
    """Cache results on per function basis."""
    if not cache_filename:
        cache_filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'cache.p'
        )

    def decorator(fn):
        def wrapped(*args, **kwargs):
            namespace = '.'.join([
                fn.__module__,
                fn.__qualname__
            ])

            # examine cache for non-expired data
            if os.path.isfile(cache_filename):
                with open(cache_filename, 'rb') as handler:
                    cached_data = pickle.load(handler)[namespace]
                    if cached_data['timestamp'] + ttl > int(time.time()):
                        return cached_data['data']

            # cache miss, do query and save in cache
            result = fn(*args, **kwargs)
            with open(cache_filename, 'wb') as handler:
                pickle.dump(
                    {
                        namespace: {
                            'data': result,
                            'timestamp': int(time.time())
                        }
                    },
                    handler
                )

            return result
        return wrapped
    return decorator
