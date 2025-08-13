from matplotlib import pyplot as plt
x=list(range(2,11))
y1=[1.000000,2.000000,1.613000,1.902100,1.862933,1.995143,2.246786,2.288694,2.426800]
y2=[1.000000,2.000000,2.002500,2.548000,3.028400,3.434143,3.784107,4.040167,4.325267]
y3=[1.000000,1.666667,1.644333,1.785200,1.831067,1.969190,2.169000,2.396833,2.677178]
plt.plot(x,y1,'o-',label='default')
plt.plot(x,y2,'o-',label='greedy')
plt.plot(x,y3,'o-',label='beam search')
plt.legend()
plt.grid(alpha=0.3)
plt.title('Benchmark on Complete Graph')
plt.xlabel('Number of qubits')
plt.ylabel('Expansion ratio')
plt.show()
