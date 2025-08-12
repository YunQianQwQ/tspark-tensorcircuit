import numpy as np

def pseudoinverse(A: np.ndarray) -> np.ndarray:
    """Compute the pseudoinverse of a general square matrix A.

    Args:
        A (np.ndarray): Input matrix of shape (n, n).

    Returns:
        np.ndarray: Pseudoinverse of A with shape (n, n).
    """
    U, S, Vh = np.linalg.svd(A)
    S_inv = np.zeros((A.shape[1], A.shape[0]))
    for i in range(len(S)):
        if S[i] > 1e-10:  # Avoid division by zero
            S_inv[i, i] = 1.0 / S[i]
    A_inv = Vh.T @ S_inv @ U.T
    return A_inv

def pseudoinverse_locality(A: np.ndarray) -> np.ndarray:
    """Compute the pseudoinverse of a matrix A with locality structure.

    Args:
        A (np.ndarray): Input matrix of shape (n, 2, 2), where n is the number of qubits.

    Returns:
        np.ndarray: Pseudoinverse of A with the same shape as A.
    """
    n = A.shape[0]
    A_inv = np.zeros_like(A)
    for i in range(n):
        # Compute the pseudoinverse for each 2x2 block
        U, S, Vh = np.linalg.svd(A[i])
        S_inv = np.zeros_like(S)
        for j in range(len(S)):
            if S[j] > 1e-10:  # Avoid division by zero
                S_inv[j] = 1.0 / S[j]
        A_inv[i] = Vh.T @ np.diag(S_inv) @ U.T
    return A_inv
