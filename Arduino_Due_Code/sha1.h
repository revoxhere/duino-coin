#ifndef Sha1_h
#define Sha1_h

#include "sha1_config.h"

#if defined(SHA1_LINUX)
class Sha1Class
#else
class Sha1Class : public Print
#endif
{
  public:
	union _buffer {
		uint8_t b[BLOCK_LENGTH];
		uint32_t w[BLOCK_LENGTH/4];
	};
	union _state {
		uint8_t b[HASH_LENGTH];
		uint32_t w[HASH_LENGTH/4];
	};
	/** Initialized the SHA1 process
	 *  Set the counter and buffers
	 */
    void init(void);
	/** initializes the HMAC process for SHA-1
	 *
	 * @param secret The key to be used
	 * @param secretLength The length of the key
	 */
    void initHmac(const uint8_t* secret, int secretLength);
	
	/** Pads the last block and finalizes the hash. 
	 * 
	 * @return returns the hash
	 */
	uint8_t* result(void);
	
	/** Pads the last block and finalizes the hash. 
	 * 
	 * @return returns the hash
	 */
    uint8_t* resultHmac(void);
    #if  defined(SHA1_LINUX)
	/**
	 * Adds data to the buffer.
	 * Also increases the byteCount variable
	 *
	 */
	virtual size_t write(uint8_t);
	
	/**
	 * Adds the str to the buffer
	 * Calles function in order to add the data into the buffer.
	 * @param str The string to be added
	 * @note Print class does not exist in linux, so we define it here using
	 * @code #if defined(SHA1_LINUX) @endcode
	 *
	 */
	size_t write_L(const char *str);
	
	/**
	 * Adds the string to the buffer
	 * Calles function in order to add the data into the buffer.
	 * @param *buffer The string to be added
	 * @param *size The size of the string
	 * @note Print class does not exist in linux, so we define it here using
	 * @code #if defined(SHA1_LINUX) @endcode
	 *
	 */
	size_t write_L(const uint8_t *buffer, size_t size);
	
	/**
	 * Adds the str to the buffer
	 * Calles functions in order to add the data into the buffer.
	 * @param str The string to be added
	 * @note Print class does not exist in linux, so we define it here using
	 * @code #if defined(SHA1_LINUX) @endcode
	 *
	 */
	size_t print(const char* str);
	
	/**
	 * used in linux in order to retrieve the time in milliseconds.
	 *
	 * @return returns the milliseconds in a double format.
	 */
	double millis();
    #else
	/**
	 * Adds data to the buffer.
	 * Also increases the byteCount variable
	 *
	 */
	virtual size_t write(uint8_t);
	using Print::write;
    #endif
  private:
	/** Implement SHA-1 padding (fips180-2 ยง5.1.1).
	 *  Pad with 0x80 followed by 0x00 until the end of the block
	 *
	 */
    void pad();
	
	/** adds the data to the buffer
	 * 
	 * @param data 
	 *
	 */
    void addUncounted(uint8_t data);
	
	/** Hash a single block of data
	 *
	 */
    void hashBlock();
	
	/**
     * rol32 - rotate a 32-bit value left
     * @param number value to rotate
     * @param bits bits to roll
     */
    uint32_t rol32(uint32_t number, uint8_t bits);
    _buffer buffer;/**< hold the buffer for the hashing process */
    uint8_t bufferOffset;/**< indicates the position on the buffer */
    _state state;/**< identical structure with buffer */
    uint32_t byteCount;/**< Byte counter in order to initialize the hash process for a block */
    uint8_t keyBuffer[BLOCK_LENGTH];/**< Hold the key for the HMAC process*/
    uint8_t innerHash[HASH_LENGTH];/**< holds the inner hash for the HMAC process */
    #if defined(SHA1_LINUX)
		timeval tv;/**< hold the time value on linux machines (ex Raspberry Pi) */
    #endif
    
};
extern Sha1Class Sha1;

#endif

 /**
 * @example sha1test.pde
 * <b>For Arduino</b><br>
 * <b>Updated: spaniakos 2015 </b><br>
 *
 * This is an example of how to use SHA1 hashing and HMAC SHA-1 HMAC of this SHA library.<br />
 * The text and keys can be either in HEX or String format.<br />
 * The examples are from the FIPS 180-2 , RFC3174 and FIPS 198a<br />
 * <br />
 * to use String key it must be in the form of : uint8_t *hmacKey2= (unsigned char*)"0123456789:;<=>?@ABC";
 */
 
 /**
 * @example sha1test.cpp
 * <b>For Rasberry pi</b><br>
 * <b>Updated: spaniakos 2015 </b><br>
 *
 * This is an example of how to use SHA1 hashing and HMAC SHA-1 HMAC of this SHA library.<br />
 * The text and keys can be either in HEX or String format.<br />
 * The examples are from the FIPS 180-2 , RFC3174 and FIPS 198a<br />
 * <br />
 * to use String key it must be in the form of : uint8_t *hmacKey2= (unsigned char*)"0123456789:;<=>?@ABC";
 */
 
 /**
 * @example sha256test.pde
 * <b>For Arduino</b><br>
 * <b>Updated: spaniakos 2015 </b><br>
 *
 * This is an example of how to use SHA256 of this SHA library.<br />
 * The text and keys can be either in HEX or String format.<br />
 * The examples are from the FIPS 180-2 and RFC4231<br />
 * <br />
 * to use String key it must be in the form of : uint8_t *hmacKey2= (unsigned char*)"0123456789:;<=>?@ABC";
 */
 
 /**
 * @example sha256test.cpp
 * <b>For Rasberry pi</b><br>
 * <b>Updated: spaniakos 2015 </b><br>
 *
 * This is an example of how to use SHA256 of this SHA library.<br />
 * The text and keys can be either in HEX or String format.<br />
 * The examples are from the FIPS 180-2 and RFC4231<br />
 * <br />
 * to use String key it must be in the form of : uint8_t *hmacKey2= (unsigned char*)"0123456789:;<=>?@ABC";
 */
 
  /**
 * @example hmacsha256test.pde
 * <b>For Arduino</b><br>
 * <b>Updated: spaniakos 2015 </b><br>
 *
 * This is an example of how to use HMAC-SHA256 of this SHA library.<br />
 * The text and keys can be either in HEX or String format.<br />
 * The examples are from the RFC4231<br />
 * <br />
 * to use String key it must be in the form of : uint8_t *hmacKey2= (unsigned char*)"0123456789:;<=>?@ABC";
 */
 
 /**
 * @example hmacsha256test.cpp
 * <b>For Rasberry pi</b><br>
 * <b>Updated: spaniakos 2015 </b><br>
 *
 * This is an example of how to use HMAC-SHA256 of this SHA library.<br />
 * The text and keys can be either in HEX or String format.<br />
 * The examples are from the RFC4231<br />
 * <br />
 * to use String key it must be in the form of : uint8_t *hmacKey2= (unsigned char*)"0123456789:;<=>?@ABC";
 */

/**
 * @mainpage SHA-1 / SHA-256 and HMAC-SHA1 / HMAC-SHA256
 *
 * @section Goals Design Goals
 *
 * This library is designed to be...
 * @li Fast and efficient
 * @li Able to effectively hash any size of string
 * @li Able to use any format of key for HMAC (hex or string)
 * @li Easy for the user to use in his programmes
 * @li to hash using SHA1 and SHA256
 * @li to hash using HMAC-SHA1 and HMAC-SHA256
 *
 * @section Acknowledgements Acknowledgements
 * This is an SHA library for the Arduino, based on bakercp's SHA library, which you can find <a href= "https://github.com/bakercp/Cryptosuite">here:</a>.<br />
 * Tzikis library was based on Cathedrow`s library, which you can find <a href="https://github.com/Cathedrow/arduino">here:</a><br /> 
 * 
 * @section Installation Installation
 * <h3>Arduino</h3>
 * Create a folder named _SHA_ in the _libraries_ folder inside your Arduino sketch folder. If the 
 * libraries folder doesn't exist, create it. Then copy everything inside. (re)launch the Arduino IDE.<br />
 * You're done. Time for a mojito
 * 
 * <h3>Raspberry  pi</h3>
 * <b>install</b><br /><br />
 * 
 * sudo make install<br />
 * cd examples_Rpi<br />
 * make<br /><br />
 * 
 * <b>What to do after changes to the library</b><br /><br />
 * sudo make clean<br />
 * sudo make install<br />
 * cd examples_Rpi<br />
 * make clean<br />
 * make<br /><br />
 * <b>What to do after changes to a sketch</b><br /><br />
 * cd examples_Rpi<br />
 * make <sketch><br /><br />
 * or <br />
 * make clean<br />
 * make<br /><br /><br />
 * <b>How to start a sketch</b><br /><br />
 * cd examples_Rpi<br />
 * sudo ./<sketch><br /><br />
 * 
 * @section News News
 *
 * If issues are discovered with the documentation, please report them <a href="https://github.com/spaniakos/spaniakos.github.io/issues"> here</a>
 * @section Useful Useful References
 *
 * Please refer to:
 *
 * @li <a href="http://spaniakos.github.io/Cryptosuite/classSha1Class.html"><b>SHA1</b> SHA1 / HMAC-SHA1 Class Documentation</a>
 * @li <a href="http://spaniakos.github.io/Cryptosuite/classSha256Class.html"><b>SHA256</b> SHA256 / HMAC-SHA256 Class Documentation</a>
 * @li <a href="https://github.com/spaniakos/Cryptosuite/archive/master.zip"><b>Download</b></a>
 * @li <a href="https://github.com/spaniakos/Cryptosuite/"><b>Source Code</b></a>
 * @li <a href="http://spaniakos.github.io/">All spaniakos Documentation Main Page</a>
 *
 * @section Board_Support Board Support
 *
 * Most standard Arduino based boards are supported:
 * - Arduino
 * - Intel Galileo support
 * - Raspberry Pi Support
 * 
 * - The library has not been tested to other boards, but it should suppport ATMega 328 based boards,Mega Boards,Arduino Due,ATTiny board
 */
