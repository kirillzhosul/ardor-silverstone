import hid  # type: ignore


def try_detect_hid_device(device_name: str) -> tuple[int, int] | None:
    """
    Tries to detect and return device with given name
    """

    unique_devices: set[int] = set()
    for device in hid.enumerate():  # type: ignore
        product_id = int(device["product_id"])  # type: ignore
        vendor_id = int(device["vendor_id"])  # type: ignore
        product_string = str(device["product_string"])  # type: ignore

        if product_id in unique_devices:
            continue
        unique_devices.add(product_id)

        if product_string == device_name:
            return (vendor_id, product_id)
    return None


def detect_hid_device(device_name: str) -> tuple[int, int]:
    """
    Detects and return device with given name
    """

    device = try_detect_hid_device(device_name)
    if not device:
        exit(1)
    return device
