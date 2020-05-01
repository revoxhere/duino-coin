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

#ifndef Sha1_h
#define Sha1_h

#include <inttypes.h>
#include "Print.h"
#include "sha1/sha1.h"

#ifndef SHA1_DISABLE_WRAPPER
class Sha1Wrapper : public Print
{
	public:
		void init(void);
		uint8_t * result(void);
#ifdef SHA1_ENABLE_HMAC
		void initHmac(const uint8_t * secret, unsigned int secretLength);
		uint8_t * resultHmac(void);
#endif
		virtual size_t write(uint8_t);
		using Print::write;
	private:
		struct sha1_hasher_s _hasher;

};

extern Sha1Wrapper Sha1;
#endif

#endif

