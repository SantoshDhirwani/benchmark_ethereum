from scipy import interpolate
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

resultsDir = 'aggregated-results/'
minGasLimit = int(sys.argv[1])
maxGasLimit = int(sys.argv[2])
gasLimitStep = int(sys.argv[3])
minInterval = int(sys.argv[4])
maxInterval = int(sys.argv[5])
intervalStep = int(sys.argv[6])

x = np.arange(minInterval, maxInterval + intervalStep, intervalStep)
y = np.arange(minGasLimit, maxGasLimit + gasLimitStep, gasLimitStep)

xx, yy = np.meshgrid(x, y)
#df = pd.read_csv(resultsDir + 'data_transfer.csv')
with open(resultsDir + 'data_grid.csv', 'r') as f:
    l = [[int(num) for num in line.split(',')] for line in f]
print(l)
z = np.array(l).flatten()
print(z)
#z = np.sin(xx**2+yy**2)
f = interpolate.interp2d(x, y, z, kind='cubic')

xnew = np.arange(minInterval, maxInterval + intervalStep, 1)
ynew = np.arange(minGasLimit, maxGasLimit + gasLimitStep, 1000000)
znew = f(xnew, ynew)
print(znew)
#plt.plot(x, z[0, :], 'ro-', xnew, znew[0, :], 'b-')
#plt.show()