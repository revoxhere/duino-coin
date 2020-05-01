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

#include "types.h"
#include <stdlib.h>
#include <string.h>
#include "constants.h"

sha256_hasher_t sha256_hasher_new(void)
{
	sha256_hasher_t hasher = (sha256_hasher_t) malloc(sizeof(struct sha256_hasher_s));
	if(!hasher)
	{
		return NULL;
	}
	sha256_hasher_init(hasher);
	return hasher;
}

void sha256_hasher_init(sha256_hasher_t hasher)
{
#ifdef __AVR__
	int i;
	for(i = 0; i < SHA256_HASH_LEN / 4; i++)
	{
		hasher->state.words[i] = pgm_read_dword(sha256_init_state + i);
	}
#else
	memcpy(hasher->state.words, sha256_init_state, SHA256_HASH_LEN);
#endif
	hasher->block_offset = 0;
	hasher->total_bytes = 0;
	hasher->_lock = 0;

}


void sha256_hasher_del(sha256_hasher_t hasher)
{
	free(hasher);
}

