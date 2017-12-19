import unittest

from hpfeeds.protocol import (
    Unpacker,
    msgauth,
    msghdr,
    msgpublish,
    msgsubscribe,
    readinfo,
    readpublish,
    readsubscribe,
)


class TestMessageBuilder(unittest.TestCase):

    def test_msghdr(self):
        assert msghdr(1, b'abcdefg') == b'\x00\x00\x00\x0c\x01abcdefg'

    def test_msgpublish(self):
        msg = msgpublish('ident', 'chan', 'somedata')
        assert msg == b'\x00\x00\x00\x18\x03\x05ident\x04chansomedata'

    def test_msgsubscribe(self):
        msg = msgsubscribe('ident', 'chan')
        assert msg == b'\x00\x00\x00\x0f\x04\x05identchan'

    def test_msgauth(self):
        msg = msgauth(b'rand', 'ident', 'secret')
        assert msg == (
            b'\x00\x00\x00\x1f\x02\x05ident\xbf\xa9^\x11I\xcd\x9es'
            b'\x80\xfd\xfcaJW\tZ\xb7\x19\xc1\xb4'
        )


class TestMessageReader(unittest.TestCase):

    def test_readinfo(self):
        name, rand = readinfo(b'\x07hpfeeds\x01 a\xff')
        assert name == 'hpfeeds'
        assert rand == b'\x01 a\xff'

    def test_readpublish(self):
        ident, chan, data = readpublish(b'\x05ident\x04chansomedata')
        assert ident == 'ident'
        assert chan == 'chan'
        assert data == b'somedata'

    def test_readsubscribe(self):
        ident, chan = readsubscribe(b'\x05identchan')
        assert ident == 'ident'
        assert chan == 'chan'


class TestUnpacker(unittest.TestCase):

    def test_unpack_1(self):
        unpacker = Unpacker()
        unpacker.feed(msghdr(1, b'abcdefghijklmnopqrstuvwxyz'))
        packets = list(iter(unpacker))
        assert packets == [(1, b'abcdefghijklmnopqrstuvwxyz')]

    def test_unpack_2(self):
        message = msghdr(1, b'abcdefghijklmnopqrstuvwxyz')
        unpacker = Unpacker()

        # The unpacker shouldn't yield any messages until it has consumed the
        # full object
        for b in message[:-1]:
            unpacker.feed([b])
            assert list(iter(unpacker)) == []

        unpacker.feed([message[-1]])
        assert list(iter(unpacker)) == [(1, b'abcdefghijklmnopqrstuvwxyz')]
