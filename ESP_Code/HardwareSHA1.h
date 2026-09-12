// SPDX-License-Identifier: MIT
// Conservative classic ESP32 hardware SHA-1 helper for Duino-Coin.

#pragma once
#include <Arduino.h>

#if !defined(CONFIG_IDF_TARGET_ESP32)
#error "HardwareSHA1.h is for the original/classic ESP32 only"
#endif

#include <sha/sha_parallel_engine.h>
#include <hal/sha_ll.h>
#include <soc/hwcrypto_reg.h>
#include <soc/dport_reg.h>

class HardwareSHA1 {
public:
    // Intentionally not IRAM_ATTR on Arduino-ESP32 3.x / GCC 13.
    // Forcing this literal-heavy helper into IRAM can trigger Xtensa
    // 'dangerous relocation: l32r: literal placed after use' link errors.
    static inline void waitIdle() {
        while (DPORT_REG_READ(SHA_1_BUSY_REG)) {}
    }

    static inline void lock() {
        esp_sha_lock_engine(SHA1);
        DPORT_REG_SET_BIT(DPORT_PERI_CLK_EN_REG, DPORT_PERI_EN_SHA);
        DPORT_REG_CLR_BIT(DPORT_PERI_RST_EN_REG,
                          DPORT_PERI_EN_SHA | DPORT_PERI_EN_SECUREBOOT);
    }

    static inline void unlock() {
        esp_sha_unlock_engine(SHA1);
    }

    static inline uint32_t pack4(const uint8_t* p) {
        return (uint32_t(p[0]) << 24) | (uint32_t(p[1]) << 16) |
               (uint32_t(p[2]) << 8) | uint32_t(p[3]);
    }

    static void preparePrefix40(const char* prefix, uint32_t words[10]) {
        const uint8_t* p = reinterpret_cast<const uint8_t*>(prefix);
        for (int i = 0; i < 10; ++i) words[i] = pack4(p + i * 4);
    }

    static void expectedWords(const uint8_t expected[20], uint32_t out[5]) {
        for (int i = 0; i < 5; ++i) out[i] = pack4(expected + i * 4);
    }

    // Hash exactly: 40-byte prefix + decimal nonce. This always fits in one SHA1 block.
    // Returns true only on exact 160-bit match.
    static inline bool hash40Locked(
        const uint32_t prefix[10], const char* nonce, uint8_t nonceLen,
        const uint32_t expected[5]
    ) {
        volatile uint32_t* const sha =
            reinterpret_cast<volatile uint32_t*>(SHA_TEXT_BASE);

        // SHA_LOAD overwrites words 0..4 with the digest, so these are always restored.
        sha[0] = prefix[0]; sha[1] = prefix[1]; sha[2] = prefix[2];
        sha[3] = prefix[3]; sha[4] = prefix[4];

        // Words 5..9 normally survive LOAD, but writing them too makes the path robust
        // across framework revisions. This can be trimmed after on-board benchmarking.
        sha[5] = prefix[5]; sha[6] = prefix[6]; sha[7] = prefix[7];
        sha[8] = prefix[8]; sha[9] = prefix[9];

        uint8_t tail[16] __attribute__((aligned(4))) = {};
        for (uint8_t i = 0; i < nonceLen; ++i) tail[i] = uint8_t(nonce[i]);
        tail[nonceLen] = 0x80;

        sha[10] = pack4(tail + 0);
        sha[11] = pack4(tail + 4);
        sha[12] = pack4(tail + 8);
        sha[13] = pack4(tail + 12);
        sha[14] = 0;
        sha[15] = uint32_t(40U + nonceLen) * 8U;

        sha_ll_start_block(SHA1);
        waitIdle();
        sha_ll_load(SHA1);
        waitIdle();

        // Almost every candidate fails on word 0, so avoid four extra APB reads.
        if (DPORT_REG_READ(SHA_TEXT_BASE + 0) != expected[0]) return false;
        if (DPORT_REG_READ(SHA_TEXT_BASE + 4) != expected[1]) return false;
        if (DPORT_REG_READ(SHA_TEXT_BASE + 8) != expected[2]) return false;
        if (DPORT_REG_READ(SHA_TEXT_BASE + 12) != expected[3]) return false;
        return DPORT_REG_READ(SHA_TEXT_BASE + 16) == expected[4];
    }

    static bool selfTest() {
        static const uint32_t expect[5] = {
            0xA9993E36UL, 0x4706816AUL, 0xBA3E2571UL, 0x7850C26CUL, 0x9CD0D89DUL
        };
        volatile uint32_t* const sha =
            reinterpret_cast<volatile uint32_t*>(SHA_TEXT_BASE);
        lock();
        sha[0] = 0x61626380UL;
        for (int i = 1; i < 15; ++i) sha[i] = 0;
        sha[15] = 24;
        sha_ll_start_block(SHA1);
        waitIdle();
        sha_ll_load(SHA1);
        waitIdle();
        bool ok = true;
        for (int i = 0; i < 5; ++i)
            ok &= DPORT_REG_READ(SHA_TEXT_BASE + i * 4) == expect[i];
        unlock();
        return ok;
    }
};
