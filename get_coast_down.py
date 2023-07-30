import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

ride_number = 2
filepath = "/Users/josheverts/power_hoss/ride_" + str(ride_number) + "_cleaned.csv"
ride_data = pd.read_csv(filepath)
speeds = ride_data['Speed (MPH)']
altitudes = ride_data['Altitude']
grade = np.tan(ride_data['Incline'])*100


''' simple algorithm to find coast-down data:
    perform simple running average smoothing, then:
    1) look for peaks and troughs over candidate heigths and ranges
    2) assign every trough to a unique peak ''' 


# min_peak_speed gives mininum speed to register a coast-down
# min_stop_speed gives speed at which to stop a coast-down
v_min = 17
v_stop = 10
def coast_down(speeds, min_peak_speed = v_min, min_stop_speed = v_stop, 
                peak_width = 30, peak_sep = 30):

    ## perform moving average smoothing 
    n_avg = 5
    speeds = np.convolve(speeds, np.ones(n_avg)/n_avg)
    t = np.arange(len(speeds))

    # Find indices of peaks
    peak_idx, _ = find_peaks(speeds, height=min_peak_speed, 
                                width=peak_width, distance = peak_sep)

    # Find indices of valleys (from inverting the signal)
    # inv_speed_threshold = (-1*speeds+coast_down_min_speed)+min_peak_speed
    valley_idx, _ = find_peaks(-1*speeds, height=-min_stop_speed, 
                            width=peak_width/2)

    ## keep valley indices if valley immediately follows a peak
    ## save all peak indices
    peak_matches = []
    valley_matches = []
    for i in range(len(valley_idx)):
        min_dist = np.inf
        min_ind = peak_idx[0]
        for j in range(len(peak_idx)):
            if peak_idx[j] < valley_idx[i]: ## find closest peak
                dist = valley_idx[i] - peak_idx[j]
                if dist < min_dist:
                    min_dist = dist
                    min_ind = peak_idx[j]
        if min_ind not in peak_matches:
            peak_matches.append(min_ind)
            valley_matches.append(valley_idx[i])
        # print(peak_matches)
        # print(valley_matches)
    return peak_matches, valley_matches, t

peak_matches, valley_matches, t = coast_down(speeds)

def plot_peaks(t, speeds, min_peak_speed=v_min):
    # Plot signal
    plt.plot(t, speeds)
    ## plot peak search range
    plt.plot([min(t), max(t)], [min_peak_speed, min_peak_speed], '--')
    plt.plot([min(t), max(t)], [-min_peak_speed, -min_peak_speed], '--')
    # Plot peaks (red) and valleys (blue)
    plt.plot(t[peak_matches], speeds[peak_matches], 'r.')
    plt.plot(t[valley_matches], speeds[valley_matches], 'b.')
    plt.show()

def get_intervals(speeds):
    peak_matches, valley_matches, t = coast_down(speeds)
    ranges = []
    for p, v in zip(peak_matches, valley_matches):
        ranges.append([p,v])
    return ranges
