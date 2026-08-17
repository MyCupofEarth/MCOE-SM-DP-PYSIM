def toBytes(data):
    """
    Compatibility implementation of pyscard.util.toBytes.

    Accepts:
      - hex strings
      - bytes
      - bytearray
      - lists/tuples of integers
    """

    if data is None:
        return []

    if isinstance(data, bytes):
        return list(data)

    if isinstance(data, bytearray):
        return list(data)

    if isinstance(data, (list, tuple)):
        return list(data)

    if isinstance(data, str):
        value = data.replace(" ", "").replace(":", "").replace("-", "")

        if value.startswith("0x"):
            value = value[2:]

        if len(value) % 2:
            value = "0" + value

        return list(bytes.fromhex(value))

    raise TypeError(f"Unsupported data type: {type(data).__name__}")
