from ardor_silverstone.controller import ControllerAdapter

controller = ControllerAdapter(900)

controller.read_nonblocking(callback=lambda _: print("callback"))
