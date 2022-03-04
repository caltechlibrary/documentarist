import os
import ray

ray.init(address='auto', _redis_password='5241590000000000')

@ray.remote
def f(x):
    return x * x

os.system('ps auxww | grep redis')

futures = [f.remote(i) for i in range(4)]
print(futures)
print(ray.get(futures))
