
.. _program_listing_file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebpEncoder.cpp:

Program Listing for File WaveformWebpEncoder.cpp
================================================

|exhale_lsh| :ref:`Return to documentation for file <file_PDJE-Godot-Plugin_Project-DJ-Engine_include_util_function_image_WaveformWebpEncoder.cpp>` (``PDJE-Godot-Plugin\Project-DJ-Engine\include\util\function\image\WaveformWebpEncoder.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #include "util/function/image/WaveformWebpEncoder.hpp"
   
   #include "util/function/image/WaveformWebpPlanBuilder.hpp"
   #include "util/function/image/WaveformWebpProcessor.hpp"
   #include "util/function/image/WaveformWebpWorkerRunner.hpp"
   
   namespace PDJE_UTIL::function::image::detail {
   
   WaveformWebpEncoder::WaveformWebpEncoder(const EncodeWaveformWebpArgs &args,
                                            function::EvalOptions         options)
       : args_(args), options_(options), mode_(Mode::Monochrome)
   {
   }
   
   WaveformWebpEncoder::WaveformWebpEncoder(
       const EncodeWaveformWebpArgs     &args,
       const EncodeWaveformWebpStftArgs &stft_args,
       function::EvalOptions             options)
       : args_(args), stft_args_(&stft_args), options_(options), mode_(Mode::Stft)
   {
   }
   
   common::Result<WaveformWebpBatch>
   WaveformWebpEncoder::Encode() const
   {
       auto plan = WaveformPlanBuilder(args_, stft_args_).Build();
       if (!plan.ok()) {
           return common::Result<WaveformWebpBatch>::failure(plan.status());
       }
   
       auto built_plan = std::move(plan).value();
       auto runner = WaveformWorkerRunner(args_.worker_thread_count);
   
       if (mode_ == Mode::Stft && stft_args_ != nullptr) {
           return runner.Run(
               built_plan,
               [&]() {
                   return WaveformJobProcessor<StftColorMapper>(
                       args_,
                       built_plan.buffer_sizes,
                       options_,
                       args_,
                       *stft_args_,
                       built_plan.buffer_sizes,
                       built_plan.chunk_sample_count);
               });
       }
   
       return runner.Run(
           built_plan,
           [&]() {
               return WaveformJobProcessor<MonochromeColorMapper>(
                   args_,
                   built_plan.buffer_sizes,
                   options_);
           });
   }
   
   } // namespace PDJE_UTIL::function::image::detail
