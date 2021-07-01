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

#include "constants.h"

const uint32_t sha1_init_state[SHA1_HASH_LEN / 4] PROGMEM =
{
	0x67452301, 0xefcdab89, 0x98badcfe,
	0x10325476, 0xc3d2e1f0
};

const uint32_t sha1_constants[4] PROGMEM =
{
	0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xca62c1d6
};


