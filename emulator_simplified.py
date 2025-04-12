from PIL import Image, ImageDraw, ImageFont
import st7735
import math
import time
import random


# GPIO connections

SPI_BUS = 0
CS = 0
DC = 24
BACKLIGHT=22
RST=25
WIDTH = 128 + 4
HEIGHT = 160
ROTATION = 0
INVERT = False
BGR = False

# UI Colours
BACKGROUND = (0,0,0)
CIRCULAR_DIAL_EXTERIOR_BACKGROUND = (200,200,200)
CIRCULAR_DIAL_INTERIOR_BACKGROUND = (0,0,0)
NEEDLE_COLOUR = (255,0,0)

# FONTS
SMALL_FONT_NAME = "Inter_18pt-Medium.ttf"
SMALL_FONT = ImageFont.truetype(SMALL_FONT_NAME, 14)

FONT_NAME = "Inter_24pt-Black.ttf"
STANDARD_FONT = ImageFont.truetype(FONT_NAME, 28)
middle_font = ImageFont.truetype(FONT_NAME, 22)

disp = st7735.ST7735(
    port=SPI_BUS, cs=CS, dc=DC, backlight=BACKLIGHT, rst=RST,
    width=WIDTH, height=HEIGHT, rotation=ROTATION, invert=INVERT ,bgr=BGR
)

CENTER = (WIDTH // 2, 65)

num_samples = 200  # 20 Hz for 10 seconds
rpm_values = []
current_rpm = random.randint(1200, 3000)  # Start at idle

for _ in range(num_samples):
    # Simulate realistic RPM changes
    delta = random.randint(-300, 300)  # Small fluctuations
    current_rpm = max(1200, min(9000, current_rpm + delta))  # Clamp values
    rpm_values.append(current_rpm)


img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
draw = ImageDraw.Draw(img)

def drawLowerValue(draw, text, font, fontColour):

    RECT_HEIGHT = 35
    TOP_Y_CORD = HEIGHT - 5
    BOTTOM_Y_CORD = TOP_Y_CORD - RECT_HEIGHT

    _, _, w, h = draw.textbbox((0, 0), text, font=font)
    draw.rectangle(((WIDTH-w)//2 - 5, BOTTOM_Y_CORD, (WIDTH+w)//2 + 5, TOP_Y_CORD), fill=(0, 0, 0))
    draw.text(((WIDTH-w)/2, BOTTOM_Y_CORD), text, font=font, fill=fontColour)

def drawMiddleValue(draw, text, font, fontColour):
    _, _, w, h = draw.textbbox((0, 0), text, font=font)
    RECT_HEIGHT = 35
    TOP_Y_CORD = HEIGHT - 70
    BOTTOM_Y_CORD = TOP_Y_CORD - RECT_HEIGHT

    draw.rectangle(((WIDTH-w)//2 - 5, BOTTOM_Y_CORD, (WIDTH+w)//2 + 5, TOP_Y_CORD), fill=(0, 0, 0))
    draw.text(((WIDTH-w)/2, BOTTOM_Y_CORD), text, font=font, fill=fontColour)

def drawCircularDial(draw):
    r_outer = 60
    r_inner = 40
    x = WIDTH / 2
    y = 65

    # leftUpPoint = (x-r_outer, y-r_outer)
    # rightDownPoint = (x+r_outer, y+r_outer)
    # twoPointList = [leftUpPoint, rightDownPoint]
    # draw.eclipse(something)

    draw.pieslice(
        [(x - r_outer, y - r_outer), (x + r_outer, y + r_outer)],  # Bounding box
        # start=225-90, end=135-90,  # Arc range
        start=210-90, end=150-90,  # Arc range
        fill=CIRCULAR_DIAL_EXTERIOR_BACKGROUND  # Grey color
    )

    draw.ellipse([(x - r_inner, y - r_inner), (x + r_inner, y + r_inner)], fill=CIRCULAR_DIAL_INTERIOR_BACKGROUND)  # White cutout

def value_to_angle(value, low, high):

    ANGLE_START = 225
    ANGLE_END = -45

    """Convert a value to an angle in the gauge range."""
    normalized = (value - low) / (high - low)  # Normalize between 0 and 1
    return ANGLE_START - (normalized * (ANGLE_START - ANGLE_END))  # Map to 270° range

def drawNeedle(draw, value, low, high, erase=False):
    angle = value_to_angle(value, low, high)
    rad = math.radians(angle)
    
    INNER_RADIUS = 40  # Inner white circle radius
    OUTER_RADIUS = 59  # Outer grey ring radius
    
    start_x = CENTER[0] + INNER_RADIUS * math.cos(rad)
    start_y = CENTER[1] - INNER_RADIUS * math.sin(rad)
    
    end_x = CENTER[0] + OUTER_RADIUS * math.cos(rad)
    end_y = CENTER[1] - OUTER_RADIUS * math.sin(rad)

    color = CIRCULAR_DIAL_EXTERIOR_BACKGROUND if erase else NEEDLE_COLOUR # Use dial background color to erase
    
    draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=10)

def drawGaugeNumbers(draw, font, font_color):

    NUMBER_POS_RADIUS = 50  # Position inside the grey ring
    label_values = [0, 2500, 5000, 7500, 10000]  # Corresponding RPM values
    label_texts = ["0", "2.5", "5", "7.5", "10"]  # Displayed text

    for value, text in zip(label_values, label_texts):
        angle = value_to_angle(value, 0, 10000)
        rad = math.radians(angle)
        
        x = CENTER[0] + NUMBER_POS_RADIUS * math.cos(rad)
        y = CENTER[1] - NUMBER_POS_RADIUS * math.sin(rad)
        
        w, h = draw.textbbox((0, 0), text, font=font)[2:]  # Get text size
        draw.text((x - w / 2, y - h / 2), text, font=font, fill=font_color)


last_value = None  # Store the previous value

def refresh(value):
    global last_value
    if last_value is not None:
        drawNeedle(draw, last_value, 0, 10000, erase=True)  # Erase previous needle

    drawNeedle(draw, value, 0, 10000, erase=False)  # Draw new needle
    drawLowerValue(draw, str(value), STANDARD_FONT, (255, 255, 255))
    drawMiddleValue(draw, str(value), middle_font, (255, 255, 255))
    drawGaugeNumbers(draw, SMALL_FONT, (0, 0, 0))

    disp.display(img)
    last_value = value  # Store current value for next refresh

drawCircularDial(draw)

# for value in range(0, 10000, 500):
#     refresh(value)
#     time.sleep(0.05)

for value in rpm_values:
    refresh(value)
    time.sleep(0.05)
    
# text_box = draw.text((30, 130), "2500", (0, 0, 0), font=font)