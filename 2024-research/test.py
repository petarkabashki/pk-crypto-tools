import bqn
import numpy as np
# bqn.call("1‿2‿3",np.arange(5))
# bqn.call("a←5×↕10", np.arange(10))
# bqn.eval("11+22")
# bqn.call("+`", np.arange(20)).astype(int)
print(bqn.call("+´", np.arange(20)))
