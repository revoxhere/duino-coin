// This file is part of cryptosuite2.                                    //
//                                                                       //
// cryptosuite2 is free software: you can redistribute it and/or modify  //
// it under the terms of the GNU General Public License as published by  //
// the Free Software Foundation, either version 3 of the License, or     //
// (at your option) any later version.                                   //
//                                                                       //
// cryptosuite2 is distributed in the hope that it will be useful,       //
// but WITHOUT ANY WARRANTY; without even the implied warranty of        //
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         //
// GNU General Public License for more details.                          //
//                                                                       //
// You should have received a copy of the GNU General Public License     //
// along with cryptosuite2.  If not, see <http://www.gnu.org/licenses/>. //
//                                                                       //

#ifndef SHA256_CONSTANTS_H_
#define SHA256_CONSTANTS_H_

#include "default.h"
#include <inttypes.h>

#define SHA256_BLOCK_LEN 64
#define SHA256_HASH_LEN 32

#ifdef __AVR__
#include <avr/pgmspace.h>
#endif

#ifndef __AVR__
extern const uint32_t sha256_init_state[SHA256_HASH_LEN / 4];
#else
extern const uint32_t sha256_init_state[SHA256_HASH_LEN / 4] PROGMEM;
#endif

#ifndef __AVR__
extern const uint32_t sha256_constants[64];
#else
extern const uint32_t sha256_constants[64] PROGMEM;
#endif

#ifdef __AVR__
#define sha256_k(i) pgm_read_dword(sha256_constants + i)
#else
#define sha256_k(i) sha256_constants[i]
#endif


#ifdef SHA256_ENABLE_HMAC
#define SHA256_HMAC_IPAD 0x36
#define SHA256_HMAC_OPAD 0x5c
#endif

#endif
