from display import DisplayController, TextWidget, VirtualLED, CircularGauge
from PIL import ImageFont
from time import sleep
from random import randint

display = DisplayController()

fontAFile = "Inter_18pt-Medium.ttf"
fontA = ImageFont.truetype(fontAFile, 14)

info_text = TextWidget((20, 20), fontA, (255, 255, 255))
info_text.text = "Hello World!"
display.add_widget(info_text)

elm_led = VirtualLED((5, 5), (255, 0, 0), 5)
display.add_widget(elm_led)

display.clear_display()

# display.setNeedle(label_values, label_text, low, high, value)
# display.setLowerValue(value)
# display.setMiddleValue(value)

gauge = CircularGauge(center=(40, 90), low=0, high=100,
                      label_values=[0, 25, 50, 75, 100], label_text=["0", "25", "50", "75", "100"],
                      fontFile=fontAFile, radius_outer=30, radius_inner=20)
#display.add_widget(gauge)

metric1 = TextWidget((20, 20), fontA, (255, 255, 255))
metric2 = TextWidget((20, 40), fontA, (255, 255, 255))
metric3 = TextWidget((20, 60), fontA, (255, 255, 255))

metric1.text = "Oil temp: 56°C"
metric2.text = "RPM: 1500rpm"
metric3.text = "Fuel_level: 75%"

display.add_widget(metric1)
display.add_widget(metric2)
display.add_widget(metric3)


while True:
    sleep(5)
    metric1.text = "Oil temp: " + str(randint(20, 120)) + "°C"
    metric2.text = "RPM: " + str(randint(800, 4000)) + "rpm"
    metric3.text = "Fuel_level: " + str(randint(0, 100)) + "%"
    display.refresh()
    # for led_color in [(255, 0, 0), (0, 255, 0), (0, 0, 255)]:
    #     elm_led.setColour(led_color)
    #     #display.clear_display()
    #     sleep(1)
    #     display.refresh()
