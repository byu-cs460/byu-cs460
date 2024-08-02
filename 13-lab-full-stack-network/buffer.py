class TCPSendBuffer(object):

    def __init__(self, seq: int):
        self.buffer = b''
        self.base_seq = seq
        self.next_seq = self.base_seq
        self.last_seq = self.base_seq

    def bytes_not_yet_sent(self) -> int:
        pass

    def bytes_outstanding(self) -> int:
        pass

    def put(self, data: bytes) -> int:
        pass

    def get(self, size: int) -> tuple[bytes, int]:
        pass

    def get_for_resend(self, size: int) -> tuple[bytes, int]:
        pass

    def slide(self, sequence: int) -> None:
        pass


class TCPReceiveBuffer(object):
    def __init__(self, seq: int):
        self.buffer = {}
        self.base_seq = seq

    def put(self, data: bytes, sequence: int) -> None:
        pass

    def get(self) -> tuple[bytes, int]:
        pass
