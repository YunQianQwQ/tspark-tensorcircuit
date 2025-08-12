import numpy as np
import tensorcircuit as tc
import tensorflow as tf
import matplotlib.pyplot as plt

K = tc.set_backend("tensorflow")

T = 10

# n = 3
# edges = [[0, 1], [1, 2]]

n = 6
edges = [[0, 1], [3, 4], [2, 5], [0, 3], [4, 5], [1, 2], [1, 4]]

# n = 9
# edges = [[0, 1], [3, 4], [7, 8], [2, 5], [0, 3], [4, 5], [6, 7], [1, 2], [4, 7], [5, 8], [3, 6], [1, 4]]

#print(reg(n, edges, 1, 1))

def evo(c, n, E, step):
    dt = T / step
    for i in range(n):
        c.x(i)
        c.h(i)
    def A(t):
        return 1 - t / T
    def B(t):
        return t / T
    t = 0


    
    for j in range(step):
        for i in range(n):
            c.rx(i, theta =  2*A(t) * dt)
        for u, v in E:
            c.cnot(u, v)
            c.rz(v, theta = 2 * B(t) * dt)
            c.cnot(u, v)
        t += dt
    return c

c = tc.Circuit(n)
x = range(2**n)
y = evo(c, n, edges, 200).state().numpy()
y = np.abs(y)**2

for i in range(len(y)):
    if y[i] > 0.2:
        ind = i
        ans = np.zeros((n), dtype = int)
        for j in range(n):
            ans[j] = (ind >> (n - j - 1)) & 1
        print(f"State with significant probability: {ans}, Probability: {y[i]}")

labels = [format(i, f'0{n}b') for i in x]

plt.bar(x, y)
plt.xlabel('State Index')
plt.ylabel('Probability Amplitude')
plt.xticks(x, labels, rotation=90, fontsize=8)  # Rotate for readability
plt.tight_layout()  # Adjust layout to fit labels
plt.title('Quantum State Evolution')
plt.show()