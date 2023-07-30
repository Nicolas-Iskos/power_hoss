import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import re 

ride_number = 2
filepath = "/Users/josheverts/Downloads/ride_data_" + str(ride_number) + ".txt"
print(filepath)
speeds = []
times = []
altitudes = []
distances = []

header_length = 17
## read file and extract data
with open(filepath, 'r') as f:
    for i, line in enumerate(f):
        if i > header_length: ## remove header
            if re.search('Speed', line):
                speed = re.findall(r'\d{1,3}.\d{1,3}', line)
                speeds.append(float(speed[0]))
            if re.search('Time', line):
                time = re.findall(r'\d{2}:\d{2}:\d{2}.\d{3}', line)
                times.append(time[0])
            if re.search('Altitude', line):
                altitude = re.findall(r'\d{1,4}.\d', line)
                altitudes.append(float(altitude[0]))
            if re.search('Distance', line):
                distance = re.findall(r'\d{1,4}.\d', line)
                distances.append(float(distance[0]))


## convert to numpy arrays
altitudes = np.array(altitudes)
distances = np.array(distances)
times = np.arange(len(distances))
speeds = np.array(speeds)
speeds = speeds * 2.237 ## m/s to mph

## calculate elevation angles from altitude and distance 
altitude_change = np.diff(altitudes)
distance_change = np.diff(distances)

## remove outliers and calculate inclination
## unphysical angles when traveling very slow are reset to 0
distance_eps = 0.5
distance_thresholded = np.where(distance_change < distance_eps)
altitude_change[distance_thresholded[0]] = 0
distance_change[distance_thresholded[0]] = 1e5
inclination = np.arctan(altitude_change/distance_change) 
grade = (altitude_change/distance_change) * 100

## plot data
# plt.plot(speeds)
# plt.plot(altitudes)
# plt.plot(grade)
# plt.show()

## export as csv data 
export_dict = {'Time': times[1:],
        'Speed (MPH)': speeds[1:], 
        'Altitude': altitudes[1:], 
        'Distance': distances[1:], 
        'Incline': inclination}
df_export = pd.DataFrame(export_dict)       
df_export.to_csv("ride_" + str(ride_number) + "_cleaned.csv") 



