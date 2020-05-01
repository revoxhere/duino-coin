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

#include "sha256.h"

#ifndef SHA256_DISABLED
#ifndef SHA256_DISABLE_WRAPPER
void Sha256Wrapper::init(void)
{
	sha256_hasher_init(&_hasher);
}

#ifdef SHA256_ENABLE_HMAC
void Sha256Wrapper::initHmac(const uint8_t * secret, unsigned int secretLength)
{
	sha256_hasher_init_hmac(&_hasher, secret, secretLength);
}

uint8_t * Sha256Wrapper::resultHmac(void)
{
	return sha256_hasher_gethmac(&_hasher);
}
#endif


size_t Sha256Wrapper::write(uint8_t byte)
{
	if(sha256_hasher_putc(&_hasher, byte) == byte)
	{
		return 1;
	}
	return 0;
}

uint8_t * Sha256Wrapper::result(void)
{
	return sha256_hasher_gethash(&_hasher);
}

Sha256Wrapper Sha256;

#endif
#endif
