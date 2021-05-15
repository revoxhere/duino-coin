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

#include "sha1.h"

#ifndef SHA1_DISABLED
#ifndef SHA1_DISABLE_WRAPPER
void Sha1Wrapper::init(void)
{
	sha1_hasher_init(&_hasher);
}

#ifdef SHA1_ENABLE_HMAC
void Sha1Wrapper::initHmac(const uint8_t * secret, uint16_t secretLength)
{
	sha1_hasher_init_hmac(&_hasher, secret, secretLength);
}

uint8_t * Sha1Wrapper::resultHmac(void)
{
	return sha1_hasher_gethmac(&_hasher);
}
#endif


size_t Sha1Wrapper::write(uint8_t byte)
{
	if(sha1_hasher_putc(&_hasher, byte) == byte)
	{
		return 1;
	}
	return 0;
}

uint8_t * Sha1Wrapper::result(void)
{
	return sha1_hasher_gethash(&_hasher);
}

Sha1Wrapper Sha1;

#endif
#endif
