import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt

# Based on provided coast-down intervals, estimates power
class Power:
    def __init__(self, m):
        self.m = m
        self.cd = 0
        self.g = 9.81
        self.fit_deg = 2
        self.av_coeffs = []

    def get_drag_force(self, v):
        return self.m * np.polyval(self.av_coeffs, v)

    def get_grav_force(self, theta):
        return self.m  * self.g * math.sin(theta) * self.m

    def get_power(self, v, theta):
        return (-1 * self.get_drag_force(v) + self.get_grav_force(theta)) * v

    def update_drag_curve(self, t, v):
        eps = 1e-10
        v_coeffs = np.polyfit(t, v, self.fit_deg)
        a_coeffs = np.polyder(v_coeffs)
        a = np.polyval(a_coeffs, t)
        self.av_coeffs = np.polyfit(v, a, self.fit_deg)

# read data
filepath = 'rides/ride1.csv'
num_metadata_rows_top = 4
num_metadata_rows_bottom = 1
df = pd.read_csv(
    filepath, 
    skiprows=num_metadata_rows_top, 
    skipfooter=num_metadata_rows_bottom, 
    header=0,
    engine='python')

# figure out how to determine these coast-down intervals from the data
coast_down_start = 8219
coast_down_end = 8351
t = df['Time'].to_numpy(dtype=float)[coast_down_start:coast_down_end]
v = df['Speed (MPH)'].to_numpy(dtype=float)[coast_down_start:coast_down_end]
# convert to m/s
v = np.divide(v, 2.237)

m = 70
p = Power(m)

# provide a coast-down interval to update the power estimation
p.update_drag_curve(t, v)

test_speed = 15
test_incline = 0
print(p.get_power(test_speed, test_incline))