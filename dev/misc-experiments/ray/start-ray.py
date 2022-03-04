import ray
import logging

# Start Ray. If you're connecting to an existing cluster, you would use
# ray.init(address=<cluster-address>) instead.
ray.init(logging_level = logging.DEBUG)
