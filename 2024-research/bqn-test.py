import numpy as np
import bqn

# Test 1: Scalar BQN expression (simple math)
print("Test 1: Scalar BQN expression")
bqn_code = "1 + 1"
result = bqn.call(bqn_code)
print(f"Result (Scalar): {result}")

# Test 2: Array BQN expression (no numpy array passed, BQN array only)
print("\nTest 2: BQN array evaluation")
bqn_code = "1‿2‿3"
result = bqn.call(bqn_code)
print(f"Result (BQN Array): {result}")

# Test 3: BQN expression with a NumPy array as an argument
print("\nTest 3: BQN expression with NumPy array argument")
arr = np.array([4, 5, 6])
bqn_code = "⌽"  # BQN reverse function
result = bqn.call(bqn_code, arr)
