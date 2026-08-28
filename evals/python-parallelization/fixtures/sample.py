MAX_IN_FLIGHT = 8


def fetch_all(client, urls: list[str]) -> list[bytes]:
    """The project contract documents client.get as blocking and thread-safe."""
    return [client.get(url, timeout=5) for url in urls]
