import threading
from typing import Any, Callable, Generator, Self

from .hid_adapter.hid_adapter import HIDAdapter
from .hid_adapter.hid_detector import detect_hid_device


class Controller:
    gear: int
    wheel: float
    handbrake: bool
    low_high_gear: bool
    angle: float
    config_angle: int

    def __init__(self, config_angle: int) -> None:
        self.config_angle = config_angle

    def wheel_from_raw(self, base: int, additional: int):
        if base > 127:
            base = base - 128 - 127
        self.wheel = float(f"{base}.{additional}")
        self.angle = self.config_angle / 127 * self.wheel

    def gear_from_raw_gearbox(
        self,
        raw_gearbox_bitfield: int,
        use_downshift: bool = False,
    ) -> None:
        self.low_high_gear = bool(raw_gearbox_bitfield & 0b10000000)
        real_gear = 0
        if bool(raw_gearbox_bitfield & 0b01000000):
            real_gear = -1
        else:
            bit_base = 0b00000001
            for shift_bit in range(0, 7):
                if bool(raw_gearbox_bitfield & (bit_base << shift_bit)):
                    real_gear = shift_bit + 1

        self.gear = real_gear + ((use_downshift and self.low_high_gear) * 6)

    def from_raw_hid_adapter_stream(self, stream: list[int]) -> None:
        """
        Unpacks fields from raw HID stream of the device
        """
        self.gear_from_raw_gearbox(stream.pop(18), use_downshift=True)  # type: ignore
        self.wheel_from_raw(*[stream.pop(1), stream.pop(1)][::-1])  # type: ignore


class ControllerAdapter(Controller):
    def read_nonblocking(
        self,
        callback: Callable[["Controller"], Any],
        adapter: HIDAdapter | None = None,
    ) -> None:
        """
        Reads non-blocking with returning controller in callback, will start a thread (currently, unstoppable)
        """
        thread = threading.Thread(
            target=self._callback_reader, args=(self, callback, adapter), daemon=True
        )
        thread.start()

    def read_blocking_generator(
        self, adapter: HIDAdapter | None = None
    ) -> Generator[Self, Any, None]:
        if adapter is None:
            adapter = HIDAdapter(*detect_hid_device("ARDOR GAMING Silverstone"))

        for raw_stream in adapter.read_raw_stream():
            self.from_raw_hid_adapter_stream(raw_stream)
            yield self

    def read_blocking_display(self, adapter: HIDAdapter | None = None) -> None:
        for _ in self.read_blocking_generator(adapter=adapter):
            print(
                f"Wheel: {self.wheel} ({self.angle}°), gear: {self.gear} (divider: {self.low_high_gear})"
            )

    def _callback_reader(
        self,
        callback: Callable[["Controller"], Any],
        adapter: HIDAdapter | None = None,
    ) -> None:
        for controller in self.read_blocking_generator(adapter=adapter):
            callback(controller)


class ControllerAdapterListener(ControllerAdapter): ...
