import time
import numpy as np

N_RUNS = 2

def estimate_pi(n_samples,rnd_seed=0):
    np.random.seed(rnd_seed)
    samples_x = np.random.uniform(0,1,n_samples)
    samples_y = np.random.uniform(0,1,n_samples)
    distances = np.sqrt(np.power(samples_x,2) + np.power(samples_y,2))
    return 4.0 * np.sum(distances <= 1.0) / float(n_samples)

averages = []
deviation = []
for i in range(2,9):
    total = 0
    approx = []
    for run in range(N_RUNS):
        n_samples = pow(10,i)
        approx.append(estimate_pi(n_samples,run))
    print "Aproximation", approx,pow(10,i)
    average = np.mean(approx)
    averages.append(average)
    deviation.append(np.abs(np.array(approx) - average))

deviation = np.array(deviation)
print "Averages: ", averages
print "Deviation from average", deviation
