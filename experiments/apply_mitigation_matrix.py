import os
import numpy as np

from edit_module import add_measure_commands, remove_measure_commands
from get_readout_pseudoinverse import get_mitigation_matrix
from mitigation import apply_mitigation, apply_mitigation_locality

TOKEN = 'W6QyiJRRS.DFibko9DVIuZwdqoTa5mGtl8HxoIYy4pfCPMTwhBztGrnXovVzUT0L6c-7nilqVxg1lcWd7Fj0pmLHvmb9RmA8TD8fSndBorSlfdVxPcJRQuKs.R5M9Ecu6G5DyJaAPwULZPs5r6H23G8='

def apply_mitigation_matrix(qubits: list[int], measure_results: dict, shots: int) -> np.ndarray:
    '''
    应用readout error缓解矩阵到测量结果
    Parameters:
    -----------
    qubits : list[int]
        量子比特
    measure_results : dict
        测量结果字典，格式为 {bitstring: count}
    shots : int
        每个态的测量次数
    Returns:
    --------
    mitigated_distribution : np.ndarray
        缓解后的分布，形状为 (2^qubits_num,)
    '''

    DATA_DIR = "../data"
    MAT_PATH = f"{DATA_DIR}/readout_matrix_pseudoinverse_locality.npy"

    if not os.path.exists(MAT_PATH):
        raise FileNotFoundError(f"Mitigation matrix not found at {MAT_PATH}. Please generate it first by running get_readout_pseudoinverse.py.")

    print(f"Loading mitigation matrix from {MAT_PATH}...")
    A_inv = np.load(MAT_PATH)

    if len(A_inv.shape) != 3 or A_inv.shape[1] != 2 or A_inv.shape[2] != 2:
        raise ValueError(f"A_inv must be a 3D tensor of shape (qubits_num, 2, 2) for locality. Actual shape: {A_inv.shape}")

    # convert the n * 2 * 2 matrix [A_inv0, A_inv1, ..., A_inv{n-1}] to a single 2^n * 2^n matrix
    A_inv_tensor_product = A_inv[qubits[0]]
    for i in range(1, len(qubits)):
        A_inv_tensor_product = np.kron(A_inv_tensor_product, A_inv[qubits[i]])
    A_inv = A_inv_tensor_product

    measured_distribution = np.zeros(2**len(qubits))

    for measured_bitstring, count in measure_results.items():
        if len(measured_bitstring) == len(qubits):
            measured_state = int(measured_bitstring, 2)
            probability = count / shots
            measured_distribution[measured_state] = probability
        else:
            raise ValueError(f"Measured bitstring {measured_bitstring} length does not match qubits length {len(qubits)}.")

    print("Measured distribution (with readout error):")
    print(measured_distribution)

    mitigated_distribution = apply_mitigation(A_inv, measured_distribution)

    print("Mitigated distribution:")
    print(mitigated_distribution)

    return mitigated_distribution


if __name__ == "__main__":
    qubits = [2, 1, 4]
    shots = 8192
    n = len(qubits)

    add_measure_commands(qubits)
    import tensorcircuit as tc
    from tensorcircuit.cloud import apis

    def construct_circuit(n) -> tc.Circuit:
        c = tc.Circuit(n)

        for i in range(n):
            if i % 2 ==0:
                c.h(i)

        return c

    c = construct_circuit(max(qubits) + 1)
    ts = apis.submit_task(provider="tencent", device='tianji_s2', circuit=c, shots=shots)

    print(ts.results())

    measured_distribution = np.zeros(2**n)

    for measured_bitstring, count in ts.results().items():
        if len(measured_bitstring) == n:
            measured_state = int(measured_bitstring, 2)
            probability = count / shots
            measured_distribution[measured_state] = probability

    mitigated_distribution = apply_mitigation_matrix(qubits, ts.results(), shots)

    remove_measure_commands()

    # theoretical_distribution = np.abs(c.state()) ** 2

    # # plot three distributions by histogram
    # import matplotlib.pyplot as plt
    # plt.figure(figsize=(12, 6))

    # plt.subplot(1, 3, 1)
    # plt.bar(range(2**n), measured_distribution, color='red', alpha=0.5, label='Measured Distribution')
    # plt.title('Measured Distribution')
    # plt.xlabel('State Index')
    # plt.ylabel('Probability')
    # plt.xticks(range(2**n), [f'{i:0{n}b}' for i in range(2**n)], rotation=90)
    # plt.legend()

    # plt.subplot(1, 3, 2)
    # plt.bar(range(2**n), mitigated_distribution, color='blue', alpha=0.5, label='Mitigated Distribution')
    # plt.title('Mitigated Distribution')
    # plt.xlabel('State Index')
    # plt.ylabel('Probability')
    # plt.xticks(range(2**n), [f'{i:0{n}b}' for i in range(2**n)], rotation=90)
    # plt.legend()

    # plt.subplot(1, 3, 3)
    # plt.bar(range(2**n), theoretical_distribution, color='green', alpha=0.5, label='Theoretical Distribution')
    # plt.title('Theoretical Distribution')
    # plt.xlabel('State Index')
    # plt.ylabel('Probability')
    # plt.xticks(range(2**n), [f'{i:0{n}b}' for i in range(2**n)], rotation=90)
    # plt.legend()

    # plt.tight_layout()
    # plt.show()
