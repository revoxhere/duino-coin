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

#include "config.h"

#ifndef Sha256_h
#define Sha256_h

#include <inttypes.h>
#include "Print.h"
#include "sha256/sha256.h"

#ifndef SHA256_DISABLE_WRAPPER
class Sha256Wrapper : public Print
{
	public:
		void init(void);
		uint8_t * result(void);
#ifdef SHA256_ENABLE_HMAC
		void initHmac(const uint8_t * secret, unsigned int secretLength);
		uint8_t * resultHmac(void);
#endif
		virtual size_t write(uint8_t);
		using Print::write;
	private:
		struct sha256_hasher_s _hasher;

};

extern Sha256Wrapper Sha256;
#endif

#endif
