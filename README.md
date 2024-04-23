### Simple _adapter_ for **Ardor Silverstone** racing wheel

Provides simple abstraction layer on top of hid / controller buttons for making some callbacks / simple applications

```python
from ardor_silverstone.controller import ControllerAdapter

controller = ControllerAdapter(900) # 900 -> wheel steering angle

# Will block running loop, and display information like gear / wheel
controller.read_blocking_display()

# Generator for working with events in loop
for _ in controller.read_blocking_generator():
    ...

# Will launch a thread, so be careful!
controller.read_nonblocking(callback=lambda _: print("callback"))
```
