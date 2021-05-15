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

#ifndef SHA1_HASH_H_
#define SHA1_HASH_H_


#include "default.h"
#include "constants.h"
#include "types.h"
#include "basic.h"

void sha1_hash_block(sha1_hasher_t hasher);

void sha1_hasher_add_byte(sha1_hasher_t hasher, uint8_t byte);

/**
 * NOTE: once the block has been pad'ed the hasher will
 * produce nonsense data. Therefore putc will return EOF
 * once the hasher has been pad'ed (this happens, when 
 * sha1_hasher_gethash or sha1_hasher_gethmac are invoced).
 * */
uint8_t sha1_hasher_putc(sha1_hasher_t hasher, uint8_t byte);

void sha1_hasher_pad(sha1_hasher_t hasher);

/**
 * NOTE: this will NOT return a copy of the data but
 * a REFERENCE! One MUST NOT free the result.
 *
 * Also this modifies the state of the hasher. The
 * hasher has an internal lock ensuring that writing
 * to the hasher fails after this operation.
 * */
uint8_t * sha1_hasher_gethash(sha1_hasher_t hasher);

#ifdef SHA1_ENABLE_HMAC
void sha1_hasher_init_hmac(sha1_hasher_t hasher, const uint8_t * key, size_t key_len);
uint8_t * sha1_hasher_gethmac(sha1_hasher_t hasher);
#endif

#endif

