# -*- coding: utf-8 -*-
import socket
import cantools
import struct


class SocketTCPClientChannel(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.fds = None

    def open(self):
        if self.fds:
            return self

        self.fds = socket.socket()
        self.fds.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.fds.connect((self.host, self.port))
        return self

    def close(self):
        if self.fds:
            self.fds.close()

    def read(self, n, timeout=None):
        return self.fds.recv(n)

    def write(self, b):
        if self.fds is None:
            raise ValueError

        return self.fds.send(b)


class CANMessage:
    def __init__(self, message, data):
        self.message = message
        self.data = dict().update(data)


class CAN2TCPClientChannel(SocketTCPClientChannel):
    """CAN转TCP客户端透传通道"""
    def __init__(self, host, port, dbc_file_path):
        super().__init__(host, port)
        self.dbc_file_path = dbc_file_path
        self.db = cantools.database.load_file(dbc_file_path)
        self.signals_map = dict()
        for message in self.db.messages:
            for signal in message.signals:
                self.signals_map[signal.name] = signal.initial

    def update_signal(self, signals):
        self.signals_map.update(signals)

    def decode(self, package):
        """将接收到的数据解包成CANMessage"""
        raise NotImplementedError

    def write(self, b):
        """write data to channel is not allowed"""
        pass


class USRCANET2TCPClientChannel(CAN2TCPClientChannel):
    """有人USRCANNET200 CAN转TCP客户端透传通道"""
    def decode(self, package):
        canID = struct.unpack('>I', package[1:5])[0]
        payload = package[5:]
        try:
            message = self.db.get_message_by_frame_id(canID)
        except KeyError:
            return None
        data = message.decode(payload)
        return CANMessage(message, data)

    def read(self, n, timeout=None):
        """
        接收n帧数据
        :param n: 帧数量
        :param timeout: 超时时长
        :return: list()
        """
        if timeout is None:
            pass

        message_list = list()
        count = n
        while count > 0:
            package = self.fds.recv(15)
            count -= 1
            if package == '':
                break

            message = self.decode(package)
            if message is None:
                continue

            message_list.append(message)

        return message_list
