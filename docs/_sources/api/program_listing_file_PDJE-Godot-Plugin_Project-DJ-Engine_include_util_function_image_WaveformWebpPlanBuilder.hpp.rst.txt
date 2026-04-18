
.. _program_listing_file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebpPlanBuilder.hpp:

Program Listing for File WaveformWebpPlanBuilder.hpp
====================================================

|exhale_lsh| :ref:`Return to documentation for file <file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebpPlanBuilder.hpp>` (``PDJE-Godot-Plugin/Project-DJ-Engine/include/util/function/image/WaveformWebpPlanBuilder.hpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #pragma once
   
   #include "util/common/Result.hpp"
   #include "util/function/image/WaveformWebpInternal.hpp"
   
   namespace PDJE_UTIL::function::image::detail {
   
   class WaveformPlanBuilder {
     public:
       WaveformPlanBuilder(const EncodeWaveformWebpArgs     &args,
                           const EncodeWaveformWebpStftArgs *stft_args);
   
       common::Result<WaveformEncodePlan>
       Build() const;
   
     private:
       common::Result<void>
       Validate() const;
   
       common::Result<std::size_t>
       ComputeChunkSampleCount() const;
   
       common::Result<WaveformBufferSizes>
       ComputeBufferSizes() const;
   
       common::Result<std::vector<std::vector<float>>>
       SplitChannels(std::size_t chunk_sample_count) const;
   
       const EncodeWaveformWebpArgs     &args_;
       const EncodeWaveformWebpStftArgs *stft_args_ = nullptr;
   };
   
   } // namespace PDJE_UTIL::function::image::detail
