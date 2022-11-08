"""
TODO: SACP protocol is not well implemented, refactor this.
"""
import struct

INT8 = 'B'
INT16 = 'H'
INT32 = 'I'
SACP_VERSION = 0x01
SACP_PACK_FORMAT = '<{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}'.format(INT8, INT8, INT16, INT8, INT8, INT8,
                                                                INT8, INT8, INT16, INT8, INT8)
SACP_PACKAGE = 60 * 1024  # 60 KiB


def SACP_check_head(package_data, length):
    crc = 0
    poly = 0x07
    for i in range(length):
        for j in range(8):
            bit = ((package_data[i] & 0xff) >> (7 - j) & 0x01) == 1
            c07 = (crc >> 7 & 0x01) == 1
            crc = crc << 1
            if c07 ^ bit:
                crc ^= poly
    crc = crc & 0xff
    return crc


def u16_check_data(package_data, length):
    check_num = 0
    if length > 0:
        for i in range(0, (length - 1), 2):
            check_num += (((package_data[i] & 0xff) << 8) | (package_data[i + 1] & 0xff))
            check_num &= 0xffffffff
        if length % 2 != 0:
            check_num += package_data[length - 1]
    while check_num > 0xffff:
        check_num = ((check_num >> 16) & 0xffff) + (check_num & 0xffff)
    check_num = ~check_num
    return check_num & 0xffff


class ReceiverException(Exception):
    def __init__(self, error_info):
        self.error_info = error_info


class ReceiverData(object):
    def __init__(self, command_set, command_id, valid_data, sequence):
        self.command_set = command_set
        self.command_id = command_id
        self.valid_data = valid_data
        self.sequence = sequence


def SACP_pack(receiver_id, sender_id, attribute, sequence, command_set, command_id, send_data):
    """
        receiver_id : 接收者ID
        sender_id : 发送者ID
        attribute: 0 - 请求, 1 - 应答
        sequence : 包的标号
        command_set : command_set
        command_id : command_id
        data : 要发送的数据
    """
    data_length = len(send_data)
    package_head = struct.pack(SACP_PACK_FORMAT,
                               0xAA,
                               0x55,
                               data_length + 6 + 2,
                               SACP_VERSION,
                               receiver_id,
                               0,  # 前6个字节的校验,暂时为0
                               sender_id,
                               attribute,
                               sequence,
                               command_set,
                               command_id)
    package_head = bytearray(package_head)
    package_head[6] = SACP_check_head(package_head, 6)
    pack_array = package_head + send_data
    check_num = u16_check_data(pack_array[7:], data_length + 6)
    pack_array = pack_array + struct.pack("<H", check_num & 0xFFFF)
    return pack_array


def SACP_unpack(receiver_data):
    if (receiver_data[0] != 0xAA and receiver_data[1] != 0x55) or len(receiver_data) < 13:
        print(receiver_data[0], receiver_data[1], len(receiver_data))
        raise ReceiverException("所获取到的总数据不对或开头不为0xAA和0x55")
    data_len = (receiver_data[2] | receiver_data[3] << 8) & 0xFFFF
    if data_len != len(receiver_data) - 7:
        print(data_len, receiver_data)
        raise ReceiverException("所获取到的有效数据不对")
    version = receiver_data[4]
    receiver_id = receiver_data[5]
    receiver_crc = receiver_data[6]
    sender_id = receiver_data[7]
    receiver_crc_check = SACP_check_head(receiver_data, 6)
    if receiver_crc_check != receiver_crc:
        raise ReceiverException("CRC校验码不对")
    attribute = receiver_data[8]
    sequence = (receiver_data[9] | receiver_data[10] << 8) & 0xFFFF
    command_set = receiver_data[11]
    command_id = receiver_data[12]
    receiver_check_num = (receiver_data[-2] | receiver_data[-1] << 8) & 0xFFFF
    calc_receiver_check_num = u16_check_data(receiver_data[7:], data_len - 2) & 0xFFFF
    if receiver_check_num != calc_receiver_check_num:
        pass

    valid_data = receiver_data[13: -2]

    return ReceiverData(command_set, command_id, valid_data, sequence)


def SACP_validData(receiver_valid_data, package_format):
    receiver_valid_data = struct.unpack(package_format, receiver_valid_data)
    return receiver_valid_data
