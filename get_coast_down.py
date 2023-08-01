import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, find_peaks_cwt
from scipy.signal import hann
from scipy.interpolate import interp1d
from process_data import load_cleaned_data
import globvars

## import ride data
# filepath = "/Users/josheverts/power_hoss/ride_" + str(ride_number) + "_cleaned.csv"
# ride_data = pd.read_csv(filepath)
ride_number = globvars.ride_number
ride_data = load_cleaned_data(ride_number)
speeds = ride_data['Speed (MPH)']
altitudes = ride_data['Altitude']
grade = np.tan(ride_data['Incline'])*100

''' simple algorithm to find coast-down data:
    perform simple running average smoothing, then:
    1) look for peaks and troughs over candidate heights and ranges
    2) assign every trough to a unique peak ''' 


# min_peak_speed(mph) gives mininum speed to register a coast-down
# min_stop_speed(mph) gives speed at which to stop a coast-down
v_min = 17 
v_stop = 5
peak_sep = 20
def coast_down(speeds, min_peak_speed = v_min, min_stop_speed = v_stop, 
                peak_width = 15, peak_sep = 1):

    ## low-pass filter bumps and noise greater than 2 hz
    n_avg = 10
    x = np.linspace(-np.pi/4,np.pi/4,n_avg)
    kernel = np.sinc(x) 
    kernel_norm = kernel/sum(kernel)
    plt.plot(np.arange(0, len(speeds)), speeds) ## plot original speeds
    speeds = np.convolve(speeds, kernel_norm)
    plt.plot(np.arange(0,len(speeds)), speeds) ## plot smoothed speeds
    plt.title('Smoothed and Raw Velocities')
    plt.show()
    t = np.arange(len(speeds))

    ## Find indices of peaks
    peak_idx  = find_peaks_cwt(speeds, np.arange(5,15))

    ## Find indices of valleys (from inverting the signal)
    valley_idx  = find_peaks_cwt(-speeds, np.arange(5,15))

    ## keep valley indices if valley immediately follows a peak
    ## save all peak indices
    peak_matches = [-1]
    valley_matches = []
    for i in range(len(valley_idx)):
        min_dist = np.inf
        min_ind = -1
        for j in range(len(peak_idx)):
            if peak_idx[j] < valley_idx[i]: ## find closest peak
                dist = valley_idx[i] - peak_idx[j]
                if dist < min_dist:
                    min_dist = dist
                    min_ind = peak_idx[j]
        if min_ind not in peak_matches:
            peak_matches.append(min_ind)
            valley_matches.append(valley_idx[i])

    return peak_matches[1:], valley_matches, speeds, t

peak_matches, valley_matches, speeds, t = coast_down(speeds)

def plot_peaks(t, speeds, min_peak_speed=v_min):
    # Plot signal
    plt.plot(t, speeds)
    plt.ylabel('v (mph)')
    plt.title("Calculated coast-down intervals")

    ## plot peak search range
    plt.plot([min(t), max(t)], [v_min, v_min], '--')
    plt.plot([min(t), max(t)], [-v_stop, -v_stop], '--')

    # Plot peaks (red) and valleys (blue)
    plt.plot(t[peak_matches], speeds[peak_matches], 'r.', label = 'start')
    plt.plot(t[valley_matches], speeds[valley_matches], 'b.', label = 'end')
    plt.legend()
    plt.show()

# plt.plot(speeds)
# plt.show()
# plot_peaks(np.arange(len(speeds)), speeds)

def get_intervals(speeds):
    peak_matches, valley_matches, speeds, t = coast_down(speeds)
    ranges = []
    for p, v in zip(peak_matches, valley_matches):
        ranges.append([p,v])
    return ranges
