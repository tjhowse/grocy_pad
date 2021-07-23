
class i2c_kb:
  def _callback(self, pin):
    print("Button press")
    if pin == self.interrupt_pin:
      # self.cb(self.read())
      if self.cursor < self.buffer_size-1:
        self.buffer[self.cursor] = self.read()
        self.cursor += 1

  def __init__(self, i2c=None, sda=21, scl=22, interrupt=33):
    from machine import I2C, Pin
    if i2c == None:
      self.i2c = I2C(sda=sda, scl=scl)
    else:
      self.i2c = i2c
    self.addr = 0x08
    self.cb = None
    self.buffer_size = 100
    self.buffer = bytearray(self.buffer_size)
    self.cursor = 0
    self.interrupt_pin = Pin(interrupt, Pin.IN)
    self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._callback)
    print("KB initialised")

  def read(self):
    return self.i2c.readfrom(self.addr, 1)

  def clear_buffer(self):
    self.cursor = 0

  def get_buffer(self):
    return self.buffer[:self.cursor]

  def get_buffer_as_string(self):
    return ''.join(map(chr, self.get_buffer()))