# Pure Python (2.x) implementation of the XXTEA cipher
# (c) 2009. Ivan Voras <ivoras@gmail.com>
# Released under the BSD License.
#
# This is a fascinating cipher which doesn't fall into typical "block cipher"
# type but can use blocks of unlimited length (as long as they are 32-bit
# aligned). Because of this it can be used to encipher long data strings
# without relying on "modes of operation" like CBC, etc. OTOH, using it in
# this native mode precludes it from being used for "streaming" purposes.
# For details, see http://en.wikipedia.org/wiki/XXTEA

import struct
import types

def raw_xxtea(v, n, k):
    assert type(v) == type([])
    assert type(k) == type([]) or type(k) == type(())
    assert type(n) == type(1)

    def MX():
        return ((z>>5)^(y<<2)) + ((y>>3)^(z<<4))^(sum^y) + (k[(p & 3)^e]^z)

    def u32(x):
        return x & 0xffffffff

    y = v[0]
    sum = 0
    DELTA = 0x9e3779b9
    if n > 1:       # Encoding
        z = v[n-1]
        q = 6 + 52 / n
        while q > 0:
            q -= 1
            sum = u32(sum + DELTA)
            e = u32(sum >> 2) & 3
            p = 0
            while p < n - 1:
                y = v[p+1]
                z = v[p] = u32(v[p] + MX())
                p += 1
            y = v[0]
            z = v[n-1] = u32(v[n-1] + MX())
        return 0
    elif n < -1:    # Decoding
        n = -n
        q = 6 + 52 / n
        sum = u32(q * DELTA)
        while sum != 0:
            e = u32(sum >> 2) & 3
            p = n - 1
            while p > 0:
                z = v[p-1]
                y = v[p] = u32(v[p] - MX())
                p -= 1
            z = v[n-1]
            y = v[0] = u32(v[0] - MX())
            sum = u32(sum - DELTA)
        return 0
    return 1


class XXTEAException(Exception):
    pass


class XXTEA:
    """
    XXTEA wrapper class, easy to use and compatible (by duck typing) with the
    Blowfish class.
    """

    def __init__(self, key):
        """
        Initializes the inner class data with the given key. The key must be
        128-bit (16 characters) in length.
        """
        if len(key) != 16 or type(key) != type(""):
            raise XXTEAException("Invalid key")
        self.key = struct.unpack("IIII", key)
        assert len(self.key) == 4
        self.initCTR()

    def encrypt(self, data):
        """
        Encrypts a block of data (of size a multiple of 4 bytes, minimum 8
        bytes) and returns the encrypted data.
        """
        if len(data) % 4 != 0:
            raise XXTEAException("Invalid data - size must be a multiple of 4 bytes")
        ldata = len(data) / 4
        idata = list(struct.unpack("%dI" % ldata, data))
        if raw_xxtea(idata, ldata, self.key) != 0:
            raise XXTEAException("Cannot encrypt")
        return struct.pack("%dI" % ldata, *idata)

    def decrypt(self, data):
        """
        Decrypts a block of data encrypted with encrypt() and returns the
        decrypted data.
        """
        if len(data) % 4 != 0:
            raise XXTEAException("Invalid data - size must be a multiple of 4 bytes")
        ldata = len(data) / 4
        idata = list(struct.unpack("%dI" % ldata, data))
        if raw_xxtea(idata, -ldata, self.key) != 0:
            raise XXTEAException("Cannot encrypt")
        return struct.pack("%dI" % ldata, *idata)

    def initCTR(self, iv=0):
        """
        Initializes CTR mode with optional 32-bit IV.
        """
        self.ctr_iv = [0, iv]
        self._calcCTRBUF()

    def _calcCTRBUF(self):
        """
        Calculates one (64-bit) block of CTR keystream.
        """
        self.ctr_cks = self.encrypt(struct.pack("II", *self.ctr_iv)) # keystream block
        self.ctr_iv[1] += 1
        if self.ctr_iv[1] > 0xffffffff:
            self.ctr_iv[0] += 1
            self.ctr_iv[1] = 0
        self.ctr_pos = 0

    def _nextCTRByte(self):
        """Returns one byte of CTR keystream"""
        b = ord(self.ctr_cks[self.ctr_pos])
        self.ctr_pos += 1
        if self.ctr_pos >= len(self.ctr_cks):
            self._calcCTRBUF()
        return b

    def encryptCTR(self, data):
        """
        Encrypts a buffer of data with CTR mode. Multiple successive buffers
        (belonging to the same logical stream of buffers) can be encrypted
        with this method one after the other without any intermediate work.
        """
        if type(data) != types.StringType:
            raise RuntimeException, "Can only work on 8-bit strings"
        result = []
        for ch in data:
            result.append(chr(ord(ch) ^ self._nextCTRByte()))
        return "".join(result)

    def decryptCTR(self, data):
        return self.encryptCTR(data)

    def block_size(self):
        return 8

    def key_length(self):
        return 16

    def key_bits(self):
        return self.key_length()*8


if __name__ == "__main__":
    k = [1,2,0xffffffff,4]
    v = [0,9,8,7,6,0xffffffff,4,3,2,1]

    print "Testing raw block encryption and decryption"
    raw_xxtea(v, 10, k)
    for x in v:
        print "%08x\t" % x,
    print

    raw_xxtea(v, -10, k)
    for x in v:
        print "%08x\t" % x,
    print

    print "Testing XXTEA class block encryption and decryption"
    x = XXTEA("1234567887654321")
    enc = x.encrypt("abcd1234")
    print repr(enc)
    dec = x.decrypt(enc)
    print dec

    print "Testing CTR mode"
    x.initCTR()
    enc = x.encryptCTR("The quick brown fox jumps over the lazy dog")
    print repr(enc)
    x.initCTR()
    dec = x.decryptCTR(enc)
    print dec

    from time import time
    print "Testing speed"
    t1 = time()
    n = 0
    while True:
        for i in xrange(1000):
            enc = x.encryptCTR("The quick brown fox jumps over the lazy dog %d" % i)
        n += 1000
        t2 = time()
        if t2 - t1 > 5:
            break
    print "%d encryptions in %0.1f seconds: %0.1f enc/s" % (n, t2-t1, n/(t2-t1))



