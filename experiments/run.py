from dotenv import load_dotenv
from tensorcircuit.cloud.apis import submit_task, get_device, set_provider, set_token, list_devices, list_properties
import os
import sys

module_path = ".."
sys.path.insert(0, module_path)

load_dotenv()
set_token(os.getenv("TOKEN"))
set_provider("tencent")

shots_const = 1000

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
    # print(qc.to_tqasm())
    n = qc._nqubits
    rf = t.results()
    # 截取第一个 '//' 之后
    s = qc.to_tqasm().split('// ')[1]
    s = s.split('\n')[0]
    # print(s.split(' '))
    ps = list(map(int, s.split(' ')))[:n]

    # 将 ps 改为 每个数在 ps 中有多少个比它小的
    qs = [sum(1 for x in ps if x < p) for p in ps]
    re = {}
    for a, b in rf.items():
        t = ""
        for i in range(n):
            t += str(a[qs[i]])
        re[t] = b
    return (re, sorted(ps))