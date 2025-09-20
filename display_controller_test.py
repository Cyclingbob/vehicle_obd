from display import DisplayController

display = DisplayController()

label_values = [0, 2500, 5000, 7500, 10000]
label_text = ["0", "2.5", "5", "7.5", "10"]
low = 0
high = 10000
value = 5600

display.clear_display()
display.setNeedle(label_values, label_text, low, high, value)
display.setLowerValue(value)
display.setMiddleValue(value)
display.refresh(value)