import threading
from typing import Any, Callable, Generator, Self

from .hid_adapter.hid_adapter import HIDAdapter
from .hid_adapter.hid_detector import detect_hid_device


class Controller:
    gear: int
    wheel: float
    low_high_gear: bool
    angle: float
    config_angle: int
    pedal_gas: float
    pedal_clutch: float
    pedal_break: float
    pedal_vector: float
    buttons: dict[str, bool] = {}
    handbrake: bool
    turn_signal: int

    # TODO:
    dpad: None

    def __init__(self, config_angle: int) -> None:
        self.config_angle = config_angle

    @property
    def pedal_vector(self) -> float:
        return self.pedal_gas - self.pedal_break

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

    def pedal_from_raw(self, pedal: tuple[int, int]) -> float:
        _, base = pedal
        # TODO: Pedal is not precise
        return base / 255

    def buttons_from_raw(self, buttons: tuple[int, int, int]):
        # 00000000 0000____ _00_0000
        # TODO: DPAD
        self.handbrake = buttons[2] & 0b10000000
        self.buttons["start"] = buttons[2] & 0b00010000
        self.buttons["a"] = buttons[1] & 0b00000001
        self.buttons["b"] = buttons[1] & 0b00000010
        self.buttons["x"] = buttons[1] & 0b00000100
        self.buttons["y"] = buttons[1] & 0b00001000
        self.turn_signals = bool(buttons[1] & 0b00100000) - bool(
            buttons[1] & 0b00010000
        )

    def from_raw_hid_adapter_stream(self, stream: list[int]) -> None:
        """
        Unpacks fields from raw HID stream of the device
        """
        if len(stream) != 19:
            raise Exception(
                "Stream has invalid segments! Mostly, this is not correct data / device!"
            )

        # Stream is integer field that is actually bit under the hood
        # [_, wheel, wheel, _, _, gas, gas, _, _, _, _, break, break, clutch, clutch, ?, ?, ?, gearbox]

        # Raw fields (bits)
        _ = stream.pop(0)
        wheel_additional, wheel_base = stream.pop(0), stream.pop(0)
        _ = stream.pop(0)
        _ = stream.pop(0)
        pedal_gas = stream.pop(0), stream.pop(0)
        _ = stream.pop(0)
        _ = stream.pop(0)
        _ = stream.pop(0)
        _ = stream.pop(0)
        pedal_break = stream.pop(0), stream.pop(0)
        pedal_clutch = stream.pop(0), stream.pop(0)
        buttons = stream.pop(0), stream.pop(0), stream.pop(0)
        gearbox = stream.pop(0)

        # Parsing into DTO
        self.pedal_clutch = self.pedal_from_raw(pedal_clutch)
        self.pedal_break = self.pedal_from_raw(pedal_break)
        self.pedal_gas = self.pedal_from_raw(pedal_gas)

        self.buttons_from_raw(buttons)
        self.gear_from_raw_gearbox(gearbox, use_downshift=True)  # type: ignore
        self.wheel_from_raw(wheel_base, wheel_additional)  # type: ignore


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
                f"Wheel: {self.wheel} ({self.angle}°), gear: {self.gear} (divider: {self.low_high_gear}), gas: {self.pedal_gas:.1f}, clutch: {self.pedal_clutch:.1f}, break: {self.pedal_break:.1f}, handbrake: {self.handbrake}, turn signals: {self.turn_signals}, buttons: {self.buttons}"
            )

    def _callback_reader(
        self,
        callback: Callable[["Controller"], Any],
        adapter: HIDAdapter | None = None,
    ) -> None:
        for controller in self.read_blocking_generator(adapter=adapter):
            callback(controller)


class ControllerAdapterListener(ControllerAdapter): ...
