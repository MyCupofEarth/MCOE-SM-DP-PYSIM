def toBytes(data):
    """
    Minimal replacement for smartcard.util.toBytes
    for pySim server-side usage.
    """
    if data is None:
        return []

    if isinstance(data, bytes):
        return list(data)

    if isinstance(data, bytearray):
        return list(data)

    if isinstance(data, list):
        return data

    if isinstance(data, str):
        data = data.replace(" ", "").replace(":", "")

        if len(data) % 2:
            raise ValueError("Hex string must contain an even number of characters")

        return list(bytes.fromhex(data))

    raise TypeError(f"Unsupported data type: {type(data).__name__}")
