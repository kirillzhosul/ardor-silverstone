### Simple _adapter_ for **Ardor Silverstone** racing wheel

#### Notice and warning!
This project is done for fun, and for now I not have access to this wheel, 
so use this project as some guideline and please contribute with code that needed for you (Or contact me for help)

---

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
