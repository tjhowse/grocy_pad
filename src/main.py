from m5stack_ui import *
screen = M5Screen()
screen.clean_screen()
Textarea = M5Textarea()

# Textarea.set_text("Hello World")

import i2c_bus

# i2c0 = i2c_bus.easyI2C(i2c_bus.PORTA, addr, freq=400000)
sda = 21
scl = 22
i2c0 = i2c_bus.easyI2C((sda, scl), 0x68, freq=400000)

# True or False
if i2c0.available():
    Textarea.set_text(i2c0.scan())