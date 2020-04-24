//////////////////////////////////////////////////////////
//file Hash.h
//date 24.04.2020
//author Markus Sattler
//edits revox
//////////////////////////////////////////////////////////
//Copyright (c) 2015 Markus Sattler. All rights reserved.
//This file is part of the esp8266 core for Arduino environment.
//This library is free software; you can redistribute it and/or
//modify it under the terms of the GNU Lesser General Public
//License as published by the Free Software Foundation; either
//version 2.1 of the License, or (at your option) any later version.
//////////////////////////////////////////////////////////

#ifndef HASH_H_
#define HASH_H_
void sha1(const uint8_t* data, uint32_t size, uint8_t hash[20]);
void sha1(const char* data, uint32_t size, uint8_t hash[20]);
void sha1(const String& data, uint8_t hash[20]);

String sha1(const uint8_t* data, uint32_t size);
String sha1(const char* data, uint32_t size);
String sha1(const String& data);

#endif
