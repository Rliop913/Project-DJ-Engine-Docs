
.. _program_listing_file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebpEncoder.hpp:

Program Listing for File WaveformWebpEncoder.hpp
================================================

|exhale_lsh| :ref:`Return to documentation for file <file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebpEncoder.hpp>` (``PDJE-Godot-Plugin/Project-DJ-Engine/include/util/function/image/WaveformWebpEncoder.hpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #pragma once
   
   #include "util/function/image/WaveformWebp.hpp"
   
   namespace PDJE_UTIL::function::image::detail {
   
   class WaveformWebpEncoder {
     public:
       WaveformWebpEncoder(const EncodeWaveformWebpArgs &args,
                           function::EvalOptions         options);
       WaveformWebpEncoder(const EncodeWaveformWebpArgs     &args,
                           const EncodeWaveformWebpStftArgs &stft_args,
                           function::EvalOptions             options);
   
       common::Result<WaveformWebpBatch>
       Encode() const;
   
     private:
       enum class Mode { Monochrome, Stft };
   
       const EncodeWaveformWebpArgs     &args_;
       const EncodeWaveformWebpStftArgs *stft_args_ = nullptr;
       function::EvalOptions             options_;
       Mode                              mode_ = Mode::Monochrome;
   };
   
   } // namespace PDJE_UTIL::function::image::detail
