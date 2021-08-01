# Re-learning how micropython be

I bit the bullet and installed M5Stack's M5Burner. I don't like it because it's closed source and
installs closed-source firmware binaries.
from: http://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/software/M5Burner.zip
https://github.com/m5stack/M5Stack-Firmware

```python
pip3 install --user adafruit-ampy

ampy --port /dev/ttyS3 ls
```
Repl: `screen /dev/ttyS3 115200`

Problem getting REPL: For some reason screen wouldn't connect sometimes. I had to run an ampy ls
and then it started working again. I assume it sets some parameters on the com port. After a fresh
flash it seems to reboot a few times? Or something?

I can't trust this firmware, so I'll block the device's MAC in my router.

# M5Stack has lots of custom reimplementations -.-

https://docs.m5stack.com/en/mpy/display/m5stack_lvgl

# Keyboard

https://github.com/m5stack/m5-docs/blob/master/docs/en/core/face_kit.md

```python
import i2c_bus
sda = 21
scl = 22
i2c0 = i2c_bus.easyI2C((sda, scl), 0x68, freq=400000)
if i2c0.available():
    i2c0.scan()
>>> [8, 52, 56, 81]
```
Git tag: 1

# Python examples galore

https://github.com/m5stack/M5Cloud/tree/master/examples

# write.py

I wrote this to avoid flashing stuff to the ESP unless it changed.

# Core 2 pin changes

The qwerty face module fires pin 5 interrupt when a button is pressed, but the core2 module
has pin 5 on the header connected to pin 33, so the example projects don't work.

# i2c weirdness

Using `from machine import i2c` and setting up an i2c bus on a couple of pins doesn't seem to work
reliably. There's some persistent state lingering that means that approach only works if the hardware
was already set up using `import i2c_bus\ni2c_bus.easyI2C()`, for some reason.

Sometimes it just stops responding. I thought it might be a bug in the callback and the exception
disappears. But no?

# Precompiled modules

I think it might be best to handle the keyboard in a C module: https://docs.micropython.org/en/latest/develop/natmod.html#natmod
I'm having troubles getting the ISR for a keypress small enough to be useful.
Maybe based on: https://github.com/m5stack/M5Stack/blob/master/examples/Face/KEYBOARD/KEYBOARD.ino

# GUI Design kinda

https://flow.m5stack.com/
This website lets you assemble a gui out of some of the available components and view the result as python. For some reason
there are more visual elements available in the code than in the drag-and-drop interface though. There's a desktop version
available too, but it's got no more elements available.

# LVGL

It looks like the m5stack gui stuff is built on something called lvgl: https://gist.github.com/amirgon/e4e09fc528923e417bcb318fb61b1f6c
AKA LittlevGL? https://docs.lvgl.io/latest/en/html/widgets/img.html

# Element of an M5List:

```python
#a = product_list.add_label("Egg")
a = displayed["Egg"] # Git: 4d1d64f03f07ec855b2335dbdfaf55959fbbe66b
a.set_style_local_bg_color(255,255,255) # Error
b = a.get_style_bg_color(0)
>>> type(b)
<class 'lv_color16_t'>
a.set_style_local_bg_color(0, 0, b)
```
https://docs.lvgl.io/latest/en/html/overview/style.html?highlight=get_style_bg_color

:O an lvgl simulator:
https://docs.lvgl.io/latest/en/html/get-started/micropython.html

From that page:
```python
import lvgl as lv
lv.init()
scr = lv.obj()
btn = lv.btn(scr)
btn.align(lv.scr_act(), lv.ALIGN.CENTER, 0, 0)
label = lv.label(btn)
label.set_text("Button")
lv.scr_load(scr)
```

Let's try:
```python
import lvgl
c = lvgl.color_make(255,255,255)
a.set_style_local_bg_color(0, 0, c) # Egg, from above
# Fuck yeah!
```

# RGB Bars

The m5stack faces base has two strips of 5 ws2812 LEDs down the side. I started playing with them. The m5 stuff gives you
the `rgb` object, but it's hardcoded to use pin 25, for some reason. The base docs say the LEDs are on pin 15, but if you
transpose the pin maps from the core to the core2 layout it becomes pin 2.

https://docs.m5stack.com/en/core/basic?id=pinmap
https://docs.m5stack.com/en/core/core2?id=pinmap

```python
from neopixel import NeoPixel
import machine
from m5stack import rgb
rgb.np
# Neopixel(Pin=25, Pixels: 10, bit/pix=24, RMTChannel=7, PixBufLen=40, Color order: 'GRB'
#          Timings (ns): T1H=600, T1L=700, T0H=350, T0L=800, Treset=80000
# )
# Note different capitalisation. It looks like the m5stack version of the neopixel library is different?
np = NeoPixel(machine.Pin(2),10)
def all(colour):
    for i in range(10):
        np[i] = colour
    np.write()
```