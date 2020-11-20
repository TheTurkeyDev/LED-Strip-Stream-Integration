import asyncio
import threading
import time

from rpi_ws281x import *
from flask import Flask

from twtich_web_socket import WebSocketClient
from web_blueprint import api
import data
from display_type import DisplayType

LED_COUNT = 240  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 127  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

app = Flask(__name__)
app.register_blueprint(api)


def color_from_tuple(color):
    # This check is just to prevent too much power from being drawn
    power = ((color[0] + color[1] + color[2]) / 255.0) * 0.2
    sub = 0
    if power > 0.5:
        sub = int(((power - 0.5) / 0.1) * 20)
    return Color(color[0] - sub, color[1] - sub, color[2] - sub)


def idle(strip, tick):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.setPixelColor(tick % strip.numPixels(), Color(255, 255, 255))
    strip.show()


def block_color(strip, tick, colors):
    num_colors = len(colors)
    if num_colors == 0:
        return
    block_size = int(strip.numPixels() / num_colors)
    j = tick % strip.numPixels()
    for i in range(strip.numPixels()):
        strip.setPixelColor((i + j) % strip.numPixels(), color_from_tuple(colors[int(i / block_size) % num_colors]))
    strip.show()


def alternate_color(strip, tick, colors):
    num_colors = len(colors)
    if num_colors == 0:
        return
    j = tick % num_colors
    for i in range(strip.numPixels()):
        strip.setPixelColor((i + j) % strip.numPixels(), color_from_tuple(colors[i % num_colors]))
    strip.show()


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


# rainbow code referenced from https://tutorials-raspberrypi.com/connect-control-raspberry-pi-ws2812-rgb-led-strips/
def rainbow(strip, tick):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    j = tick % 256
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
    strip.show()


def police(strip, tick):
    for i in range(strip.numPixels()):
        if tick % 2 == 0 and 0 < i <= 62:
            strip.setPixelColor(i, Color(255, 0, 0))
        elif tick % 2 == 1 and 178 < i <= 240:
            strip.setPixelColor(i, Color(0, 0, 255))
        else:
            strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()


def setup_led_strip():
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    tick = 0
    wait_ms = 20
    while True:
        if data.display == DisplayType.IDLE:
            wait_ms = 20
            idle(strip, tick)
        elif data.display == DisplayType.SOLID or data.display == DisplayType.BLOCK_COLOR:
            wait_ms = 20
            block_color(strip, tick, data.colors)
        elif data.display == DisplayType.RAINBOW:
            wait_ms = 20
            rainbow(strip, tick)
        elif data.display == DisplayType.ALTERNATE_COLOR:
            wait_ms = 100
            alternate_color(strip, tick, data.colors)
        elif data.display == DisplayType.POLICE:
            wait_ms = 500
            police(strip, tick)

        tick += 1
        time.sleep(wait_ms / 1000.0)


async def setup_twitch_connection():
    client = WebSocketClient()
    connection = await client.connect()
    await client.receive_message(connection)


def setup_flask():
    app.run(host='0.0.0.0', debug=True, use_reloader=False)


if __name__ == '__main__':
    led_strip_thread = threading.Thread(target=setup_led_strip)
    led_strip_thread.start()
    flask_thread = threading.Thread(target=setup_flask)
    flask_thread.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(loop.create_task(setup_twitch_connection()))
