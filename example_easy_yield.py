from ardor_silverstone.controller import ControllerAdapter

controller = ControllerAdapter(900)
for _ in controller.read_blocking_generator():
    ...
