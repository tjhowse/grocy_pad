# Re-learning how micropython be

I bit the bullet and installed M5Stack's M5Burner. I don't like it because it's closed source and
installs closed-source firmware binaries.
from: http://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/software/M5Burner.zip
https://github.com/m5stack/M5Stack-Firmware

```python
pip3 install --user adafruit-ampy

ampy --port /dev/ttyS3 ls
```
Repl: screen /dev/ttyS3 115200

I can't trust this firmware, so I'll block the device's MAC in my router.
