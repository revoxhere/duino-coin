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


void sha256_hash_block(sha256_hasher_t hasher)
{
	int i;
	uint32_t a, b, c, d, e, f, g, h, t1, t2;

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
	f = hasher->state.words[5];
	g = hasher->state.words[6];
	h = hasher->state.words[7];

	for(i = 0; i < 64; i++)
	{
		// XXX:
		// This part of the computation omits the message schedule
		// W as described in https://tools.ietf.org/html/rfc4634
		// The first 16 words of the message schedule is just the block
		// anyways and the computation of the message schedule uses only
		// the last 16 words, so we can do that.
		if( i >= 16 )
		{
			hasher->buffer.words[i & 15] = sha256_sigma1(hasher->buffer.words[(i - 2) & 15]) +
				hasher->buffer.words[(i - 7) & 15] + 
				sha256_sigma0(hasher->buffer.words[(i - 15) & 15]) +
				hasher->buffer.words[(i - 16) & 15];
		}
		t1 = h + sha256_SIGMA1(e) + sha_ch(e, f, g) + sha256_k(i) + hasher->buffer.words[i & 15];
		t2 = sha256_SIGMA0(a) + sha_maj(a, b, c);
		h = g;
		g = f;
		f = e;
		e = d + t1;
		d = c;
		c = b;
		b = a;
		a = t1 + t2;
	}
	hasher->state.words[0] += a;
	hasher->state.words[1] += b;
	hasher->state.words[2] += c;
	hasher->state.words[3] += d;
	hasher->state.words[4] += e;
	hasher->state.words[5] += f;
	hasher->state.words[6] += g;
	hasher->state.words[7] += h;
	
}



void sha256_hasher_add_byte(sha256_hasher_t hasher, uint8_t byte)
{
	hasher->buffer.bytes[hasher->block_offset] = byte;
	hasher->block_offset++;
	if(hasher->block_offset == SHA256_BLOCK_LEN)
	{
		sha256_hash_block(hasher);
		hasher->block_offset = 0;
	}
}

/**
 * NOTE: once the block has been pad'ed the hasher will
 * produce nonsense data. Therefore putc will return EOF
 * once the hasher has been pad'ed (this happens, when 
 * sha256_hasher_gethash or sha256_hasher_gethmac are invoced).
 * */
int sha256_hasher_putc(sha256_hasher_t hasher, uint8_t byte)
{
	if(hasher->_lock)
	{
		return EOF;
	}
	hasher->total_bytes++;
	sha256_hasher_add_byte(hasher, byte);
	return byte;

}



void sha256_hasher_pad(sha256_hasher_t hasher)
{
	hasher->_lock = 1;
	sha256_hasher_add_byte(hasher, 0x80);
	while(hasher->block_offset != 56)
	{
		sha256_hasher_add_byte(hasher, 0);
	}

	// FIXME:
	// Use a loop for this.
	sha256_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 56);
	sha256_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 48);
	sha256_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 40);
	sha256_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 32);
	sha256_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 24);
	sha256_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 16);
	sha256_hasher_add_byte(hasher, hasher->total_bytes * 8 >> 8);
	sha256_hasher_add_byte(hasher, hasher->total_bytes * 8);

}

uint8_t * sha256_hasher_gethash(sha256_hasher_t hasher)
{
	sha256_hasher_pad(hasher);
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


#ifdef SHA256_ENABLE_HMAC
void sha256_hasher_init_hmac(sha256_hasher_t hasher, const uint8_t * key, size_t key_len)
{
	int i;
	memset(hasher->hmac_key_buffer, 0, SHA256_BLOCK_LEN);

	if(key_len > SHA256_BLOCK_LEN)
	{
		sha256_hasher_init(hasher);
		while(key_len--)
		{
			sha256_hasher_putc(hasher, *key++);
		}
		memcpy(hasher->hmac_key_buffer, 
				sha256_hasher_gethash(hasher),
				SHA256_HASH_LEN);
	}
	else
	{
		memcpy(hasher->hmac_key_buffer, key, key_len);
	}
	sha256_hasher_init(hasher);
	for(i = 0; i < SHA256_BLOCK_LEN; i++)
	{
		sha256_hasher_putc(hasher, hasher->hmac_key_buffer[i] ^ SHA256_HMAC_IPAD);
	}

}
uint8_t * sha256_hasher_gethmac(sha256_hasher_t hasher)
{
	int i;
	memcpy(hasher->hmac_inner_hash, sha256_hasher_gethash(hasher),
			SHA256_HASH_LEN);
	sha256_hasher_init(hasher);

	for(i = 0; i < SHA256_BLOCK_LEN; i++)
	{
		sha256_hasher_putc(hasher, hasher->hmac_key_buffer[i] ^ SHA256_HMAC_OPAD);
	}
	for(i = 0; i < SHA256_HASH_LEN; i++)
	{
		sha256_hasher_putc(hasher, hasher->hmac_inner_hash[i]);
	}
	return sha256_hasher_gethash(hasher);
}
#endif
