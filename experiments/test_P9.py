import sys
import os
import matplotlib.pyplot as plt

# Add the directory containing your module to Python's search path
module_path = ".."
sys.path.insert(0, module_path)

from tensorcircuit import Circuit, Param, gates, waveforms
from tensorcircuit.cloud.apis import submit_task, get_device, set_provider, set_token, list_devices, list_properties
import re

from dotenv import load_dotenv
from P9 import test
from run import run_circuit

load_dotenv()  

set_token(os.getenv("TOKEN"))
set_provider("tencent")

def get_circuit():
    
    n = 5
    edges = [[1, 2], [3, 4], [0, 1], [2, 3], [1, 2], [3, 4]]

    # n = 6
    # edges = [[0, 1], [3, 4], [2, 5], [0, 3], [4, 5], [1, 2], [1, 4]]

    # n = 9
    # edges = [[0, 1], [3, 4], [7, 8], [2, 5], [0, 3], [4, 5], [6, 7], [1, 2], [4, 7], [5, 8], [3, 6], [1, 4]]

    N = 4
    qc = test(n, edges, N, 1, 1)

    # qc = Circuit(13)
    # qc.cx(0, 2)

    # tqasm_code = qc.to_tqasm()

    # print(tqasm_code)

    # print(f"after processing : line = {tqasm_code.count('\n')}")
    return qc

qc = get_circuit()
# # print(777)
result = run_circuit(qc)
print(result)

# c = Circuit(3)
# c.X(0)
# c.X(1)
# c.CNOT(0, 1)
# c.CNOT(1, 2)
# print(run_circuit(c))





# print(list_properties("tianji_m2"))
