import os
from jt808.tools import tools

# 文件码流负载包


class AttachDataRate:
    # 从Config.py中获取数据
    def __init__(self, filePath, tcp):
        self.t = tools.Tools()
        self.tcp = tcp
        self.filePath = filePath
        self.BUFFER = 64000  # 分包大小默认长度 64K

    # 文件名称

    def getAttachName(self, filepath):
        name = self.t.getDocNameToHex(filepath)
        if len(name) != 100:
            name = name + (100 - len(name)) * '0'
        print('文件名称', name)
        return name

    # 数据长度，输入16进制字节
    def getDataLen(self, tempHex):
        data_int = int(len(tempHex) / 2)
        data_len = self.t.IntToHex(data_int, 8)
        print('数据长度', data_len)
        return data_len

    # 计算偏移量
    def getDataOffset(self, count):
        sum = count * self.BUFFER
        data_offset = self.t.IntToHex(sum, 8)
        print('数据偏移量', data_offset)
        return data_offset

    # 组合码流
    def combineData(self, data_offset, data_len, data_body):
        # 帧头标识 30316364
        # 数据偏移量 00000000
        self.data = ('30316364' + self.getAttachName(self.filePath) +
                     data_offset + data_len + data_body)
        print('文件码流负载包：', self.data)
        return self.data

    # 分包组装，按照buffer大小切片
    def sendData(self):
        with open(self.filePath, 'rb') as f:  # 这里我们以二进制读的方式打开文件
            filesize = os.path.getsize(self.filePath)
            count = 0
            while True:
                if filesize >= self.BUFFER:
                    content = f.read(self.BUFFER)  # 每次读出来的内容
                    # print(content)
                    content_hex = self.t.BinToHex(content)  # 转16进制字节流
                    data_len = self.getDataLen(content_hex)  # 数据长度
                    data_offset = self.getDataOffset(count)  # 计算偏移量
                    count += 1
                    attData = self.combineData(
                        data_offset, data_len, content_hex)
                    self.tcp.send(bytes.fromhex(attData))
                    filesize -= self.BUFFER                 # 分包

                else:
                    content = f.read(filesize)
                    # print(content)
                    content_hex = self.t.BinToHex(content)  # 转16进制字节流
                    data_len = self.getDataLen(content_hex)  # 数据长度
                    data_offset = self.getDataOffset(count)  # 计算偏移量
                    attData = self.combineData(
                        data_offset, data_len, content_hex)
                    self.tcp.send(bytes.fromhex(attData))
                    break


if __name__ == '__main__':
    path = '../../attachment/02_64_6401_3_0.mp4'
    file = '../../attachment/52204.jpg'
    from socket import *
    tcp = socket(AF_INET, SOCK_STREAM)
    tcp.connect(('192.168.1.192', 1079))
    a = AttachDataRate(path, tcp)
    print(a.sendData())
    # print('文件码流负载包：', a.getData())
