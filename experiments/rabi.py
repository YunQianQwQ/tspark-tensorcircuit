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

def gen_parametric_waveform_circuit(t):
    qc = Circuit(2)

    param0 = Param("a")

    builder = qc.calibrate("rabi_test", [param0])
    builder.new_frame("drive_frame", param0)
    builder.play("drive_frame", waveforms.CosineDrag(t, 0.2, 0.0, 0.0))

    builder.build()


    qc.x(0)
    # qc.x(0)
    # qc.add_calibration('rabi_test', ['q[0]'])
    # qc.add_calibration('rabi_test', ['q[0]'])
    # qc.x(0)
    # qc.add_calibration('rabi_test', ['q[0]'])
    # qc.add_calibration('rabi_test', ['q[0]'])
    # qc.add_calibration('rabi_test', ['q[0]'])
    # qc.x(0)
    qc.add_calibration('rabi_test', ['q[0]'])
    # qc.rabi_test(['q[0]'])

    tqasm_code = qc.to_tqasm()

    print(tqasm_code)
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
    print(qc.to_tqasm())
    n = qc._nqubits
    rf = t.results()
    print(rf)
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
    return re



def exp_rabi():
    result_lst = []
    for t in range(1, 4, 2):
        qc = gen_parametric_waveform_circuit(t)
        result = run_circuit(qc)
        result['duration'] = t
        result_lst.append(result)
    return result_lst



def draw_rabi(result_lst):
    data = {'duration': [], '0': [], '1': []}

    for result in result_lst:
        data['0'].append(int(result['0']) / shots_const)
        data['1'].append(int(result['1']) / shots_const)
        data['duration'].append(result['duration'])

    plt.figure(figsize=(10, 6))
    plt.plot(data['duration'], data['0'], 'b-o', label='State |0>')
    plt.plot(data['duration'], data['1'], 'r--s', label='State |1>')

    plt.title('Rabi Oscillation Experiment')
    plt.xlabel('Duration (dt)')
    plt.ylabel('Probability')
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig('rabi.png', dpi=300)
    plt.show()


# data = exp_rabi()
# draw_rabi(data)


# gen_parametric_waveform_circuit(1)

T = 10

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


def test(n, edge, N, J=-1., h=1.):
    c = Circuit(n)
    for i in range(N):
        c = P(c, n, edge, N, J, h)
    run_circuit(c)

    # z_exp = c.expectation([gates.z(), [0]])
    # z_exp_float = float(z_exp.numpy())

    # return z_exp_float

n = 2
edges = [[1, 2], [3, 4], [0, 1], [2, 3], [1, 2], [3, 4]]

# n = 6
# edges = [[0, 1], [3, 4], [2, 5], [0, 3], [4, 5], [1, 2], [1, 4]]

# n = 9
# edges = [[0, 1], [3, 4], [7, 8], [2, 5], [0, 3], [4, 5], [6, 7], [1, 2], [4, 7], [5, 8], [3, 6], [1, 4]]

# c = Circuit(n)
# c.x(0)
# c.x(0)
# c.x(1)
# print(run_circuit(c))
# N = 20
# test(n, edges, N, 1, 1)



for a, b in list_properties("tianji_m2")["bits"].items():
    print(str(1 - b["SingleQubitErrRate"]).split('.')[1][2:4], end=',')
