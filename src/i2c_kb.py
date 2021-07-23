
class i2c_kb:
  def __init__(self, i2c=None, sda=21, scl=22, interrupt=33):
    if i2c == None:
      from machine import I2C
      self.i2c = I2C(sda=sda, scl=scl)
    else:
      self.i2c = i2c
    self.addr = 0x08
    self.cb = None
    self.interrupt = interrupt

  def read(self):
    return self.i2c.readfrom(self.addr, 1)

  def _callback(self, pin):
    if pin == self.interrupt_pin:
      self.cb(self.read())

  def callback(self, cb):
    from machine import Pin
    self.interrupt_pin = Pin(self.interrupt, Pin.IN)
    self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._callback)
    self.cb = cb
