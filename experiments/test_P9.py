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

load_dotenv()  

shots_const = 1000

print("✅ TEST FILE LOADED")
set_token(os.getenv("TOKEN"))
set_provider("tencent")
ds = list_devices()
print(ds)

# TQASM 0.2;
# QREG a[1];
# defcal rabi_test a {
# frame drive_frame = newframe(a); 
# play(drive_frame, cosine_drag($formatted_t, 0.2, 0.0, 0.0)); } 
# rabi_test a[0];
# MEASZ a[0];

def get_circuit():
    
    n = 5
    edges = [[1, 2], [3, 4], [0, 1], [2, 3], [1, 2], [3, 4]]

    # n = 6
    # edges = [[0, 1], [3, 4], [2, 5], [0, 3], [4, 5], [1, 2], [1, 4]]

    # n = 9
    # edges = [[0, 1], [3, 4], [7, 8], [2, 5], [0, 3], [4, 5], [6, 7], [1, 2], [4, 7], [5, 8], [3, 6], [1, 4]]

    N = 4
    # qc = test(n, edges, N, 1, 1)

    qc = Circuit(13)
    qc.cx(0, 2)

    # tqasm_code = qc.to_tqasm()

    # print(tqasm_code)

    # print(f"after processing : line = {tqasm_code.count('\n')}")
    return qc


def run_circuit(qc):
    device_name = "tianji_s2" 
    d = get_device(device_name)
    t = submit_task(
    circuit=qc,
    shots=shots_const,
    device=d,
    enable_qos_gate_decomposition=False,
    enable_qos_qubit_mapping=False,
    )
    rf = t.results()
    print(rf)
    return rf



def exp_rabi():
    result_lst = []
    for t in range(1, 4, 2):
        qc = get_circuit()
        result = run_circuit(qc)
        result['duration'] = t
        result_lst.append(result)
    return result_lst

# data = exp_rabi()
# draw_rabi(data)


# gen_parametric_waveform_circuit(1)
qc = get_circuit()
print(777)
result = run_circuit(qc)
print(result)



# print(list_properties("tianji_m2"))