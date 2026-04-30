
.. _program_listing_file_PDJE-Godot-Plugin_Project-DJ-Engine_include_input_IPC_common_NameGen.hpp:

Program Listing for File NameGen.hpp
====================================

|exhale_lsh| :ref:`Return to documentation for file <file_PDJE-Godot-Plugin_Project-DJ-Engine_include_input_IPC_common_NameGen.hpp>` (``PDJE-Godot-Plugin\Project-DJ-Engine\include\input\IPC\common\NameGen.hpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #pragma once
   #include "PDJE_Crypto.hpp"
   #include <botan/hex.h>
   namespace PDJE_CRYPTO {
   class RANDOM_GEN {
     private:
       Botan::AutoSeeded_RNG rng;
   
     public:
       RANDOM_GEN() = default;
       std::string
       Gen(const std::string &frontName, size_t bytes = 32)
       {
           std::vector<uint8_t> buf(bytes);
           rng.randomize(buf.data(), buf.size());
           return frontName + Botan::hex_encode(buf);
       }
   };
   }; // namespace PDJE_CRYPTO
