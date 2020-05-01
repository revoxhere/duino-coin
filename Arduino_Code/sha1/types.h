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

#ifndef SHA1_TYPES_H_
#define SHA1_TYPES_H_

#include "default.h"
#include <inttypes.h>
#include <stddef.h>
#include "constants.h"


typedef union 
{
	uint8_t bytes[SHA1_HASH_LEN];
	uint32_t words[SHA1_HASH_LEN / 4];
	
} sha1_state_t;

typedef union
{
	uint8_t bytes[SHA1_BLOCK_LEN];
	uint32_t words[SHA1_BLOCK_LEN / 4];

} sha1_block_t;

typedef struct __attribute__((__packed__)) sha1_hasher_s
{
	sha1_state_t state;
	sha1_block_t buffer;

	uint8_t block_offset;
	uint64_t total_bytes;
	uint8_t _lock;
#ifdef SHA1_ENABLE_HMAC
	uint8_t hmac_key_buffer[SHA1_BLOCK_LEN];
	uint8_t hmac_inner_hash[SHA1_HASH_LEN];
#endif
} * sha1_hasher_t;

sha1_hasher_t sha1_hasher_new(void);
void sha1_hasher_del(sha1_hasher_t hasher);
void sha1_hasher_init(sha1_hasher_t hasher);


#endif

