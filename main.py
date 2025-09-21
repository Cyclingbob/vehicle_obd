from display import DisplayController, TextWidget, VirtualLED, CircularGauge
from diagnostics import Vehicle
from PIL import ImageFont

from selected_metrics import getWatchedMetrics
from metrics import Metric, our_metrics

from getIPs import getIPs

import copy
import time

display = DisplayController(90)

fontAFile = "Inter_18pt-Medium.ttf"
fontA = ImageFont.truetype(fontAFile, 14)

vehicle = Vehicle() # Initialise Vehicle Object
# success = vehicle.connect() # Connect to the vehicle
success = False

text_metrics = getWatchedMetrics() # get all user selected metrics to watch
watched_metrics = []

if not success: # If connection fails
    while not success: # while it is failing
        
        display.clear_display()
        display.widgets = []

        info_text = TextWidget((5, 20), fontA, (255, 255, 255))
        elm_led = VirtualLED((5, 5), (255, 0, 0), 3)

        if vehicle.ELM_connected:
            info_text.text = "ELM connected"
            elm_led.setColour((0, 255, 0)) # ELM status LED (connected)
        else:
            info_text.text = "ELM disconnected"
            elm_led.setColour((255, 0, 0)) # ELM status LED (disconnected)

        display.add_widget(info_text)
        display.add_widget(elm_led)

        car_led = VirtualLED((15, 5), (255, 0, 0), 3) # vehicle status LED (disconnected)
        display.add_widget(car_led)

        ips = getIPs()
        ips_render_y_count = 40
        for ip in ips:
            info_text = TextWidget((5, ips_render_y_count), fontA, (255, 255, 255))
            info_text.text = ip
            ips_render_y_count = ips_render_y_count + 10
            display.add_widget(info_text)

        ips_render_y_count = ips_render_y_count + 10

        for metric in text_metrics:
            info_text = TextWidget((5, ips_render_y_count), fontA, (255, 255, 255))
            info_text.text = metric + ": No car yet"
            ips_render_y_count = ips_render_y_count + 20
            display.add_widget(info_text)

        display.refresh()

        time.sleep(1)
        success = vehicle.connect() # reconnect

for metric in text_metrics:
    got_metric = copy.deepcopy(our_metrics[metric]) # don't affect our_metrics in metrics.py
    got_metric.setVehicle(vehicle) # So it knows where to send commands
    # got_metric.startWatching() # Subscribe
    watched_metrics.append(got_metric)

vehicle.start()

while True:

    display.clear_display()
    display.widgets = []

    # time.sleep()
    value1 = watched_metrics[0].getValue()
    value2 = watched_metrics[1].getValue()
    value3 = watched_metrics[2].getValue()

    # label_values = [0, 2500, 5000, 7500, 10000]
    # label_text = ["0", "2.5", "5", "7.5", "10"]
    # low = 0
    # high = 10000

    # display.setNeedle(label_values, label_text, low, high, value1)

    elm_led = VirtualLED((5, 5), (255, 0, 0), 3)
    car_led = VirtualLED((15, 5), (255, 0, 0), 3) # vehicle status LED (disconnected)

    if vehicle.ELM_connected:
        elm_led.setColour((0, 255, 0)) # ELM status LED (connected) # ELM status LED (connected)

    if vehicle.connected:
        elm_led.setColour((0, 255, 0)) # ELM status LED (connected) # vehicle status LED (disconnected)
        car_led.setColour((0, 255, 0))
    else:
        car_led.setColour((255, 0, 0))

    display.add_widget(elm_led)
    display.add_widget(car_led)

    metric1 = TextWidget((5, 20), fontA, (255, 255, 255))
    metric1.text = f"{watched_metrics[0].getName()}: {value1} {watched_metrics[0].getUnit()}"

    metric2 = TextWidget((5, 40), fontA, (255, 255, 255))
    metric2.text = f"{watched_metrics[1].getName()}: {value2} {watched_metrics[1].getUnit()}"

    metric3 = TextWidget((5, 60), fontA, (255, 255, 255))
    metric3.text = f"{watched_metrics[2].getName()}: {value2} {watched_metrics[2].getUnit()}"

    display.add_widget(metric1)
    display.add_widget(metric2)
    display.add_widget(metric3)

    display.refresh()