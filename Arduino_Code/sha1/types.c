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

sha1_hasher_t sha1_hasher_new(void)
{
	sha1_hasher_t hasher = (sha1_hasher_t) malloc(sizeof(struct sha1_hasher_s));
	if(!hasher)
	{
		return NULL;
	}
	sha1_hasher_init(hasher);
	return hasher;
}

void sha1_hasher_init(sha1_hasher_t hasher)
{
	uint8_t i;
	for(i = 0; i < SHA1_HASH_LEN / 4; i++)
	{
		hasher->state.words[i] = pgm_read_dword(sha1_init_state + i);
	}
	hasher->block_offset = 0;
	hasher->total_bytes = 0;
	hasher->_lock = 0;

}


void sha1_hasher_del(sha1_hasher_t hasher)
{
	free(hasher);
}


