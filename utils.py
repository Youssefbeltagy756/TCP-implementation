import socket
import zlib
import struct

def calculateChecksum(data):
    checksum = zlib.crc32(data)
    return checksum

def invertSeqNum(seqnum):
    return 0 if seqnum == 1 else 1

class Message:
    def __init__(self, src_port, dest_port, seq_num, ACK_num, data_offset, reserved, flags, window_size, check_sum, urgent_ptr, data):
        self.src_port = src_port
        self.dest_port = dest_port
        self.seq_num = seq_num
        self.ACK_num = ACK_num
        self.data_offset = data_offset
        self.reserved = reserved
        self.flags = flags
        self.window_size = window_size
        self.check_sum = check_sum
        self.urgent_ptr = urgent_ptr
        self.data = data  

    def returnVals(self):
        return self.src_port, self.dest_port, self.seq_num, self.ACK_num, self.data_offset, self.reserved, self.flags, self.window_size, self.check_sum, self.urgent_ptr
    