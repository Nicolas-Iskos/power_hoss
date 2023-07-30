from estimate_power import Power
from get_coast_down import get_intervals
import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt

## import ride data and find coast down intervals
ride_data = pd.read_csv("ride_2_cleaned.csv")
v = np.array(ride_data['Speed (MPH)']) 
t = np.array(ride_data['Time'])
theta = np.array(ride_data['Incline'])
p = Power(85)
coast_down_intervals = get_intervals(v)
interval_regions = []
for interval in coast_down_intervals:
    interval_regions.append(v[interval[0]:interval[1]])

## calculate power for each set of coefficients to see differences
power_curves = []
for region in interval_regions:
    t = np.arange(len(region))
    p.update_drag_curve(t, region)
    print("Power est (w) at 20 mph with these coeff: ", p.get_power(20/2.237,0))
    power_curves.append(p.get_power(v / 2.237, theta)) ## convert to m/s
print("mean power across ride (w): ", np.mean(power_curves))

## plot power curves
for data in power_curves:
    plt.plot(data)
plt.show()



    





