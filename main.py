from display import DisplayController
from diagnostics import Vehicle

from selected_metrics import getWatchedMetrics
from metrics import Metric, our_metrics

from getIPs import getIPs

import copy
import time

display = DisplayController()

vehicle = Vehicle() # Initialise Vehicle Object
# success = vehicle.connect() # Connect to the vehicle
success = False

if not success: # If connection fails
    while not success: # while it is failing
        
        display.clear_display()

        if vehicle.ELM_connected:
            display.warn(5, 20, "ELM connected")
            display.drawVirtualLED(10, 10, (0, 255, 0), 3) # ELM status LED (connected)
        else:
            display.warn(5, 20, "ELM disconnected")
            display.drawVirtualLED(10, 10, (255, 0, 0), 3) # ELM status LED (disconnected)
        
        display.drawVirtualLED(20, 10, (255, 0, 0), 3) # vehicle status LED (disconnected)

        ips = getIPs()
        ips_render_y_count = 30
        for ip in ips:
            display.warn(5, ips_render_y_count, ip)
            ips_render_y_count = ips_render_y_count + 10

        display.refresh(None)

        time.sleep(1)
        success = vehicle.connect() # reconnect

text_metrics = getWatchedMetrics() # get all user selected metrics to watch
watched_metrics = []

for metric in text_metrics:
    got_metric = copy.deepcopy(our_metrics[metric]) # don't affect our_metrics in metrics.py
    got_metric.setVehicle(vehicle) # So it knows where to send commands
    # got_metric.startWatching() # Subscribe
    watched_metrics.append(got_metric)

vehicle.start()

while True:

    # time.sleep()
    value1 = watched_metrics[0].getValue()
    value2 = watched_metrics[1].getValue()
    value3 = watched_metrics[2].getValue()

    label_values = [0, 2500, 5000, 7500, 10000]
    label_text = ["0", "2.5", "5", "7.5", "10"]
    low = 0
    high = 10000

    display.setNeedle(label_values, label_text, low, high, value1)
    display.setLowerValue(value2)
    display.setMiddleValue(value3)

    if vehicle.ELM_connected:
        display.drawVirtualLED(10, 10, (0, 255, 0), 3) # ELM status LED (connected)

    if vehicle.connected:
        display.drawVirtualLED(20, 10, (0, 255, 0), 3) # vehicle status LED (disconnected)
    else:
        display.drawVirtualLED(20, 10, (255, 0, 0), 3) # vehicle status LED (disconnected)

    display.refresh(value1)