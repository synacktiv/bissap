ALG_LZC: int
ALG_LZH: int

class CompressError(Exception):
    pass

class DecompressError(Exception):
    pass

def compress(
    buf: bytes,
    algorithm: int,
) -> tuple[int, int, bytes]:
    """
    Compress a buffer using SAP's compression algorithms.

    :param str buf: input buffer to compress
    :param int algorithm: algorithm to use
    :return: tuple with return code, output length and output buffer
    :rtype: tuple of int, int, string
    :raises CompressError: if an error occurred during compression
    """

def decompress(buf: bytes) -> tuple[int, bytes | None]:
    """
    Decompress a buffer using SAP's compression algorithms.

    :param bytes buf: input buffer to decompress
    :return: tuple of return code and output buffer
    :rtype: tuple of int, Optional[bytes]
    :raises DecompressError: if an error occurred during decompression
    """
    ...
