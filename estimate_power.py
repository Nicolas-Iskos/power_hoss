import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt

# Based on provided coast-down intervals, estimates power
class Power:
    def __init__(self, m):
        # physics parameters
        self.m = m
        self.cd = 0
        self.g = 9.81
        
        # heuristic parameters used to update drag curve
        self.fit_deg = 2
        self.look_back_length = 3
        
        # latent data used for updating drag curve
        self.look_back_coeffs = np.zeros((self.look_back_length, self.fit_deg + 1))
        self.look_back_weights = np.zeros((self.look_back_length, self.look_back_length))
        self.look_back_weights[1][1] = 1

        # drag curve
        self.av_coeffs = np.empty((self.fit_deg + 1,))

    def get_drag_force(self, v):
        return self.m * np.polyval(self.av_coeffs, v)

    def get_power(self, v):
        return -1 * self.get_drag_force(v) * v

    def get_av_coeffs(self, t, v):
        v_coeffs = np.polyfit(t, v, self.fit_deg)
        a_coeffs = np.polyder(v_coeffs)
        a = np.polyval(a_coeffs, t)
        return np.polyfit(v, a, self.fit_deg)

    def get_run_weight(self, t, v):
        # for now, just weight based on the number of points
        # This method can be improved later
        return np.size(t)

    # update drag coeffs used to estimate instantaneous power
    def update_drag_curve(self, t, v):
        # discard oldest set of coefficients & weights
        self.look_back_coeffs = np.roll(self.look_back_coeffs, shift=1, axis=1)
        self.look_back_weights = np.roll(self.look_back_weights, shift=1, axis=(0,1))

        # get the coeffs for this run
        run_coeffs = self.get_av_coeffs(t, v)

        # update coeff matrix
        self.look_back_coeffs[0:self.fit_deg+1,0] = run_coeffs

        # update weight matrix
        self.look_back_weights[0][0] = self.get_run_weight(t, v)

        # normalize weight matrix
        norm_look_back_weights = np.divide(
            self.look_back_weights, 
            np.linalg.norm(self.look_back_weights, ord=1))

        # compute av curve using weighted average of coeffs
        weighted_coeffs = np.matmul(self.look_back_coeffs, norm_look_back_weights)
        self.av_coeffs = np.sum(weighted_coeffs, axis=1)

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

test_speed = 10
print(p.get_power(test_speed))