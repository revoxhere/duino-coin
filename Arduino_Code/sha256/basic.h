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

#ifndef SHA256_BASIC_H_
#define SHA256_BASIC_H_

#include "default.h"
#include <inttypes.h>

#define sha_ch(x, y, z)      (((x) & ((y) ^ (z))) ^ (z))
#define sha_maj(x, y, z)     (((x) & ((y) | (z))) | ((y) & (z)))
#define sha_parity(x, y, z)  ((x) ^ (y) ^ (z))

#define sha256_shr(bits,word)      ((word) >> (bits))
#define sha256_rotl(bits,word)     (((word) << (bits)) | ((word) >> (32 - (bits))))
#define sha256_rotr(bits,word)     (((word) >> (bits)) | ((word) << (32 - (bits))))

#define sha256_SIGMA0(word)   (sha256_rotr(2, word) ^ sha256_rotr(13, word) ^ sha256_rotr(22, word))
#define sha256_SIGMA1(word)   (sha256_rotr(6, word) ^ sha256_rotr(11, word) ^ sha256_rotr(25, word))
#define sha256_sigma0(word)   (sha256_rotr(7, word) ^ sha256_rotr(18, word) ^ sha256_shr(3, word))
#define sha256_sigma1(word)   (sha256_rotr(17, word) ^ sha256_rotr(19, word) ^ sha256_shr(10, word))

#endif
