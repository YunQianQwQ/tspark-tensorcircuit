import os
import sys
module_path = ".."
sys.path.insert(0, module_path)

import numpy as np
import tensorcircuit as tc
import tensorflow as tf
import matplotlib.pyplot as plt
from run import run_circuit
from apply_mitigation_matrix import apply_mitigation_matrix

from tensorcircuit.cloud.apis import submit_task, get_device, set_provider, set_token, list_devices, list_properties
from dotenv import load_dotenv

load_dotenv()

set_token(os.getenv("TOKEN"))
set_provider("tencent")

T = 19

def rzz (c, i, j, theta):
	c.cnot(j, i)
	c.rz(i, theta=theta)
	c.cnot(j, i)
	return c

def P (c, n, edges, N, J = -1., h = 1.):
	for i in range(n):
		c.rx(i, theta = 2*T*h/N)
	for g0,g1 in edges:
		c = rzz(c, g0, g1, -2*T*J/N)
	return c

def test (n, edge, N, J = -1., h = 1.):
	c=tc.Circuit(n)
	for i in range(N):
		c = P(c, n, edge, N, J, h)
	return c
	# z_exp = c.expectation([tc.gates.z(), [0]])
	# z_exp_float = float(z_exp.numpy())

	# return z_exp_float

n = 5
edges = [[1, 2], [3, 4], [0, 1], [2, 3], [1, 2], [3, 4]]

# n = 6
# edges = [[0, 1], [3, 4], [2, 5], [0, 3], [4, 5], [1, 2], [1, 4]]

# n = 9
# edges = [[0, 1], [3, 4], [7, 8], [2, 5], [0, 3], [4, 5], [6, 7], [1, 2], [4, 7], [5, 8], [3, 6], [1, 4]]

N = 2
c = test(n, edges, N, 1, 1)

# print(c.state())
st = c.state()
print(np.abs(st) ** 2)
res = run_circuit(c)
res = apply_mitigation_matrix(res[1], res[0], 1000)

