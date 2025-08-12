import numpy as np

TOKEN = 'W6QyiJRRS.DFibko9DVIuZwdqoTa5mGtl8HxoIYy4pfCPMTwhBztGrnXovVzUT0L6c-7nilqVxg1lcWd7Fj0pmLHvmb9RmA8TD8fSndBorSlfdVxPcJRQuKs.R5M9Ecu6G5DyJaAPwULZPs5r6H23G8='

def project_to_simplex(v: np.ndarray) -> np.ndarray:
    """
    Project vector v onto the probability simplex using the efficient algorithm.
    
    Parameters:
    v (np.ndarray): Input vector (quasi-probability distribution)
    
    Returns:
    np.ndarray: Projected vector on probability simplex
    """
    n = len(v)
    # Sort in descending order
    u = np.sort(v)[::-1]
    
    # Find the threshold
    cumsum = np.cumsum(u)
    j = np.arange(1, n + 1)
    cond = u - (cumsum - 1) / j > 0
    
    if np.any(cond):
        rho = np.max(np.where(cond)[0])
        theta = (cumsum[rho] - 1) / (rho + 1)
    else:
        theta = (cumsum[-1] - 1) / n
    
    # Project
    return np.maximum(v - theta, 0)

def apply_mitigation(A_inv: np.ndarray, x: np.ndarray) -> np.ndarray:
    """
    Apply the mitigation matrix to the input distribution.
    
    Parameters:
    A_inv (np.ndarray): The pseudoinverse of the matrix A.
    x (np.ndarray): The distribution to be mitigated.
    
    Returns:
    np.ndarray: The mitigated distribution.
    """
    # Ensure the dimensions match
    if A_inv.shape[0] != A_inv.shape[1]:
        raise ValueError("A_inv must be a square matrix.")
    if A_inv.shape[0] != x.shape[0]:
        raise ValueError("Dimensions of A and input vector must match.")
    
    quasi_x = A_inv @ x

    # Project the quasi-probability distribution onto the simplex
    mitigated_x = project_to_simplex(quasi_x)  

    return mitigated_x

def apply_mitigation_locality(A_inv: np.ndarray, x: np.ndarray, qubit_index: int) -> np.ndarray:
    """
    Apply the mitigation matrix to the input marginal distribution of a single qubit.
    
    Parameters:
    A_inv (np.ndarray): The pseudoinverse of the matrix A.
    x (np.ndarray): The marginal distribution to be mitigated (must be in the shape of [2,]).
    qubit_index (int): The index of the qubit being mitigated.
    
    Returns:
    np.ndarray: The mitigated distribution.
    """
    # Ensure the dimensions match
    n = A_inv.shape[0]
    if A_inv.shape[1] != 2 or A_inv.shape[1] != 2:
        raise ValueError("A_inv must be a tensor in the shape of [n, 2, 2].")
    if x.shape[0] != 2:
        raise ValueError("Dimensions of the input vector (a marginal distribution of a single qubit) must be 2.")
    if qubit_index < 0 or qubit_index >= n:
        raise ValueError("qubit_index must be between 0 and n-1.")
    
    quasi_x = A_inv[qubit_index] @ x

    # Project the quasi-probability distribution onto the simplex
    mitigated_x = project_to_simplex(quasi_x)

    return mitigated_x
