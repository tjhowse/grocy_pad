
class i2c_kb:
  def _callback(self, pin):
    # import machine
    # state = machine.disable_irq()
    if pin == self.interrupt_pin:
      if self.cursor < self.buffer_size-1:
        self.new = True
        while True:
          char = self.i2c.read_u8(1)
          if char == 0:
            break
          if char == 8 and self.cursor > 0:
            # Backspace.
            self.cursor -= 1
          else:
            self.buffer[self.cursor] = char
            self.cursor += 1
    # machine.enable_irq(state)

  def __init__(self, i2c=None, sda=21, scl=22, interrupt=33):
    from machine import Pin
    import i2c_bus
    if i2c == None:
      self.i2c = i2c_bus.easyI2C((sda, scl), 0x08, freq=400000)
    else:
      self.i2c = i2c
    # Flush the i2c buffer.
    while self.i2c.read_u8(1):
      pass
    self.buffer_size = 100
    self.buffer = bytearray(self.buffer_size)
    self.cursor = 0
    self.new = False
    if interrupt is not None:
      self.interrupt_pin = Pin(interrupt, Pin.IN)
      # Don't be tempted to change this to IRQ_RISING. I tried it, it doesn't work.
      self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._callback)
    else:
      from machine import Timer
      # tim = Timer(1, mode=Timer.PERIODIC, width=32)
      # tim_a = tim.channel(Timer.A | Timer.B, freq=10)
      # tim_a.irq(handler=self.poll, trigger=Timer.TIMEOUT)

  def poll(self):
    # Call this regularly if you want to use this with the interrupts disabled.
    while True:
      char = self.i2c.read_u8(1)
      if char == 0:
        break
      self.new = True
      if char == 8 and self.cursor > 0:
        # Backspace.
        self.cursor -= 1
      else:
        self.buffer[self.cursor] = char
        self.cursor += 1
      self.new = True

  def read_i2c_raw(self, size):
    return self.i2c.read_u8(size)

  def clear_buffer(self):
    self.cursor = 0

  def get_buffer(self):
    self.new = False
    return self.buffer[:self.cursor]

  def get_buffer_as_string(self):
    return ''.join(map(chr, self.get_buffer()))