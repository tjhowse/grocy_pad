
class i2c_kb:
  def _callback(self, pin):
    if pin == self.interrupt_pin:
      if self.cursor < self.buffer_size-1:
        self.buffer[self.cursor] = self.i2c.read_u8(1)
        self.cursor += 1

  def __init__(self, i2c=None, sda=21, scl=22, interrupt=33):
    from machine import Pin
    import i2c_bus
    if i2c == None:
      self.i2c = i2c_bus.easyI2C((sda, scl), 0x08, freq=400000)
    else:
      self.i2c = i2c
    self.buffer_size = 100
    self.buffer = bytearray(self.buffer_size)
    self.cursor = 0
    self.interrupt_pin = Pin(interrupt, Pin.IN)
    self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._callback)

  def clear_buffer(self):
    self.cursor = 0

  def get_buffer(self):
    return self.buffer[:self.cursor]

  def get_buffer_as_string(self):
    return ''.join(map(chr, self.get_buffer())).decode('utf-8')