from PIL import Image, ImageDraw, ImageFont
import st7735
import math

class Widget:
    def __init__(self):
        pass

    def draw(self, draw_obj):
        """Draw the widget onto the given PIL draw object."""
        raise NotImplementedError("Must implement draw()")
    
class TextWidget(Widget):
    def __init__(self, position, font, colour=(255, 255, 255)):
        self.position = position
        self.font = font
        self.colour = colour
        self.text = ""

    def draw(self, draw_obj):
        _, _, w, h = draw_obj.textbbox((0, 0), self.text, font=self.font)
        x, y = self.position
        draw_obj.rectangle((x - 5, y - 5, x + w + 5, y + h + 5), fill=(0, 0, 0))
        draw_obj.text((x, y), self.text, fill=self.colour, font=self.font)

class VirtualLED(Widget):
    def __init__(self, position, colour, radius):
        self.radius = radius
        self.colour = colour
        self.setPosition(position)

    def setColour(self, colour):
        self.colour = colour

    def setPosition(self, position):
        x, y = position
        self.x0 = x - self.radius
        self.x1 = x + self.radius
        self.y0 = y - self.radius
        self.y1 = y + self.radius

    def draw(self, draw_obj):
        draw_obj.ellipse((self.x0, self.y0, self.x1, self.y1), outline=None, fill=self.colour)

class CircularGauge(Widget):
    def __init__(self, center, radius_outer=60, radius_inner=40, low=0, high=100, label_values=None, label_text=None, color=(255, 0, 0)):
        self.center = center
        self.r_outer = radius_outer
        self.r_inner = radius_inner
        self.low = low
        self.high = high
        self.value = low
        self.needle_color = color
        self.label_values = label_values or []
        self.label_text = label_text or []

    def value_to_angle(self, value):
        ANGLE_START = 225
        ANGLE_END = -45
        normalized = (value - self.low) / (self.high - self.low)
        return ANGLE_START - (normalized * (ANGLE_START - ANGLE_END))

    def draw(self, draw_obj):
        x, y = self.center
        # Outer dial
        draw_obj.pieslice([(x - self.r_outer, y - self.r_outer), (x + self.r_outer, y + self.r_outer)],
                          start=135, end=405, fill=(200, 200, 200))
        # Inner dial
        draw_obj.ellipse([(x - self.r_inner, y - self.r_inner), (x + self.r_inner, y + self.r_inner)],
                         fill=(0, 0, 0))

        # Needle
        angle = self.value_to_angle(self.value)
        rad = math.radians(angle)
        start_x = x + self.r_inner * math.cos(rad)
        start_y = y - self.r_inner * math.sin(rad)
        end_x = x + self.r_outer * math.cos(rad)
        end_y = y - self.r_outer * math.sin(rad)
        draw_obj.line([(start_x, start_y), (end_x, end_y)], fill=self.needle_color, width=10)

        # Labels
        NUMBER_POS_RADIUS = 50
        for v, text in zip(self.label_values, self.label_text):
            angle = self.value_to_angle(v)
            rad = math.radians(angle)
            lx = x + NUMBER_POS_RADIUS * math.cos(rad)
            ly = y - NUMBER_POS_RADIUS * math.sin(rad)
            w, h = draw_obj.textbbox((0, 0), text)[2:]
            draw_obj.text((lx - w / 2, ly - h / 2), text, fill=(0, 0, 0))

class DisplayController:
    def __init__(self):
        # Display Configuration
        self.SPI_BUS = 0
        self.CS = 0
        self.DC = 24
        self.BACKLIGHT = 22
        self.RST = 25
        self.ROTATION = 270

        if self.ROTATION in (90, 270):
            self.WIDTH, self.HEIGHT = 160, 128
        else:
            self.WIDTH, self.HEIGHT = 160, 128 + 4

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

        if(self.ROTATION in (90, 270)):
            # Initialize Display
            self.disp = st7735.ST7735(
                port=self.SPI_BUS, cs=self.CS, dc=self.DC, backlight=self.BACKLIGHT, rst=self.RST,
                width=self.HEIGHT, height=self.WIDTH, rotation=self.ROTATION, invert=self.INVERT, bgr=self.BGR, offset_left=0, offset_top=0
            )
        else:
            self.disp = st7735.ST7735(
                port=self.SPI_BUS, cs=self.CS, dc=self.DC, backlight=self.BACKLIGHT, rst=self.RST,
                width=self.WIDTH, height=self.HEIGHT, rotation=self.ROTATION, invert=self.INVERT, bgr=self.BGR, offset_left=0, offset_top=0
            )
        
        self.CENTER = (self.WIDTH // 2, 65)
    
        self.img = Image.new("RGB", (self.WIDTH, self.HEIGHT), (0, 255, 0))  # Green fill
        
        self.draw = ImageDraw.Draw(self.img)
        self.last_needle_value = None  # Store last needle position

        self.widgets = []
        self.clear_display()

    def clear_display(self):
        """Fills the screen with the background color and refreshes it."""
        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), fill=self.BACKGROUND)
        #self.refresh(None)  # Update display
        self.refresh()
        
    def add_widget(self, widget):
        self.widgets.append(widget)

    def refresh(self):
        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), fill=(0, 0, 0))  # Clear screen
        for widget in self.widgets:
            widget.draw(self.draw)
        self.disp.display(self.img)