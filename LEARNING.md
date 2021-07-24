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