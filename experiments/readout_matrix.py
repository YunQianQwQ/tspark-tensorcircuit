import numpy as np
import tensorcircuit as tc
from tensorcircuit.cloud import apis

TOKEN = os.getenv("TOKEN")
apis.set_token(TOKEN)

def create_circuit_with_prep_state(n: int, target_state) -> tc.Circuit:
    """
    制备指定的n比特经典态
    
    Parameters:
    -----------
    n : int
        量子比特数量
    target_state : str or int
        目标态，可以是二进制字符串'101'或整数5
        
    Returns:
    --------
    circuit : tc.Circuit
        制备指定态的量子线路
    """
    circuit = tc.Circuit(n)
    
    # 转换为二进制字符串
    if isinstance(target_state, int):
        target_state = format(target_state, f'0{n}b')
    
    # 对每个应该为|1⟩的量子比特应用X门
    for i, bit in enumerate(target_state):
        if bit == '1':
            circuit.x(i)
    
    return circuit

def execute_and_measure(c: tc.Circuit, shots=8192) -> dict:
    """执行量子线路并测量"""
    ts = apis.submit_task(provider="tencent", device='tianji_s2', circuit=c, shots=shots)
    return ts.results()

def measure_readout_error_matrix(n, shots=8192, token=TOKEN) -> np.ndarray:
    """
    不基于locality假设，测量完整的readout error矩阵
    
    对于n个量子比特，readout error矩阵A是2^n × 2^n的矩阵
    A[i,j] = P(测量到态i | 制备态j)
    
    Parameters:
    -----------
    n : int
        量子比特数量
    shots : int
        每个态的测量次数
        
    Returns:
    --------
    readout_matrix : np.ndarray, shape (2^n, 2^n)
        完整的readout error矩阵
    """
    apis.set_token(token)
    n_states = 2**n
    readout_matrix = np.zeros((n_states, n_states))
    
    
    for prepared_state in range(n_states):
        prepared_bitstring = format(prepared_state, f'0{n}b')
        print(f"制备态 |{prepared_bitstring}⟩ ({prepared_state+1}/{n_states})...")
        
        # 制备目标态
        circuit = create_circuit_with_prep_state(n, prepared_state)
        
        # 重复测量
        counts = execute_and_measure(circuit, shots=shots)
        
        # 统计每个测量结果的概率
        for measured_bitstring, count in counts.items():
            if len(measured_bitstring) == n:
                measured_state = int(measured_bitstring, 2)
                probability = count / shots
                
                # A[measured_state, prepared_state] = P(测量到measured | 制备prepared)
                readout_matrix[measured_state, prepared_state] = probability
        
        # 显示该制备态的主要测量结果
        # 打印所有测量结果及其概率
        all_results = sorted(counts.items(), key=lambda x: x[0])
        print("  所有测量结果: [", end="")
        for bs, c in all_results:
            print(f"({bs}): ({c/shots:.3f}), ", end="")
        print("]")
        print()
    
    return readout_matrix

######################################## For locality assumption ########################################

def create_circuit_with_prep_0(n):
    """制备所有量子比特为|0⟩态"""
    circuit = tc.Circuit(n)
    return circuit

def create_circuit_with_prep_1(n):
    """制备所有量子比特为|1⟩态"""
    circuit = tc.Circuit(n)
    for i in range(n):
        circuit.x(i)
    return circuit

def measure_readout_error_matrix_locality(n: int, shots=8192, token=TOKEN) -> np.ndarray:
    """
    利用量子比特间不相互干扰的假设，并行测量所有量子比特的readout error
    通过多比特并行测量提高效率
    Parameters:
    -----------
    n : int
        量子比特数量
    shots : int
        每个态的测量次数
    Returns:
    --------
    readout_tensor : np.ndarray, shape (n, 2, 2)
    """
    apis.set_token(token)

    # 初始化 N×2×2 的张量
    readout_tensor = np.zeros((n, 2, 2))
    
    # 所有量子比特制备为|0⟩态并测量
    circuit_all_0 = create_circuit_with_prep_0(n)
    counts_all_0 = execute_and_measure(circuit_all_0, shots=shots)
    
    # 所有量子比特制备为|1⟩态并测量
    circuit_all_1 = create_circuit_with_prep_1(n)
    counts_all_1 = execute_and_measure(circuit_all_1, shots=shots)
    
    # 从多比特测量结果中提取单比特统计
    for qubit in range(n):
        # 统计|0⟩制备态下第qubit位的测量结果
        count_0_measured_0 = 0
        count_0_measured_1 = 0
        
        for bitstring, count in counts_all_0.items():
            if len(bitstring) == n:
                measured_bit = int(bitstring[n-1-qubit])  # 注意比特顺序
                if measured_bit == 0:
                    count_0_measured_0 += count
                else:
                    count_0_measured_1 += count
        
        # 统计|1⟩制备态下第qubit位的测量结果
        count_1_measured_0 = 0
        count_1_measured_1 = 0
        
        for bitstring, count in counts_all_1.items():
            if len(bitstring) == n:
                measured_bit = int(bitstring[n-1-qubit])  # 注意比特顺序
                if measured_bit == 0:
                    count_1_measured_0 += count
                else:
                    count_1_measured_1 += count
        
        # 计算概率
        p00 = count_0_measured_0 / shots
        p01 = count_0_measured_1 / shots
        p10 = count_1_measured_0 / shots
        p11 = count_1_measured_1 / shots
        
        # 存储到张量中
        readout_tensor[qubit, 0, 0] = p00
        readout_tensor[qubit, 0, 1] = p01
        readout_tensor[qubit, 1, 0] = p10
        readout_tensor[qubit, 1, 1] = p11
    
    return readout_tensor

def get_readout_matrix_for_qubit(readout_tensor: np.ndarray, qubit_idx: int) -> np.ndarray:
    """获取特定量子比特的2×2 readout error矩阵"""
    return readout_tensor[qubit_idx]

if __name__ == "__main__":
    # test for 2 qubits
    readout_matrix = measure_readout_error_matrix(2, token=TOKEN)
    print("完整的readout error矩阵:")
    print(readout_matrix)

    readout_matrix_locality = measure_readout_error_matrix_locality(2, shots=8192)
    print("基于locality假设的readout error矩阵:")
    print(readout_matrix_locality)
