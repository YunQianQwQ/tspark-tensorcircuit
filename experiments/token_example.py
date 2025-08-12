from edit_module import *

qubits_num = 3
shots = 8192

add_measure_commands([2, 1])  # 添加测量命令到量子比特0和1

import tensorcircuit as tc
from tensorcircuit.cloud import apis

token = 'W6QyiJRRS.DFibko9DVIuZwdqoTa5mGtl8HxoIYy4pfCPMTwhBztGrnXovVzUT0L6c-7nilqVxg1lcWd7Fj0pmLHvmb9RmA8TD8fSndBorSlfdVxPcJRQuKs.R5M9Ecu6G5DyJaAPwULZPs5r6H23G8='
apis.set_token(token)
print(apis.list_devices(provider="tencent"))

c = tc.Circuit(qubits_num)
c.z(0)
c.x(1)
c.h(2)
# c.cnot(1, 2)
ts = apis.submit_task(provider="tencent", device='tianji_s2', circuit=c, shots=shots)
data = ts.results()
print(data)

remove_measure_commands()
