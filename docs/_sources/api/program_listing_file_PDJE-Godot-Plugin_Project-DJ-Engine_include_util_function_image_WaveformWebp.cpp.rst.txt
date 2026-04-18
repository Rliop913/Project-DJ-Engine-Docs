
.. _program_listing_file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebp.cpp:

Program Listing for File WaveformWebp.cpp
=========================================

|exhale_lsh| :ref:`Return to documentation for file <file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebp.cpp>` (``PDJE-Godot-Plugin/Project-DJ-Engine/include/util/function/image/WaveformWebp.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #include "util/function/image/WaveformWebp.hpp"
   
   #include "util/function/image/WaveformWebpEncoder.hpp"
   
   namespace PDJE_UTIL::function::image {
   
   common::Result<WaveformWebpBatch>
   encode_waveform_webps(const EncodeWaveformWebpArgs &args,
                         function::EvalOptions         options)
   {
       return detail::WaveformWebpEncoder(args, options).Encode();
   }
   
   common::Result<WaveformWebpBatch>
   encode_waveform_webps(const EncodeWaveformWebpArgs     &args,
                         const EncodeWaveformWebpStftArgs &stft_args,
                         function::EvalOptions             options)
   {
       return detail::WaveformWebpEncoder(args, stft_args, options).Encode();
   }
   
   } // namespace PDJE_UTIL::function::image
