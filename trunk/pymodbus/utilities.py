'''
Extra utilites that do not neccessarily require a class
'''

def packBitsToString(bits):
    '''
    Creates a string out of an array of bits
    @param bits A bit array

    example:
            bits = [False, True, False, ...]
    '''
    ret = ''
    i = packed = 0
    for bit in bits:
        if bit: packed += 128
        i += 1
        if i == 8:
            ret += chr(packed)
            i = packed = 0
        else: packed >>= 1
    if i > 0 and i < 8:
        packed >>= 7-i
        ret += chr(packed)
    return ret

def unpackBitsFromString(string):
    '''
    Creates bit array out of a string
    @param string The modbus data packet to decode

    example:
            string[0]   = bytes to follow
            string[1-N] = bytes to decode
    '''
    byte_count = ord(string[0])
    bits = []
    for byte in range(1, byte_count+1):
        value = ord(string[byte])
        for bit in range(8):
            bits.append((value & 1) == 1)
            value >>= 1
    return bits, byte_count

#---------------------------------------------------------------------------#
# Error Detection Functions
#---------------------------------------------------------------------------#
def __generate_crc16_table():
    result = []
    for byte in range(256):
        crc = 0x0000
        for bit in range(8):
            if (byte ^ crc) & 0x0001: crc = (crc >> 1) ^ 0xa001
            else: crc >>= 1
            byte >>= 1
        result.append(crc)
    return result

__crc16_table = __generate_crc16_table()

def computeCRC(data):
    '''
    Computes a crc16 on the passed in data. The difference between modbus's
    crc16 and a normal crc16 is that modbus starts the crc value out at
    0xffff.
    @param data The data to create a crc16 of

    Accepts a string or a integer list
    '''
    crc = 0xffff
    pre = lambda x: x
    if isinstance(data, str): pre = lambda x: ord(x)

    for a in data: crc = ((crc >> 8) & 0xff) ^ __crc16_table[
            (crc ^ pre(a)) & 0xff];
    return crc

def checkCRC(data, check):
    '''
    Checks if the data matches the passed in CRC
    @param data The data to create a crc16 of
    @param check The CRC to validate
    '''
    return computeCRC(data) == check

def computeLRC(data):
    '''
    Wrapper to computer LRC of multiple types of data
    @param data The data to apply a lrc to

    Accepts a string or a integer list
    '''
    lrc = 0
    pre = lambda x: x
    if isinstance(data, str): pre = lambda x: ord(x)

    for a in data: lrc = lrc ^ pre(a);
    return lrc

def checkLRC(data, check):
    '''
    Checks if the passed in data matches the LRC
    @param data The data to calculate
    @param check The LRC to validate
    '''
    return computeLRC(data) == check

__all__ = [
        'packBitsToString', 'unpackBitsFromString', 'computeCRC',
        'checkCRC', 'computeLRC', 'checkLRC'
]
