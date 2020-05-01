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

#include "hash.h"
#include <stdio.h>
#include <string.h>


void sha1_hash_block(sha1_hasher_t hasher)
{
	int i;
	uint32_t a, b, c, d, e, temp;

	// XXX: Omit initializing the message schedule.
	// See how I did this below.
	// Allocating the message schedule would eat 2k RAM
	// which is a no-go on an AVR. 
	int i4;
	// On x86 we have to change the byte order, because...
	// I actually do not know.
	for(i = i4 = 0; i < 16; i++, i4 += 4)
	{
		hasher->buffer.words[i] =  	(((uint32_t)hasher->buffer.bytes[i4]) << 24) |
						(((uint32_t)hasher->buffer.bytes[i4 + 1]) << 16) |
						(((uint32_t)hasher->buffer.bytes[i4 + 2]) << 8) |
						(((uint32_t)hasher->buffer.bytes[i4 + 3]));
	}
	
	a = hasher->state.words[0];
	b = hasher->state.words[1];
	c = hasher->state.words[2];
	d = hasher->state.words[3];
	e = hasher->state.words[4];

	for(i = 0; i < 80; i++)
	{
		// XXX:
		// This part of the computation omits the message schedule
		// W as described in https://tools.ietf.org/html/rfc4634
		// The first 16 words of the message schedule is just the block
		// anyways and the computation of the message schedule uses only
		// the last 16 words, so we can do that.
		if( i >= 16 )
		{
			hasher->buffer.words[i & 15] = sha1_rotl(1
							, hasher->buffer.words[(i - 3)& 15]
								^ hasher->buffer.words[(i - 8)& 15]
								^ hasher->buffer.words[(i - 14)& 15]
								^ hasher->buffer.words[(i - 16)& 15]);
		}

		temp = sha1_rotl(5, a) + e + hasher->buffer.words[i & 15] + sha1_k(i);
		if(i < 20)
		{
			temp += (b & c) | ((~b) & d);
		}
		else if(i < 40)
		{
			temp += b ^ c ^ d;
		}
		else if(i < 60)
		{
			temp += (b & c) | (b & d) | (c & d);
		}
		else
		{
			temp += b ^ c ^ d;
		}





		e = d;
		d = c;
		c = sha1_rotl(30, b);
		b = a;
		a = temp;
	}
	hasher->state.words[0] += a;
	hasher->state.words[1] += b;
	hasher->state.words[2] += c;
	hasher->state.words[3] += d;
	hasher->state.words[4] += e;
	
}



void sha1_hasher_add_byte(sha1_hasher_t hasher, uint8_t byte)
{
	hasher->buffer.bytes[hasher->block_offset] = byte;
	hasher->block_offset++;
	if(hasher->block_offset == SHA1_BLOCK_LEN)
	{
		sha1_hash_block(hasher);
		hasher->block_offset = 0;
	}
}

/**
 * NOTE: once the block has been pad'ed the hasher will
 * produce nonsense data. Therefore putc will return EOF
 * once the hasher has been pad'ed (this happens, when 
 * sha1_hasher_gethash or sha1_hasher_gethmac are invoced).
 * */
int sha1_hasher_putc(sha1_hasher_t hasher, uint8_t byte)
{
	if(hasher->_lock)
	{
		return EOF;
	}
	hasher->total_bytes++;
	sha1_hasher_add_byte(hasher, byte);
	return byte;

}



void sha1_hasher_pad(sha1_hasher_t hasher)
{
	hasher->_lock = 1;
	sha1_hasher_add_byte(hasher, 0x80);
	while(hasher->block_offset != 56)
	{
		sha1_hasher_add_byte(hasher, 0);
	}

	// FIXME:
	// Use a loop for this.
	sha1_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 56);
	sha1_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 48);
	sha1_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 40);
	sha1_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 32);
	sha1_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 24);
	sha1_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 16);
	sha1_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 8);
	sha1_hasher_add_byte(hasher, hasher->total_bytes * 8);

}

uint8_t * sha1_hasher_gethash(sha1_hasher_t hasher)
{
	sha1_hasher_pad(hasher);
	int i;

	// switch byte order.
	for(i = 0; i < 8; i++)
	{
		uint32_t a, b;
		a = hasher->state.words[i];
		b = a << 24;
		b |= ( a << 8) & 0x00ff0000;
		b |= ( a >> 8) & 0x0000ff00;
		b |= a >> 24;
		hasher->state.words[i] = b;
	}
	return hasher->state.bytes;
}


#ifdef SHA1_ENABLE_HMAC
void sha1_hasher_init_hmac(sha1_hasher_t hasher, const uint8_t * key, size_t key_len)
{
	int i;
	memset(hasher->hmac_key_buffer, 0, SHA1_BLOCK_LEN);

	if(key_len > SHA1_BLOCK_LEN)
	{
		sha1_hasher_init(hasher);
		while(key_len--)
		{
			sha1_hasher_putc(hasher, *key++);
		}
		memcpy(hasher->hmac_key_buffer, 
				sha1_hasher_gethash(hasher),
				SHA1_HASH_LEN);
	}
	else
	{
		memcpy(hasher->hmac_key_buffer, key, key_len);
	}
	sha1_hasher_init(hasher);
	for(i = 0; i < SHA1_BLOCK_LEN; i++)
	{
		sha1_hasher_putc(hasher, hasher->hmac_key_buffer[i] ^ SHA1_HMAC_IPAD);
	}

}
uint8_t * sha1_hasher_gethmac(sha1_hasher_t hasher)
{
	int i;
	memcpy(hasher->hmac_inner_hash, sha1_hasher_gethash(hasher),
			SHA1_HASH_LEN);
	sha1_hasher_init(hasher);

	for(i = 0; i < SHA1_BLOCK_LEN; i++)
	{
		sha1_hasher_putc(hasher, hasher->hmac_key_buffer[i] ^ SHA1_HMAC_OPAD);
	}
	for(i = 0; i < SHA1_HASH_LEN; i++)
	{
		sha1_hasher_putc(hasher, hasher->hmac_inner_hash[i]);
	}
	return sha1_hasher_gethash(hasher);
}
#endif

