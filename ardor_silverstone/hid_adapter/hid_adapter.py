from typing import Any, Generator, NoReturn

import hid


class HIDAdapter:
    def __init__(self, vendor_id: int, product_id: int) -> None:
        self.vendor_id = vendor_id
        self.product_id = product_id
        self._open_device()

    def read_raw_stream(self) -> Generator[list[int], Any, NoReturn]:
        while True:
            raw_report: list[int] = list(self.device.read(32))  # type: ignore
            if not raw_report:
                continue
            yield raw_report

    def _open_device(self) -> None:
        self.device = hid.device()  # type: ignore
        self.device.open(self.vendor_id, self.product_id)  # type: ignore
        self.device.set_nonblocking(True)  # type: ignore

    # for n in r:
    #    print(format(n, "08b"), end=" ")
