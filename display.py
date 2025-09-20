from PIL import Image, ImageDraw, ImageFont
import st7735
import math

class DisplayController:
    def __init__(self):
        # Display Configuration
        self.SPI_BUS = 0
        self.CS = 0
        self.DC = 24
        self.BACKLIGHT = 22
        self.RST = 25
        self.WIDTH = 128 + 4
        self.HEIGHT = 160
        self.ROTATION = 90
        self.INVERT = False
        self.BGR = False
        
        # Colors
        self.BACKGROUND = (0, 0, 0)
        self.CIRCULAR_DIAL_EXTERIOR_BACKGROUND = (200, 200, 200)
        self.CIRCULAR_DIAL_INTERIOR_BACKGROUND = (0, 0, 0)
        self.NEEDLE_COLOUR = (255, 0, 0)
        
        # Fonts
        self.SMALL_FONT_NAME = "Inter_18pt-Medium.ttf"
        self.SMALL_FONT = ImageFont.truetype(self.SMALL_FONT_NAME, 14)
        self.FONT_NAME = "Inter_24pt-Black.ttf"
        self.STANDARD_FONT = ImageFont.truetype(self.FONT_NAME, 28)
        self.MIDDLE_FONT = ImageFont.truetype(self.FONT_NAME, 22)
        
        # Initialize Display
        self.disp = st7735.ST7735(
            port=self.SPI_BUS, cs=self.CS, dc=self.DC, backlight=self.BACKLIGHT, rst=self.RST,
            width=self.WIDTH, height=self.HEIGHT, rotation=self.ROTATION, invert=self.INVERT, bgr=self.BGR
        )
        
        self.CENTER = (self.WIDTH // 2, 65)
        
        # Create Image Canvas
        self.img = Image.new("RGB", (self.WIDTH, self.HEIGHT), self.BACKGROUND)
        self.draw = ImageDraw.Draw(self.img)
        self.last_needle_value = None  # Store last needle position

        self.clear_display()
        
        # Initial Dial Draw
        # self.draw_circular_dial()

    def clear_display(self):
        """Fills the screen with the background color and refreshes it."""
        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), fill=self.BACKGROUND)
        self.refresh(None)  # Update display
    
    def drawVirtualLED(self, x, y, colour, radius):
        x0 = x - radius
        x1 = x + radius
        y0 = y - radius
        y1 = y + radius
        # print(f"Drawing LED at: ({x0}, {y0}) to ({x1}, {y1}) with color {colour}")  # Debug output
        self.draw.ellipse((x0, y0, x1, y1), outline=None, fill=colour)
        
    def draw_lower_value(self, text, font, font_colour):
        RECT_HEIGHT = 35
        TOP_Y_CORD = self.HEIGHT - 5
        BOTTOM_Y_CORD = TOP_Y_CORD - RECT_HEIGHT
        _, _, w, h = self.draw.textbbox((0, 0), text, font=font)
        self.draw.rectangle(((self.WIDTH-w)//2 - 5, BOTTOM_Y_CORD, (self.WIDTH+w)//2 + 5, TOP_Y_CORD), fill=self.BACKGROUND)
        self.draw.text(((self.WIDTH-w)/2, BOTTOM_Y_CORD), text, font=font, fill=font_colour)

    def draw_middle_value(self, text, font, font_colour):
        RECT_HEIGHT = 35
        TOP_Y_CORD = self.HEIGHT - 70
        BOTTOM_Y_CORD = TOP_Y_CORD - RECT_HEIGHT
        _, _, w, h = self.draw.textbbox((0, 0), text, font=font)
        self.draw.rectangle(((self.WIDTH-w)//2 - 5, BOTTOM_Y_CORD, (self.WIDTH+w)//2 + 5, TOP_Y_CORD), fill=self.BACKGROUND)
        self.draw.text(((self.WIDTH-w)/2, BOTTOM_Y_CORD), text, font=font, fill=font_colour)

    def draw_circular_dial(self):
        r_outer = 60
        r_inner = 40
        x, y = self.CENTER
        start = 210 - 90
        end = 150 - 90
        self.draw.pieslice([(x - r_outer, y - r_outer), (x + r_outer, y + r_outer)], start=start, end=end, fill=self.CIRCULAR_DIAL_EXTERIOR_BACKGROUND)
        # self.draw.pieslice([(x - r_outer, y - r_outer), (x + r_outer, y + r_outer)], start=0, end=240, fill=self.CIRCULAR_DIAL_EXTERIOR_BACKGROUND)
        self.draw.ellipse([(x - r_inner, y - r_inner), (x + r_inner, y + r_inner)], fill=self.CIRCULAR_DIAL_INTERIOR_BACKGROUND)

    def value_to_angle(self, value, low, high):
        ANGLE_START = 225
        ANGLE_END = -45
        normalized = (value - low) / (high - low)
        return ANGLE_START - (normalized * (ANGLE_START - ANGLE_END))

    def draw_needle(self, value, low, high, erase=False):
        angle = self.value_to_angle(value, low, high)
        rad = math.radians(angle)
        INNER_RADIUS, OUTER_RADIUS = 40, 59
        start_x = self.CENTER[0] + INNER_RADIUS * math.cos(rad)
        start_y = self.CENTER[1] - INNER_RADIUS * math.sin(rad)
        end_x = self.CENTER[0] + OUTER_RADIUS * math.cos(rad)
        end_y = self.CENTER[1] - OUTER_RADIUS * math.sin(rad)
        color = self.CIRCULAR_DIAL_EXTERIOR_BACKGROUND if erase else self.NEEDLE_COLOUR
        self.draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=10)

    def draw_gauge_numbers(self, label_values, label_text, low, high, value):
        NUMBER_POS_RADIUS = 50
        
        for value, text in zip(label_values, label_text):
            angle = self.value_to_angle(value, low, high)
            rad = math.radians(angle)
            x = self.CENTER[0] + NUMBER_POS_RADIUS * math.cos(rad)
            y = self.CENTER[1] - NUMBER_POS_RADIUS * math.sin(rad)
            w, h = self.draw.textbbox((0, 0), text, font=self.SMALL_FONT)[2:]
            self.draw.text((x - w / 2, y - h / 2), text, font=self.SMALL_FONT, fill=(0, 0, 0))

    def setLowerValue(self, value):
        self.draw_lower_value(str(value), self.STANDARD_FONT, (255, 255, 255))
    
    def setMiddleValue(self, value):
        self.draw_middle_value(str(value), self.MIDDLE_FONT, (255, 255, 255))

    def setNeedle(self, label_values, label_text, low, high, value):
        self.draw_circular_dial()
        if self.last_needle_value is not None:
            self.draw_needle(self.last_needle_value, low, high, erase=True)
        self.draw_needle(value, low, high, erase=False)
        self.draw_gauge_numbers(label_values, label_text, low, high, value)

    def warn(self, x, y, text):
        
        WARN_FONT = ImageFont.truetype(self.SMALL_FONT_NAME, 12)
        self.draw.text((x, y), text, fill=(255, 255, 255), font=WARN_FONT)

    def refresh(self, last_needle_value):
        # if self.last_value is not None:
        #     self.draw_needle(self.last_value, 0, 10000, erase=True)
        # self.draw_needle(value, 0, 10000, erase=False)
        # self.draw_lower_value(str(value), self.STANDARD_FONT, (255, 255, 255))
        # self.draw_middle_value(str(value), self.MIDDLE_FONT, (255, 255, 255))
        # self.draw_gauge_numbers()
        self.disp.display(self.img)
        self.last_needle_value = last_needle_value
