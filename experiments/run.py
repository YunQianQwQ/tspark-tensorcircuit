from dotenv import load_dotenv
from tensorcircuit.cloud.apis import submit_task, get_device, set_provider, set_token, list_devices, list_properties
import os
import sys

module_path = ".."
sys.path.insert(0, module_path)

shots_const = 8000

def run_circuit(qc):
    # print("asddslkajfjsakf")
    # set_provider("tencent")
    # load_dotenv()
    # token = os.getenv("TOKEN")
    # print(token)
    device_name = "tianji_s2"
    d = get_device(device_name)
    t = submit_task(
        circuit=qc,
        # token=token,
        shots=shots_const,
        device=d,
        enable_qos_gate_decomposition=False,
        enable_qos_qubit_mapping=False,
    )

    code = qc.to_tqasm()
    print("number of CX =", code.count("CX"))
    print("lines =", code.count('\n'))
    n = qc._nqubits
    rf = t.results()
    # 截取第一个 '//' 之后
    s = code.split('// ')[1]
    s = s.split('\n')[0]
    print("s =", s)
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