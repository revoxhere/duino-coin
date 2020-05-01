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

#ifndef SHA1_CONSTANTS_H_
#define SHA1_CONSTANTS_H_

#include "default.h"
#include <inttypes.h>

#define SHA1_BLOCK_LEN 64
#define SHA1_HASH_LEN 20

#ifdef __AVR__
#include <avr/pgmspace.h>
#endif

#ifndef __AVR__
extern const uint32_t sha1_init_state[SHA1_HASH_LEN / 4];
#else
extern const uint32_t sha1_init_state[SHA1_HASH_LEN / 4] PROGMEM;
#endif

#ifndef __AVR__
extern const uint32_t sha1_constants[4];
#else
extern const uint32_t sha1_constants[4] PROGMEM;
#endif


// From RFC3174 (http://www.faqs.org/rfcs/rfc3174.html) 
// (Section 5):
// 
// A sequence of constant words K(0), K(1), ... , K(79) is used in the
// SHA-1.  In hex these are given by
// 
//       K(t) = 5A827999         ( 0 <= t <= 19)
// 
//       K(t) = 6ED9EBA1         (20 <= t <= 39)
// 
//       K(t) = 8F1BBCDC         (40 <= t <= 59)
// 
//       K(t) = CA62C1D6         (60 <= t <= 79).
// 
// This can be achieved using an integer division by 20 and only 4 constants.

#ifdef __AVR__
#define sha1_k(i) pgm_read_dword(sha1_constants + (i / 20))
#else
#define sha1_k(i) sha1_constants[i / 20]
#endif


#ifdef SHA1_ENABLE_HMAC
#define SHA1_HMAC_IPAD 0x36
#define SHA1_HMAC_OPAD 0x5c
#endif

#endif

