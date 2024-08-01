'''
Test the Prefix.__contains__() method
>>> '10.20.0.1' in Prefix('10.20.0.0/23')
False
>>> '10.20.1.0' in Prefix('10.20.0.0/23')
False
>>> '10.20.1.255' in Prefix('10.20.0.0/23')
False
>>> '10.20.2.0' in Prefix('10.20.0.0/23')
False
>>> '10.20.0.1' in Prefix('10.20.0.0/24')
False
>>> '10.20.0.255' in Prefix('10.20.0.0/24')
False
>>> '10.20.1.0' in Prefix('10.20.0.0/24')
False
>>> '10.20.0.1' in Prefix('10.20.0.0/25')
False
>>> '10.20.0.127' in Prefix('10.20.0.0/25')
False
>>> '10.20.0.128' in Prefix('10.20.0.0/25')
False
>>> '10.20.0.1' in Prefix('10.20.0.0/26')
False
>>> '10.20.0.63' in Prefix('10.20.0.0/26')
False
>>> '10.20.0.64' in Prefix('10.20.0.0/26')
False
>>> '10.20.0.1' in Prefix('10.20.0.0/27')
False
>>> '10.20.0.31' in Prefix('10.20.0.0/27')
False
>>> '10.20.0.32' in Prefix('10.20.0.0/27')
False
'''

import binascii
import socket

int_type_int = type(0xff)
int_type_long = type(0xffffffffffffffff)


def ip_int_to_str(address: int, family: int) -> str:
    '''Convert an integer value to an IP address string, in presentation
    format.

    address: int, integer value of an IP address (IPv4 or IPv6)
    family: int, either socket.AF_INET (IPv4) or socket.AF_INET6 (IPv6)

    Examples:
    >>> ip_int_to_str(0xc0000201, socket.AF_INET)
    '192.0.2.1'
    >>> ip_int_to_str(0x20010db8000000000000000000000001, socket.AF_INET6)
    '2001:db8::1'
    '''

    if family == socket.AF_INET6:
        address_len = 128
    else:
        address_len = 32
    return socket.inet_ntop(family,
            binascii.unhexlify(('%x' % address).zfill(address_len >> 2)))

def ip_str_to_int(address: str) -> int:
    '''Convert an IP address string, in presentation format, to an integer.
    address:

    str, string representation of an IP address (IPv4 or IPv6)

    Examples:
    >>> hex(ip_str_to_int('192.0.2.1'))
    '0xc0000201'
    >>> hex(ip_str_to_int('2001:db8::1'))
    '0x20010db8000000000000000000000001'
    '''

    if ':' in address:
        family = socket.AF_INET6
    else:
        family = socket.AF_INET
    return int_type_long(
            binascii.hexlify(socket.inet_pton(family, address)), 16)

def all_ones(n: int) -> int:
    '''Return an int that is value the equivalent of having only the least
    significant n bits set.  Any bits more significant are not set.  This is a
    helper function for other IP address manipulation functions.

    n: int, the number of least significant bits that should be set

    Examples:
    >>> hex(all_ones(4))
    '0xf'
    >>> bin(all_ones(4))
    '0b1111'
    >>> hex(all_ones(8))
    '0xff'
    >>> bin(all_ones(8))
    '0b11111111'
    >>> hex(all_ones(16))
    '0xffff'
    >>> bin(all_ones(16))
    '0b1111111111111111'
    '''

    return 2**n - 1

def ip_prefix_mask(family: int, prefix_len: int) -> int:
    '''Return prefix mask for the given address family and prefix length, as an
    int.  The prefix_len most-significant bits should be set, and the remaining
    (least significant) bits should not be set.  The total number of bits in
    the value returned should be dictated by the address family: 32 bits for
    socket.AF_INET (IPv4); 128 bits for socket.AF_INET6 (IPv6).

    family: int, either socket.AF_INET (IPv4) or socket.AF_INET6 (IPv6)
    prefix_len: int, the number of bits corresponding to the length of the
        prefix

    Examples:
    >>> hex(ip_prefix_mask(socket.AF_INET, 24))
    '0xffffff00'
    >>> bin(ip_prefix_mask(socket.AF_INET, 24))
    '0b11111111111111111111111100000000'
    >>> hex(ip_prefix_mask(socket.AF_INET, 27))
    '0xffffffe0'
    >>> bin(ip_prefix_mask(socket.AF_INET, 27))
    '0b11111111111111111111111111100000'
    >>> hex(ip_prefix_mask(socket.AF_INET6, 50))
    '0xffffffffffffc0000000000000000000'
    >>> bin(ip_prefix_mask(socket.AF_INET6, 50))
    '0b11111111111111111111111111111111111111111111111111000000000000000000000000000000000000000000000000000000000000000000000000000000'
    >>> hex(ip_prefix_mask(socket.AF_INET6, 64))
    '0xffffffffffffffff0000000000000000'
    >>> bin(ip_prefix_mask(socket.AF_INET6, 64))
    '0b11111111111111111111111111111111111111111111111111111111111111110000000000000000000000000000000000000000000000000000000000000000'
    '''

    #FIXME
    return 0

def ip_prefix(address: int, family: int, prefix_len: int) -> int:
    '''Return the prefix for the given IP address, address family, and
    prefix length, as an int.  The prefix_len most-significant bits
    from the IP address should be preserved in the prefix, and the
    remaining (least significant) bits should not be set.  The total
    number of bits in the prefix should be dictated by the address
    family: 32 bits for socket.AF_INET (IPv4); 128 bits for
    socket.AF_INET6 (IPv6).

    address: int, integer value of an IP address (IPv4 or IPv6)
    family: int, either socket.AF_INET (IPv4) or socket.AF_INET6 (IPv6)
    prefix_len: int, the number of bits corresponding to the length of the
        prefix

    Examples:
    >>> hex(ip_prefix(0xc00002ff, socket.AF_INET, 16))
    '0xc0000000'
    >>> hex(ip_prefix(0xc00002ff, socket.AF_INET, 24))
    '0xc0000200'
    >>> hex(ip_prefix(0xc00002ff, socket.AF_INET, 27))
    '0xc00002e0'
    >>> hex(ip_prefix(0x20010db80000ffffffffffffffffffff, socket.AF_INET6, 48))
    '0x20010db8000000000000000000000000'
    >>> hex(ip_prefix(0x20010db80000ffffffffffffffffffff, socket.AF_INET6, 50))
    '0x20010db80000c0000000000000000000'
    >>> hex(ip_prefix(0x20010db80000ffffffffffffffffffff, socket.AF_INET6, 64))
    '0x20010db80000ffff0000000000000000'
    '''

    #FIXME
    return 0

def ip_prefix_total_addresses(family: int, prefix_len: int) -> int:
    '''Return the total number IP addresses (_including_ the first and
    last addresses within an IPv4 subnet, which cannot be used by a host
    or router on that subnet) for the given address family and prefix
    length.  The address family should be used to derive the address
    length: 32 bits for socket.AF_INET (IPv4); 128 bits for
    socket.AF_INET6 (IPv6).

    family: int, either socket.AF_INET (IPv4) or socket.AF_INET6 (IPv6)
    prefix_len: int, the number of bits corresponding to the length of the
        prefix

    Examples:
    >>> ip_prefix_total_addresses(socket.AF_INET, 24)
    256
    >>> ip_prefix_total_addresses(socket.AF_INET, 27)
    32
    >>> ip_prefix_total_addresses(socket.AF_INET6, 120)
    256
    '''

    #FIXME
    return 0

def ip_prefix_nth_address(prefix: int, family: int,
        prefix_len: int, n: int) -> int:
    '''Return the nth IP address within the prefix specified with the given
    prefix, address family, and prefix length, as an int.  The prefix_len
    most-significant bits from the from the prefix should be preserved in the
    prefix, and the remaining (least significant) bits are incremented by n to
    yield an IP address within the prefix. The total number of bits in the
    prefix should be dictated by the address family: 32 bits for socket.AF_INET
    (IPv4); 128 bits for socket.AF_INET6 (IPv6).

    prefix: int, integer value of an IP prefix (IPv4 or IPv6)
    family: int, either socket.AF_INET (IPv4) or socket.AF_INET6 (IPv6)
    prefix_len: int, the number of bits corresponding to the length of the
        prefix
    n: int, the offset of the IP address within the prefix

    Examples:
    >>> hex(ip_prefix_nth_address(0xc0000200, socket.AF_INET, 24, 0))
    '0xc0000200'
    >>> hex(ip_prefix_nth_address(0xc0000200, socket.AF_INET, 24, 10))
    '0xc000020a'
    >>> hex(ip_prefix_nth_address(0xc0000200, socket.AF_INET, 24, 255))
    '0xc00002ff'
    >>> hex(ip_prefix_nth_address(0x20010db80000ffff0000000000000000, socket.AF_INET6, 64, 0))
    '0x20010db80000ffff0000000000000000'
    >>> hex(ip_prefix_nth_address(0x20010db80000ffff0000000000000000, socket.AF_INET6, 64, 0xa))
    '0x20010db80000ffff000000000000000a'
    >>> hex(ip_prefix_nth_address(0x20010db80000ffff0000000000000000, socket.AF_INET6, 64, 0xff))
    '0x20010db80000ffff00000000000000ff'
    '''

    #FIXME
    return 0

def ip_prefix_last_address(prefix: int, family: int, prefix_len: int) -> int:
    '''Return the last IP address within the prefix specified with the given
    prefix, address family, and prefix length, as an int.  The prefix_len
    most-significant bits from the from the prefix should be preserved in the
    prefix, and the remaining (least significant) bits should all be set. The
    total number of bits in the prefix should be dictated by the address
    family: 32 bits for socket.AF_INET (IPv4); 128 bits for socket.AF_INET6
    (IPv6).

    prefix: int, integer value of an IP prefix (IPv4 or IPv6)
    family: int, either socket.AF_INET (IPv4) or socket.AF_INET6 (IPv6)
    prefix_len: int, the number of bits corresponding to the length of the
        prefix
    n: int, the offset of the IP address within the prefix

    Examples:
    >>> hex(ip_prefix_last_address(0xc0000000, socket.AF_INET, 16))
    '0xc000ffff'
    >>> hex(ip_prefix_last_address(0xc0000200, socket.AF_INET, 24))
    '0xc00002ff'
    >>> hex(ip_prefix_last_address(0xc0000200, socket.AF_INET, 27))
    '0xc000021f'
    >>> hex(ip_prefix_last_address(0x20010db8000000000000000000000000, socket.AF_INET6, 48))
    '0x20010db80000ffffffffffffffffffff'
    >>> hex(ip_prefix_last_address(0x20010db8000000000000000000000000, socket.AF_INET6, 50))
    '0x20010db800003fffffffffffffffffff'
    >>> hex(ip_prefix_last_address(0x20010db8000000000000000000000000, socket.AF_INET6, 64))
    '0x20010db800000000ffffffffffffffff'
    '''

    #FIXME
    return 0


class Prefix:
    '''A class consisting of a prefix (int), a prefix length (int), and an
    address family (int).
    '''

    def __init__(self, prefix: str):
        if ':' in prefix:
            family = socket.AF_INET6
        else:
            family = socket.AF_INET

        # divide the prefix and the prefix length
        prefix_str, prefix_len_str = prefix.split('/')
        prefix_len = int(prefix_len_str)

        # make sure prefix is a true prefix
        prefix_int = ip_str_to_int(prefix_str)
        prefix_int = ip_prefix(prefix_int, family, prefix_len)

        self.prefix = prefix_int
        self.prefix_len = prefix_len
        self.family = family

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return '%s/%d' % \
                (ip_int_to_str(self.prefix, self.family), self.prefix_len)

    def __contains__(self, address: str) -> bool:
        '''Return True if the address corresponding to this IP address is
        within this prefix, False otherwise.

        address: str, 'x.x.x.x' or 'x:x::x'
        '''

        if ':' in address:
            family = socket.AF_INET6
        else:
            family = socket.AF_INET
        if family != self.family:
            raise ValueError('Address can only be tested against prefix of ' + \
                    'the same address family.')

        address = ip_str_to_int(address)

        #FIXME
        return False

    def __hash__(self):
        return hash((self.prefix, self.prefix_len))

    def __eq__(self, other):
        return self.prefix == other.prefix and \
                self.prefix_len == other.prefix_len
