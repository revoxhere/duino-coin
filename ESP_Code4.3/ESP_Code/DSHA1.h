#ifndef DSHA1_H
#define DSHA1_H

#include <Arduino.h>

class DSHA1 {
    
public:
    static const size_t OUTPUT_SIZE = 20;

    DSHA1() {
        initialize(s);
    }

    DSHA1 &write(const unsigned char *data, size_t len) {
        size_t bufsize = bytes % 64;
        if (bufsize && bufsize + len >= 64) {
            memcpy(buf + bufsize, data, 64 - bufsize);
            bytes += 64 - bufsize;
            data += 64 - bufsize;
            transform(s, buf);
            bufsize = 0;
        }
        while (len >= 64) {
            transform(s, data);
            bytes += 64;
            data += 64;
            len -= 64;
        }
        if (len > 0) {
            memcpy(buf + bufsize, data, len);
            bytes += len;
        }
        return *this;
    }

    void finalize(unsigned char hash[OUTPUT_SIZE]) {
        const unsigned char pad[64] = {0x80};
        unsigned char sizedesc[8];
        writeBE64(sizedesc, bytes << 3);
        write(pad, 1 + ((119 - (bytes % 64)) % 64));
        write(sizedesc, 8);
        writeBE32(hash, s[0]);
        writeBE32(hash + 4, s[1]);
        writeBE32(hash + 8, s[2]);
        writeBE32(hash + 12, s[3]);
        writeBE32(hash + 16, s[4]);
    }

    DSHA1 &reset() {
        bytes = 0;
        initialize(s);
        return *this;
    }

    // Warmup the cache and get a boost in performance
    DSHA1 &warmup() {
        uint8_t warmup[20];
        this->write((uint8_t *)"warmupwarmupwa", 20).finalize(warmup);
        return *this;
    }

private:
    uint32_t s[5];
    unsigned char buf[64];
    uint64_t bytes;

    const uint32_t k1 = 0x5A827999ul;
    const uint32_t k2 = 0x6ED9EBA1ul;
    const uint32_t k3 = 0x8F1BBCDCul;
    const uint32_t k4 = 0xCA62C1D6ul;

    uint32_t inline f1(uint32_t b, uint32_t c, uint32_t d) { return d ^ (b & (c ^ d)); }
    uint32_t inline f2(uint32_t b, uint32_t c, uint32_t d) { return b ^ c ^ d; }
    uint32_t inline f3(uint32_t b, uint32_t c, uint32_t d) { return (b & c) | (d & (b | c)); }

    uint32_t inline left(uint32_t x) { return (x << 1) | (x >> 31); }

    void inline Round(uint32_t a, uint32_t &b, uint32_t c, uint32_t d, uint32_t &e,
                      uint32_t f, uint32_t k, uint32_t w) {
        e += ((a << 5) | (a >> 27)) + f + k + w;
        b = (b << 30) | (b >> 2);
    }

    void initialize(uint32_t s[5]) {
        s[0] = 0x67452301ul;
        s[1] = 0xEFCDAB89ul;
        s[2] = 0x98BADCFEul;
        s[3] = 0x10325476ul;
        s[4] = 0xC3D2E1F0ul;
    }

    void transform(uint32_t *s, const unsigned char *chunk) {
        uint32_t a = s[0], b = s[1], c = s[2], d = s[3], e = s[4];
        uint32_t w0, w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12, w13, w14, w15;

        Round(a, b, c, d, e, f1(b, c, d), k1, w0 = readBE32(chunk + 0));
        Round(e, a, b, c, d, f1(a, b, c), k1, w1 = readBE32(chunk + 4));
        Round(d, e, a, b, c, f1(e, a, b), k1, w2 = readBE32(chunk + 8));
        Round(c, d, e, a, b, f1(d, e, a), k1, w3 = readBE32(chunk + 12));
        Round(b, c, d, e, a, f1(c, d, e), k1, w4 = readBE32(chunk + 16));
        Round(a, b, c, d, e, f1(b, c, d), k1, w5 = readBE32(chunk + 20));
        Round(e, a, b, c, d, f1(a, b, c), k1, w6 = readBE32(chunk + 24));
        Round(d, e, a, b, c, f1(e, a, b), k1, w7 = readBE32(chunk + 28));
        Round(c, d, e, a, b, f1(d, e, a), k1, w8 = readBE32(chunk + 32));
        Round(b, c, d, e, a, f1(c, d, e), k1, w9 = readBE32(chunk + 36));
        Round(a, b, c, d, e, f1(b, c, d), k1, w10 = readBE32(chunk + 40));
        Round(e, a, b, c, d, f1(a, b, c), k1, w11 = readBE32(chunk + 44));
        Round(d, e, a, b, c, f1(e, a, b), k1, w12 = readBE32(chunk + 48));
        Round(c, d, e, a, b, f1(d, e, a), k1, w13 = readBE32(chunk + 52));
        Round(b, c, d, e, a, f1(c, d, e), k1, w14 = readBE32(chunk + 56));
        Round(a, b, c, d, e, f1(b, c, d), k1, w15 = readBE32(chunk + 60));

        Round(e, a, b, c, d, f1(a, b, c), k1, w0 = left(w0 ^ w13 ^ w8 ^ w2));
        Round(d, e, a, b, c, f1(e, a, b), k1, w1 = left(w1 ^ w14 ^ w9 ^ w3));
        Round(c, d, e, a, b, f1(d, e, a), k1, w2 = left(w2 ^ w15 ^ w10 ^ w4));
        Round(b, c, d, e, a, f1(c, d, e), k1, w3 = left(w3 ^ w0 ^ w11 ^ w5));
        Round(a, b, c, d, e, f2(b, c, d), k2, w4 = left(w4 ^ w1 ^ w12 ^ w6));
        Round(e, a, b, c, d, f2(a, b, c), k2, w5 = left(w5 ^ w2 ^ w13 ^ w7));
        Round(d, e, a, b, c, f2(e, a, b), k2, w6 = left(w6 ^ w3 ^ w14 ^ w8));
        Round(c, d, e, a, b, f2(d, e, a), k2, w7 = left(w7 ^ w4 ^ w15 ^ w9));
        Round(b, c, d, e, a, f2(c, d, e), k2, w8 = left(w8 ^ w5 ^ w0 ^ w10));
        Round(a, b, c, d, e, f2(b, c, d), k2, w9 = left(w9 ^ w6 ^ w1 ^ w11));
        Round(e, a, b, c, d, f2(a, b, c), k2, w10 = left(w10 ^ w7 ^ w2 ^ w12));
        Round(d, e, a, b, c, f2(e, a, b), k2, w11 = left(w11 ^ w8 ^ w3 ^ w13));
        Round(c, d, e, a, b, f2(d, e, a), k2, w12 = left(w12 ^ w9 ^ w4 ^ w14));
        Round(b, c, d, e, a, f2(c, d, e), k2, w13 = left(w13 ^ w10 ^ w5 ^ w15));
        Round(a, b, c, d, e, f2(b, c, d), k2, w14 = left(w14 ^ w11 ^ w6 ^ w0));
        Round(e, a, b, c, d, f2(a, b, c), k2, w15 = left(w15 ^ w12 ^ w7 ^ w1));

        Round(d, e, a, b, c, f2(e, a, b), k2, w0 = left(w0 ^ w13 ^ w8 ^ w2));
        Round(c, d, e, a, b, f2(d, e, a), k2, w1 = left(w1 ^ w14 ^ w9 ^ w3));
        Round(b, c, d, e, a, f2(c, d, e), k2, w2 = left(w2 ^ w15 ^ w10 ^ w4));
        Round(a, b, c, d, e, f2(b, c, d), k2, w3 = left(w3 ^ w0 ^ w11 ^ w5));
        Round(e, a, b, c, d, f2(a, b, c), k2, w4 = left(w4 ^ w1 ^ w12 ^ w6));
        Round(d, e, a, b, c, f2(e, a, b), k2, w5 = left(w5 ^ w2 ^ w13 ^ w7));
        Round(c, d, e, a, b, f2(d, e, a), k2, w6 = left(w6 ^ w3 ^ w14 ^ w8));
        Round(b, c, d, e, a, f2(c, d, e), k2, w7 = left(w7 ^ w4 ^ w15 ^ w9));
        Round(a, b, c, d, e, f3(b, c, d), k3, w8 = left(w8 ^ w5 ^ w0 ^ w10));
        Round(e, a, b, c, d, f3(a, b, c), k3, w9 = left(w9 ^ w6 ^ w1 ^ w11));
        Round(d, e, a, b, c, f3(e, a, b), k3, w10 = left(w10 ^ w7 ^ w2 ^ w12));
        Round(c, d, e, a, b, f3(d, e, a), k3, w11 = left(w11 ^ w8 ^ w3 ^ w13));
        Round(b, c, d, e, a, f3(c, d, e), k3, w12 = left(w12 ^ w9 ^ w4 ^ w14));
        Round(a, b, c, d, e, f3(b, c, d), k3, w13 = left(w13 ^ w10 ^ w5 ^ w15));
        Round(e, a, b, c, d, f3(a, b, c), k3, w14 = left(w14 ^ w11 ^ w6 ^ w0));
        Round(d, e, a, b, c, f3(e, a, b), k3, w15 = left(w15 ^ w12 ^ w7 ^ w1));

        Round(c, d, e, a, b, f3(d, e, a), k3, w0 = left(w0 ^ w13 ^ w8 ^ w2));
        Round(b, c, d, e, a, f3(c, d, e), k3, w1 = left(w1 ^ w14 ^ w9 ^ w3));
        Round(a, b, c, d, e, f3(b, c, d), k3, w2 = left(w2 ^ w15 ^ w10 ^ w4));
        Round(e, a, b, c, d, f3(a, b, c), k3, w3 = left(w3 ^ w0 ^ w11 ^ w5));
        Round(d, e, a, b, c, f3(e, a, b), k3, w4 = left(w4 ^ w1 ^ w12 ^ w6));
        Round(c, d, e, a, b, f3(d, e, a), k3, w5 = left(w5 ^ w2 ^ w13 ^ w7));
        Round(b, c, d, e, a, f3(c, d, e), k3, w6 = left(w6 ^ w3 ^ w14 ^ w8));
        Round(a, b, c, d, e, f3(b, c, d), k3, w7 = left(w7 ^ w4 ^ w15 ^ w9));
        Round(e, a, b, c, d, f3(a, b, c), k3, w8 = left(w8 ^ w5 ^ w0 ^ w10));
        Round(d, e, a, b, c, f3(e, a, b), k3, w9 = left(w9 ^ w6 ^ w1 ^ w11));
        Round(c, d, e, a, b, f3(d, e, a), k3, w10 = left(w10 ^ w7 ^ w2 ^ w12));
        Round(b, c, d, e, a, f3(c, d, e), k3, w11 = left(w11 ^ w8 ^ w3 ^ w13));
        Round(a, b, c, d, e, f2(b, c, d), k4, w12 = left(w12 ^ w9 ^ w4 ^ w14));
        Round(e, a, b, c, d, f2(a, b, c), k4, w13 = left(w13 ^ w10 ^ w5 ^ w15));
        Round(d, e, a, b, c, f2(e, a, b), k4, w14 = left(w14 ^ w11 ^ w6 ^ w0));
        Round(c, d, e, a, b, f2(d, e, a), k4, w15 = left(w15 ^ w12 ^ w7 ^ w1));

        Round(b, c, d, e, a, f2(c, d, e), k4, w0 = left(w0 ^ w13 ^ w8 ^ w2));
        Round(a, b, c, d, e, f2(b, c, d), k4, w1 = left(w1 ^ w14 ^ w9 ^ w3));
        Round(e, a, b, c, d, f2(a, b, c), k4, w2 = left(w2 ^ w15 ^ w10 ^ w4));
        Round(d, e, a, b, c, f2(e, a, b), k4, w3 = left(w3 ^ w0 ^ w11 ^ w5));
        Round(c, d, e, a, b, f2(d, e, a), k4, w4 = left(w4 ^ w1 ^ w12 ^ w6));
        Round(b, c, d, e, a, f2(c, d, e), k4, w5 = left(w5 ^ w2 ^ w13 ^ w7));
        Round(a, b, c, d, e, f2(b, c, d), k4, w6 = left(w6 ^ w3 ^ w14 ^ w8));
        Round(e, a, b, c, d, f2(a, b, c), k4, w7 = left(w7 ^ w4 ^ w15 ^ w9));
        Round(d, e, a, b, c, f2(e, a, b), k4, w8 = left(w8 ^ w5 ^ w0 ^ w10));
        Round(c, d, e, a, b, f2(d, e, a), k4, w9 = left(w9 ^ w6 ^ w1 ^ w11));
        Round(b, c, d, e, a, f2(c, d, e), k4, w10 = left(w10 ^ w7 ^ w2 ^ w12));
        Round(a, b, c, d, e, f2(b, c, d), k4, w11 = left(w11 ^ w8 ^ w3 ^ w13));
        Round(e, a, b, c, d, f2(a, b, c), k4, w12 = left(w12 ^ w9 ^ w4 ^ w14));
        Round(d, e, a, b, c, f2(e, a, b), k4, left(w13 ^ w10 ^ w5 ^ w15));
        Round(c, d, e, a, b, f2(d, e, a), k4, left(w14 ^ w11 ^ w6 ^ w0));
        Round(b, c, d, e, a, f2(c, d, e), k4, left(w15 ^ w12 ^ w7 ^ w1));

        s[0] += a;
        s[1] += b;
        s[2] += c;
        s[3] += d;
        s[4] += e;
    }

    uint32_t static inline readBE32(const unsigned char *ptr) {
        return __builtin_bswap32(*(uint32_t *)ptr);
    }

    void static inline writeBE32(unsigned char *ptr, uint32_t x) {
        *(uint32_t *)ptr = __builtin_bswap32(x);
    }

    void static inline writeBE64(unsigned char *ptr, uint64_t x) {
        *(uint64_t *)ptr = __builtin_bswap64(x);
    }
};
#endif
