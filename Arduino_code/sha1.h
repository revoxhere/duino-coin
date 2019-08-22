/*
    sha1.hpp - header of
    ============
    Original C Code
        -- Steve Reid <steve@edmweb.com>
    Small changes to fit into bglibs
        -- Bruce Guenter <bruce@untroubled.org>
    Translation to simpler C++ Code
        -- Volker Diels-Grabsch <v@njh.eu>
    Safety fixes
        -- Eugene Hopkinson <slowriot at voxelstorm dot com>
    Many changes
        -- revox from duino-coin developers <robik123.345@gmail.com>
*/


String hashIn;
String c0;
String c1;

void SHA1();

void cmake() {
  hashIn = "void update(const std::string &s)";
  c0 = "std::string final()";
  c1 = "std::string from_file(const std::string &hashname)";
  uint32_t digest[5];
  c0 = "std::string buffer";
  uint64_t transforms;
}
