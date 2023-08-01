from estimate_power import Power
from get_coast_down import get_intervals
from process_data import load_cleaned_data
import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import globvars


## import ride data and find coast down intervals
ride_number = globvars.ride_number
ride_data = load_cleaned_data(ride_number)
v = np.array(ride_data['Speed (MPH)'])
t = np.array(ride_data['Time'])
theta = np.array(ride_data['Incline'])
p = Power(98)
coast_down_intervals = get_intervals(v)
v_regions = []
theta_regions = []
for interval in coast_down_intervals:
    v_regions.append(v[interval[0]:interval[1]])
    theta_regions.append(theta[interval[0]:interval[1]])

## calculate power for each set of coefficients to see differences
power_curves = []
for v_region, theta_region in zip(v_regions, theta_regions):
    t = np.arange(len(v_region))
    p.update_drag_curve(t, v_region, theta_region)
    print("Power est (w) at 20 mph with these coeff: ", p.get_power(20/2.237,0))
    power_curves.append(p.get_power(v / 2.237, theta)) ## convert to m/s
print("mean power across ride (w): ", np.mean(power_curves))
    
## plot inclination    
# plt.plot(theta)
# plt.show()
## plot power curves
# for data in power_curves:
#     plt.plot(data)
# plt.show()



    





