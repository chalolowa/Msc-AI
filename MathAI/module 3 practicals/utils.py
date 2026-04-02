import numpy as np

#set random seed for reproducibility
np.random.seed(42)

#Implement SVD
def perform_svd(A):
    """
    Perform Singular Value Decomposition on matrix A.
    Returns U, singular values (vector), and Vt
    """
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    return U, s, Vt

def reconstruct_from_svd(U, s, Vt):
    """
    Reconstruct original matrix from SVD components.
    """
    Sigma = np.diag(s)
    return U @ Sigma @ Vt

def low_rank_approx(U, s, Vt, k):
    """
    Compute the low-rank approximation of a matrix using its SVD.
    k: the number of singular values to keep.
    """
    # Keep only the first k singular values, U columns, and V^T rows
    U_k = U[:, :k]
    s_k = s[:k]
    Vt_k = Vt[:k, :]
    
    # Construct the low-rank approximation
    return U_k @ np.diag(s_k) @ Vt_k

# Test matrix
A_task1 = np.array([[1, 2, 3],
                    [4, 5, 6]], dtype=float)

print(f"Original Matrix A (2x3):\n{A_task1}\n")

U, s, Vt = perform_svd(A_task1)
Sigma = np.diag(s)

print(f"Matrix U ({U.shape}):\n{U}\n")
print(f"Singular Values Σ (vector): {s}")
print(f"Σ as diagonal matrix:\n{Sigma}\n")
print(f"Matrix V^T ({Vt.shape}):\n{Vt}\n")

# Reconstruction
A_reconstructed = reconstruct_from_svd(U, s, Vt)
print(f"Reconstructed Matrix:\n{A_reconstructed}\n")
print(f"Reconstruction Error (Frobenius norm): {np.linalg.norm(A_task1 - A_reconstructed):.2e}")
print(f"Verification: A = UΣV^T? {np.allclose(A_task1, A_reconstructed)}")
