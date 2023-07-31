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
        return self.m  * self.g * np.sin(theta) 

    def smooth_acceleration(self, v, a, n_avg = 5):
        '''for unrealistic acceleration and jerk values, replace with 
        moving average acceleration value.'''
        for i in range(len(a)):
            if v[i] < 2: ## adjust values based on speed threshold
                if a[i] < -3 or a[i] > 3: 
                    if i > n_avg: 
                        a[i] = np.mean(a[i-n_avg:i])
                    else: ## if at the beginning, replace with average a
                        a[i] = np.mean(a)
            else:
                if a[i] < -6 or a[i] > 0.5: 
                    if i > n_avg: 
                        a[i] = np.mean(a[i-n_avg:i])
                    else: 
                        a[i] = np.mean(a)

        jerk = np.diff(a, prepend=0)
        for i in range(len(jerk)):
            if abs(jerk[i]) > 2: 
                if i > n_avg: 
                    a[i] = np.mean(a[i-n_avg:i])
                else: ## if at the beginning, replace with average a
                    a[i] = np.mean(a)

        ## smoothing option with hanning window
        # window_size = 10 (10 second window)
        # win = signal.windows.hann(window_size)
        # filtered = signal.convolve(sig, win, mode='same') / sum(win)
        return a

    def get_power(self, v, theta):
        '''get power based on drag force, 
        gravitational force, and rider acceleration'''
        if np.isscalar(v):
            a_est = 0
        else: 
            a_est = -1 * np.diff(v, prepend=0) ## numerical derivative @ 1hz
            a_est = self.smooth_acceleration(v, a_est)
            # plt.plot(a_est)
            # plt.show()
        p_net = self.m * a_est * v 
        power = np.array((-1 * self.get_drag_force(v) + self.get_grav_force(theta)) * v + p_net)
        power[power < 0] = 0 ## zero out negative power values
        return power

    def update_drag_curve(self, t, v, theta):
        '''updates drag curve after adjusting velocity and acceleration curves by 
        the incline of the rider'''
        eps = 1e-10
        ## adjust v_coeffs by current inclination 
        v_adj = v - (0.5 * self.g * np.sin(theta)) 
        v_coeffs = np.polyfit(t, v_adj, self.fit_deg)
        a_coeffs = np.polyder(v_coeffs)
        a = np.polyval(a_coeffs, t)
        ## adjust a_coeffs by current inclination
        a_adj = a - self.g * np.sin(theta)
        v_fit = np.polyval(v_coeffs, t)
        self.av_coeffs = np.polyfit(v_fit, a_adj, self.fit_deg)


if __name__ == "__main__": ## stops execution when imported
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


