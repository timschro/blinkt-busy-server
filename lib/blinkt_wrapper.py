#!/usr/bin/env python
import contextlib
import io
import colorsys
import spidev
import blinkt

class BlinktWrapper:
    def __init__(self, hat = None):
      
        self.brightness = 0.5
        self.rotation = 0

    def getType(self):
        return self.type


    def clear(self):
        return self.clear()

  
    def setAll(self, r, g, b):
        self.set_all(r, g, b)

    def getBrightness(self):
        return self.brightness
    
    def setBrightness(self, brightness):
        self.brightness = brightness
        self.set_brightness(brightness)
    
    def setPixel(self, x, r, g, b):
        self.set_pixel(x, r, g, b)
    
    def setColour(self, r = None, g = None, b = None, RGB = None):
        if RGB is not None:
            r = RGB[0]
            g = RGB[1]
            b = RGB[2] 
        self.clear()
        for x in range(7):
             self.setPixel(x, y, r, g, b)
        self.hat.show()
    
    
    def show(self):
        self.show()

    def off(self):
        self.clear()
        self.show()
    
    # Colour converstion operations as we only understand RGB
    def hsvIntToRGB(self, h, s, v):
        h = h / 360
        s = s /100
        v = v / 100
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))
    
    def htmlToRGB(self, html):
        if len(html) is 6:
            r = int(f"{html[0]}{html[1]}", 16)
            g = int(f"{html[2]}{html[3]}", 16)
            b = int(f"{html[4]}{html[5]}", 16)
        elif len(html) > 6:
            r = int(f"{html[1]}{html[2]}", 16)
            g = int(f"{html[3]}{html[4]}", 16)
            b = int(f"{html[5]}{html[6]}", 16)
        else:
            raise Exception("The Hex value is not in the correct format it should RRGGBB or #RRGGBB the same as HTML")
        return tuple(r,g,b)
