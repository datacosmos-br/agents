IPV4_MAX_OCTET = 255


def is_ipv4_octet(value: int) -> bool:
    return 0 <= value <= IPV4_MAX_OCTET
