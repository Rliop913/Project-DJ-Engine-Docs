
.. _program_listing_file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebpInternal.hpp:

Program Listing for File WaveformWebpInternal.hpp
=================================================

|exhale_lsh| :ref:`Return to documentation for file <file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebpInternal.hpp>` (``PDJE-Godot-Plugin/Project-DJ-Engine/include/util/function/image/WaveformWebpInternal.hpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #pragma once
   
   #include "util/function/image/WaveformWebp.hpp"
   
   #include <cstddef>
   #include <cstdint>
   #include <vector>
   
   namespace PDJE_UTIL::function::image::detail {
   
   struct WaveformJob {
       const float      *samples       = nullptr;
       std::size_t       sample_count  = 0;
       std::size_t       channel_index = 0;
       std::size_t       image_index   = 0;
       EncodedWebpBytes *output_slot   = nullptr;
   };
   
   struct WaveformBufferSizes {
       std::size_t row_stride            = 0;
       std::size_t image_byte_count      = 0;
       std::size_t column_rgb_byte_count = 0;
   };
   
   struct WaveformWorkerContext {
       std::vector<float>        column_mins;
       std::vector<float>        column_maxs;
       std::vector<std::uint8_t> rgba;
   
       WaveformWorkerContext(std::size_t x_pixels_per_image,
                             std::size_t image_byte_count)
           : column_mins(x_pixels_per_image, 0.0f),
             column_maxs(x_pixels_per_image, 0.0f),
             rgba(image_byte_count, 0)
       {
       }
   };
   
   struct WaveformEncodePlan {
       std::vector<std::vector<float>> channels;
       WaveformWebpBatch               batch;
       std::vector<WaveformJob>        jobs;
       std::size_t                     chunk_sample_count = 0;
       WaveformBufferSizes             buffer_sizes      = {};
   };
   
   } // namespace PDJE_UTIL::function::image::detail
