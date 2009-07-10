"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
# Import helpers as desired, or define your own, ie:
# from webhelpers.html.tags import checkbox, password

from pyamf.remoting.gateway.wsgi import WSGIGateway
from pdk.util.imageutils import rgbToHex, hexToRgb

def hexToFlexColor(color):
    return eval(rgbToHex(*hexToRgb(color), **{'prefix':'0x'}))
