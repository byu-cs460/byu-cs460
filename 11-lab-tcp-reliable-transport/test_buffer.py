import binascii
import unittest

from buffer import TCPSendBuffer, TCPReceiveBuffer


class TestBuffer(unittest.TestCase):

    def test_send_buffer(self):
        buf = TCPSendBuffer(1057)

        self.assertEqual(buf.buffer, b'')
        self.assertEqual(buf.base_seq, 1057)
        self.assertEqual(buf.next_seq, 1057)
        self.assertEqual(buf.last_seq, 1057)
        self.assertEqual(buf.bytes_outstanding(), 0)
        self.assertEqual(buf.bytes_not_yet_sent(), 0)


        buf.put(b'abcdefg')
        self.assertEqual(buf.buffer, b'abcdefg')
        self.assertEqual(buf.base_seq, 1057)
        self.assertEqual(buf.next_seq, 1057)
        self.assertEqual(buf.last_seq, 1064)
        self.assertEqual(buf.bytes_outstanding(), 0)
        self.assertEqual(buf.bytes_not_yet_sent(), 7)


        buf.put(b'hijk')
        self.assertEqual(buf.buffer, b'abcdefghijk')
        self.assertEqual(buf.base_seq, 1057)
        self.assertEqual(buf.next_seq, 1057)
        self.assertEqual(buf.last_seq, 1068)
        self.assertEqual(buf.bytes_outstanding(), 0)
        self.assertEqual(buf.bytes_not_yet_sent(), 11)


        data, seq = buf.get(4)
        self.assertEqual(data, b'abcd')
        self.assertEqual(seq, 1057)
        self.assertEqual(buf.buffer, b'abcdefghijk')
        self.assertEqual(buf.base_seq, 1057)
        self.assertEqual(buf.next_seq, 1061)
        self.assertEqual(buf.last_seq, 1068)
        self.assertEqual(buf.bytes_outstanding(), 4)
        self.assertEqual(buf.bytes_not_yet_sent(), 7)


        data, seq = buf.get(4)
        self.assertEqual(data, b'efgh')
        self.assertEqual(seq, 1061)
        self.assertEqual(buf.buffer, b'abcdefghijk')
        self.assertEqual(buf.base_seq, 1057)
        self.assertEqual(buf.next_seq, 1065)
        self.assertEqual(buf.last_seq, 1068)
        self.assertEqual(buf.bytes_outstanding(), 8)
        self.assertEqual(buf.bytes_not_yet_sent(), 3)


        buf.slide(1061)
        self.assertEqual(buf.buffer, b'efghijk')
        self.assertEqual(buf.base_seq, 1061)
        self.assertEqual(buf.next_seq, 1065)
        self.assertEqual(buf.last_seq, 1068)
        self.assertEqual(buf.bytes_outstanding(), 4)
        self.assertEqual(buf.bytes_not_yet_sent(), 3)


        data, seq = buf.get_for_resend(4)
        self.assertEqual(data, b'efgh')
        self.assertEqual(seq, 1061)
        self.assertEqual(buf.buffer, b'efghijk')
        self.assertEqual(buf.base_seq, 1061)
        self.assertEqual(buf.next_seq, 1065)
        self.assertEqual(buf.last_seq, 1068)
        self.assertEqual(buf.bytes_outstanding(), 4)
        self.assertEqual(buf.bytes_not_yet_sent(), 3)


        data, seq = buf.get(4)
        self.assertEqual(data, b'ijk')
        self.assertEqual(seq, 1065)
        self.assertEqual(buf.buffer, b'efghijk')
        self.assertEqual(buf.base_seq, 1061)
        self.assertEqual(buf.next_seq, 1068)
        self.assertEqual(buf.last_seq, 1068)
        self.assertEqual(buf.bytes_outstanding(), 7)
        self.assertEqual(buf.bytes_not_yet_sent(), 0)


    def test_receive_buffer(self):
        buf = TCPReceiveBuffer(2021)

        # put three chunks in buffer
        buf.put(b'fghi', 2026)
        buf.put(b'def', 2024)
        buf.put(b'mn', 2033)
        self.assertEqual(buf.buffer,
                {2024: b'def', 2027: b'ghi', 2033: b'mn'})
        self.assertEqual(buf.base_seq, 2021)

        # ignore a chunk starting with the same sequence number if the existing
        # chunk is longer
        buf.put(b'm', 2033)
        self.assertEqual(buf.buffer,
                {2024: b'def', 2027: b'ghi', 2033: b'mn'})
        self.assertEqual(buf.base_seq, 2021)

        # overwrite a chunk starting with the same sequence number if the
        # existing chunk is shorter
        buf.put(b'mno', 2033)
        self.assertEqual(buf.buffer,
                {2024: b'def', 2027: b'ghi', 2033: b'mno'})
        self.assertEqual(buf.base_seq, 2021)

        # try to get ready data; none is ready because initial bytes are
        # missing
        data, start = buf.get()
        self.assertEqual(data, b'')
        self.assertEqual(buf.base_seq, 2021)

        # add missing data
        buf.put(b'abc', 2021)
        self.assertEqual(buf.buffer,
                {2021: b'abc', 2024: b'def', 2027: b'ghi', 2033: b'mno'})
        self.assertEqual(buf.base_seq, 2021)

        # get ready data
        data, start = buf.get()
        self.assertEqual(data, b'abcdefghi')
        self.assertEqual(start, 2021)
        self.assertEqual(buf.base_seq, 2030)
        self.assertEqual(buf.buffer,
                {2033: b'mno'})

        # make sure buffer does not accept data with seq number lower
        # than base seq
        buf.put(b'abc', 2021)
        self.assertEqual(buf.base_seq, 2030)
        self.assertEqual(buf.buffer,
                {2033: b'mno'})

        # add missing data
        buf.put(b'jkl', 2030)
        self.assertEqual(buf.buffer,
                {2030: b'jkl', 2033: b'mno'})

        # get ready data
        data, start = buf.get()
        self.assertEqual(data, b'jklmno')
        self.assertEqual(start, 2030)
        self.assertEqual(buf.base_seq, 2036)

if __name__ == '__main__':
    unittest.main()
