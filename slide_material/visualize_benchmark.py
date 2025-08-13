from matplotlib import pyplot as plt
x=list(range(2,11))
y1=[1.000000,2.000000,1.613000,1.902100,1.862933,1.995143,2.246786,2.288694,2.426800]
y2=[1.000000,2.000000,2.002500,2.548000,3.028400,3.434143,3.784107,4.040167,4.325267]
y21=[1.000000,1.666667,1.788500,2.421100,2.912000,3.330048,3.654679,3.938944,4.251978]
y22=[1.000000,1.666667,1.704333,2.055300,2.310533,2.547476,2.813214,3.090722,3.438511]
y3=[1.000000,1.666667,1.644333,1.785200,1.831067,1.969190,2.169000,2.396833,2.677178]
plt.plot(x,y1,'s:',label='default',color='#777')
plt.plot(x,y2,'o-',label='greedy')
plt.plot(x,y21,'o-',label='swap0')
plt.plot(x,y22,'o-',label='reorder')
plt.plot(x,y3,'o-',label='beam search')
plt.legend()
plt.grid(alpha=0.3)
plt.title('Benchmark on Complete Graph')
plt.xlabel('Number of qubits')
plt.ylabel('Expansion ratio')
plt.show()
