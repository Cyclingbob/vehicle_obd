from display import DisplayController, TextWidget, VirtualLED, CircularGauge
from PIL import ImageFont
from time import sleep

display = DisplayController()

label_values = [0, 2500, 5000, 7500, 10000]
label_text = ["0", "2.5", "5", "7.5", "10"]
low = 0
high = 10000
value = 5600

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

gauge = CircularGauge(center=display.CENTER, low=0, high=100, label_values=[0,50,100], label_text=["0","50","100"])
display.add_widget(gauge)

while True:
    for led_color in [(255, 0, 0), (0, 255, 0), (0, 0, 255)]:
        elm_led.setColour(led_color)
        #display.clear_display()
        sleep(1)
        display.refresh()
