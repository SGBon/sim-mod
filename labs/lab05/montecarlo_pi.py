import time
import numpy as np

N_RUNS = 2

def estimate_pi(n_samples,rnd_seed=0):
    np.random.seed(rnd_seed)
    samples_x = np.random.uniform(0,1,n_samples)
    samples_y = np.random.uniform(0,1,n_samples)
    distances = np.sqrt(np.power(samples_x,2) + np.power(samples_y**2,2))
    return 4.0 * np.sum(distances <= 1.0) / float(n_samples)


averages = []
for i in range(2,8):
    total = 0
    for run in range(N_RUNS):
        n_samples = pow(10,i)
        result = estimate_pi(n_samples,run)
        print result
        total += result
    averages.append(total/N_RUNS)

print averages
