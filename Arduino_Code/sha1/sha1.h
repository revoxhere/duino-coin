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

#ifndef SHA1_SHA1_H_
#define SHA1_SHA1_H_

#include "default.h"
#include "types.h"
#include "hash.h"
#include <stddef.h>
//#include <unistd.h>

#ifdef __AVR__
#define ssize_t long int
#endif

ssize_t sha1_hasher_write(sha1_hasher_t hasher, const void * buf, size_t count); 

#endif  

