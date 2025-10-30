from display import DisplayController, TextWidget, VirtualLED, CircularGauge
from diagnostics import Vehicle
from PIL import ImageFont

from getIPs import getIPs

import copy
import time
import threading

display = DisplayController(90)

fontAFile = "Inter_18pt-Medium.ttf"
fontA = ImageFont.truetype(fontAFile, 14)

vehicle = Vehicle() # Initialise Vehicle Object

from webserver import run_webserver, watched_metrics_names, load_watched_metrics, get_watched_metrics_names, set_watched_metrics_names
#import webserver
from selected_metrics import getWatchedMetrics
from metrics import Metric, our_metrics

#text_metrics = getWatchedMetrics() # get all user selected metrics to watch
watched_metrics = []

def refresh_watched_metrics():
    """
    Populate the global watched_metrics list with Metric objects corresponding
    to the currently selected watched_metrics_names (dictionary keys).
    """
    global watched_metrics
    # global watched_metrics_names
    names = get_watched_metrics_names() or []

    # metrics_lock = threading.Lock()
    # with metrics_lock:
    #     watched_metrics_names = get_watched_metrics_names()

    watched_metrics = []

    # if vehicle.connected:
    # for metric_name in watched_metrics_names:
    for metric_name in names:
        if metric_name in our_metrics:
            got_metric = copy.deepcopy(our_metrics[metric_name])
            got_metric.setVehicle(vehicle)
            watched_metrics.append(got_metric)
    # else:
        # print("Unable to refresh watched metrics as vehicle is not connected (vehicle.connected)")

threading.Thread(target=run_webserver, daemon=True).start()
refresh_watched_metrics()

success = False
active_status_led_toggle = False

while not success: # while it is failing
    
    display.clear_display()
    display.widgets = []

    info_text = TextWidget((5, 20), fontA, (255, 255, 255))
    elm_led = VirtualLED((5, 5), (255, 0, 0), 3)

    active_status_led_toggle_led = VirtualLED((155, 5), (0, 0, 0), 3)
    if active_status_led_toggle:
        active_status_led_toggle_led.setColour((0, 0, 255))
        active_status_led_toggle = False
    else:
        active_status_led_toggle = True
    display.add_widget(active_status_led_toggle_led)

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

#        for metric in text_metrics:

    watched_metrics_names = get_watched_metrics_names()
    refresh_watched_metrics()

    for metric in watched_metrics:
        info_text = TextWidget((5, ips_render_y_count), fontA, (255, 255, 255))
        info_text.text = metric.getShort() + ": No car yet"
        ips_render_y_count = ips_render_y_count + 20
        display.add_widget(info_text)

    display.refresh()

    time.sleep(1)
    success = vehicle.connect() # reconnect

active_watched_metrics = []

for metric in watched_metrics:
    got_metric = copy.deepcopy(our_metrics[metric.getKey()]) # don't affect our_metrics in metrics.py
    got_metric.setVehicle(vehicle) # So it knows where to send commands
    # got_metric.startWatching() # Subscribe
    active_watched_metrics.append(got_metric)

vehicle.start()

while True:

    watched_metrics_names = get_watched_metrics_names()
    refresh_watched_metrics()

    display.clear_display()
    display.widgets = []

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

    # Display watched metrics

    y = 20

    for metric in active_watched_metrics:
        value = metric.getValue() if vehicle.connected else "No car yet"
        display.add_widget(TextWidget((5, y), fontA, (255, 255, 255)))
        display.widgets[-1].text = f"{metric.getShort()}: {value} {metric.getUnit() if vehicle.connected else ''}"
        y += 20

    display.refresh()
    time.sleep(0.5)