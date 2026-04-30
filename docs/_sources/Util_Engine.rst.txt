Util_Engine
===========

This page documents the current utility surface that is backed by the source
tree in this repository. For this module, the hand-written source of truth is:

- `include/util/`
- `tests/unit/util/`
- `cmakes/src/UTIL/UTILsrc.cmake`

Generated API pages under :doc:`/api/api_root` remain useful for symbol lookup,
but this guide is the recommended starting point for the maintained utility
surface and the intended consumption boundaries.

How to read the examples:

- C++ snippets show the core call shape and the expected `Result<T>` or
  `Status` checks; they are not full standalone sample projects.
- Godot snippets use the wrapper class and method names exactly as bound by the
  extension layer.
- Paths, model files, PCM buffers, and cache directories are placeholders that
  must be replaced with checkout- or application-specific values.

Public Consumption Units
------------------------

The current CMake targets split the utility layer into four consumer-facing
units:

- `PDJE_UTIL`
  base interface target for the utility include tree and the umbrella header
  path, including the maintained AI/ONNX Runtime utility implementation
- `PDJE_UTIL_DB`
  aggregate database target that wires the SQLite, RocksDB, and Annoy utility
  backends
- `PDJE_UTIL_IMAGE_WEBP`
  image/WebP helper target for the generic WebP writer path
- `PDJE_UTIL_IMAGE_WAVEFORM`
  waveform image generation target that also compiles the STFT and backend
  loader implementation files

In other words, the utility layer is not roadmap-only. It is active code with
headers, tests, and CMake consumption points in the current tree.

Header Boundaries
-----------------

The utility surface is intentionally split between one umbrella header and a
few direct-include headers.

Umbrella header:

.. code-block:: c++

   #include "util/PDJE_Util.hpp"

This re-exports the currently maintained:

- `PDJE_UTIL::common::{StatusCode, Status, Result<T>, Result<void>}`
- database wrapper types and backend concepts
- `db::Database<Backend>` as the key-value convenience alias
- `PDJE_UTIL::function::{clamp, slugify, EvalOptions, CacheContext}`

Direct include headers still required for APIs that are not re-exported by the
umbrella header:

- `util/function/image/WebpWriter.hpp`
- `util/function/image/WaveformWebp.hpp`
- `util/function/stft/STFT_Parallel.hpp`
- `util/ai/AI.hpp`
- `util/ai/beat_this/BeatThis.hpp`
- `util/common/BackendLoader/OpenCL_Loader.hpp`
- `util/common/BackendLoader/PDJE_Parallel_Runtime_Loader.hpp`

Common Status And Result Types
------------------------------

The utility module uses one error transport pattern everywhere: `StatusCode`,
`Status`, and `Result<T>`.

.. doxygenfile:: include/util/common/StatusCode.hpp
   :project: Project_DJ_Engine

.. doxygenfile:: include/util/common/Status.hpp
   :project: Project_DJ_Engine

.. doxygenfile:: include/util/common/Result.hpp
   :project: Project_DJ_Engine

Current facts from the headers and tests:

- `StatusCode` is the shared error taxonomy for utility APIs
- `Status` stores `code` plus a human-readable `message`
- `Status::ok()` is true only when `code == StatusCode::ok`
- `Result<T>` stores either a value plus ok status, or a failure status
- `Result<void>` keeps the same success/failure contract without a value

The header set and util status tests currently define and reference codes such
as:

- `invalid_argument`
- `not_found`
- `type_mismatch`
- `unsupported`
- `io_error`
- `closed`
- `backend_error`
- `out_of_range`
- `internal_error`

Typical usage checks the status before consuming the value:

.. code-block:: c++

   #include "util/PDJE_Util.hpp"

   using namespace PDJE_UTIL;

   auto clamped = function::clamp(
       { .value = 2.5, .min_value = 0.0, .max_value = 1.0 });
   if (!clamped.ok()) {
       std::cerr << clamped.status().message << std::endl;
       return;
   }

   std::cout << clamped.value() << std::endl;

The same status pattern applies to `Result<void>`:

.. code-block:: c++

   #include "util/PDJE_Util.hpp"

   PDJE_UTIL::common::Result<void> stored =
       PDJE_UTIL::common::Result<void>::success();

   if (!stored.ok()) {
       const auto &status = stored.status();
       std::cerr << "utility operation failed: "
                 << status.message << std::endl;
   }

Database Wrappers
-----------------

The current utility DB layer is organized by access pattern, not by one global
database class.

Wrapper split:

.. list-table::
   :header-rows: 1
   :widths: 28 32 40

   * - Wrapper
     - Typical backend
     - Current role
   * - `db::Database<Backend>`
     - key-value backend
     - convenience alias for `db::keyvalue::KeyValueDatabase<Backend>`
   * - `db::keyvalue::KeyValueDatabase<Backend>`
     - `db::backends::RocksDbBackend`
     - text/blob lookup, overwrite, erase, prefix scan
   * - `db::relational::RelationalDatabase<Backend>`
     - `db::backends::SqliteBackend`
     - SQL execution, queries, transactions
   * - `db::nearest::NearestNeighborIndex<Backend>`
     - `db::backends::AnnoyBackend`
     - embedding storage and nearest-neighbor search

All three wrapper families follow the same high-level lifecycle:

- `create(config)`
- `open(config)`
- use the opened object
- `close()`
- optionally `destroy(config)`

The shipped tests validate concrete behavior rather than only type presence:

- RocksDB key-value:
  text writes, byte writes, overwrite, prefix `list_keys()`, erase, read-only
  rejection, and type mismatch reporting
- SQLite relational:
  execute/query, parameter binding, blob transport, transaction rollback and
  commit, and read-only rejection
- Annoy nearest-neighbor:
  upsert, get, search, erase, reopen/persistence, read-only rejection, and
  invalid embedding dimension handling

RocksDB key-value example:

.. code-block:: c++

   #include "util/db/backends/RocksDbBackend.hpp"
   #include "util/db/keyvalue/Database.hpp"

   using Db = PDJE_UTIL::db::keyvalue::KeyValueDatabase<
       PDJE_UTIL::db::backends::RocksDbBackend>;

   PDJE_UTIL::db::backends::RocksDbConfig cfg{
       .path = "tmp/example-rocks",
       .open_options = { .create_if_missing = true }
   };

   auto opened = Db::open(cfg);
   if (!opened.ok()) {
       std::cerr << opened.status().message << std::endl;
       return;
   }

   auto db = std::move(opened.value());
   auto stored = db.put_text("artist", "RLIOP913");
   if (!stored.ok()) {
       std::cerr << stored.status().message << std::endl;
       return;
   }

   auto artist = db.get_text("artist");
   if (artist.ok()) {
       std::cout << artist.value() << std::endl;
   } else {
       std::cerr << artist.status().message << std::endl;
   }

SQLite relational example:

.. code-block:: c++

   #include "util/db/backends/SqliteBackend.hpp"
   #include "util/db/relational/Database.hpp"

   using Db = PDJE_UTIL::db::relational::RelationalDatabase<
       PDJE_UTIL::db::backends::SqliteBackend>;

   PDJE_UTIL::db::backends::SqliteConfig cfg{
       .path = "tmp/example.sqlite3",
       .open_options = { .create_if_missing = true }
   };

   auto opened = Db::open(cfg);
   if (!opened.ok()) {
       std::cerr << opened.status().message << std::endl;
       return;
   }

   auto db = std::move(opened.value());
   (void)db.execute(
       "CREATE TABLE IF NOT EXISTS notes("
       "id INTEGER PRIMARY KEY, lane TEXT NOT NULL);");
   (void)db.begin_transaction();
   (void)db.execute("INSERT INTO notes(id, lane) VALUES(?1, ?2);",
                    { PDJE_UTIL::db::relational::Value{ std::int64_t{1} },
                      PDJE_UTIL::db::relational::Value{ PDJE_UTIL::db::Text{"left"} } });
   (void)db.commit();

   auto rows = db.query("SELECT lane FROM notes WHERE id = ?1;",
                        { PDJE_UTIL::db::relational::Value{ std::int64_t{1} } });
   if (rows.ok() && !rows.value().rows.empty()) {
       const auto *lane = rows.value().rows.front().find("lane");
       if (lane != nullptr) {
           std::cout << std::get<PDJE_UTIL::db::Text>(lane->storage)
                     << std::endl;
       }
   }

Annoy nearest-neighbor follows the same open/use/close shape, but its payloads
are `db::nearest::Item`, `SearchHit`, and `SearchOptions` rather than text or
SQL values.

Annoy nearest-neighbor example:

.. code-block:: c++

   #include "util/db/backends/AnnoyBackend.hpp"
   #include "util/db/nearest/Index.hpp"

   using Index = PDJE_UTIL::db::nearest::NearestNeighborIndex<
       PDJE_UTIL::db::backends::AnnoyBackend>;

   PDJE_UTIL::db::backends::AnnoyConfig cfg{
       .root_path = "tmp/example-annoy",
       .open_options = { .create_if_missing = true },
       .dimension = 3,
       .trees = 10
   };

   auto opened = Index::open(cfg);
   if (!opened.ok()) {
       std::cerr << opened.status().message << std::endl;
       return;
   }

   auto index = std::move(opened.value());
   (void)index.upsert_item(
       { .id = "track-a",
         .embedding = { 0.9f, 0.1f, 0.0f },
         .text_payload = PDJE_UTIL::db::Text{ "high-energy intro" } });

   const std::vector<float> query{ 1.0f, 0.0f, 0.0f };
   auto hits = index.search(query, { .limit = 3, .search_k = -1 });
   if (hits.ok()) {
       for (const auto &hit : hits.value()) {
           std::cout << hit.id << " distance=" << hit.distance << std::endl;
       }
   }

Godot DB wrapper examples:

.. code-block:: gdscript

   var kv := PDJE_KeyValueDB.new()
   if kv.Open("user://pdje-cache/kv", true):
       kv.PutText("artist", "RLIOP913")
       print(kv.GetText("artist"))
       kv.Close()

.. code-block:: gdscript

   var sql := PDJE_RelationalDB.new()
   if sql.Open("user://pdje-cache/library.sqlite3", true):
       sql.Execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER, lane TEXT)")
       sql.Execute("INSERT INTO notes(id, lane) VALUES(?1, ?2)", [1, "left"])
       for row in sql.Query("SELECT lane FROM notes WHERE id = ?1", [1]):
           print(row.values)
       sql.Close()

.. code-block:: gdscript

   var vectors := PDJE_VectorDB.new()
   if vectors.Open("user://pdje-cache/vectors", 3, 10, false, true):
       var item := PDJE_VectorItem.new()
       item.id = "track-a"
       item.embedding = PackedFloat32Array([0.9, 0.1, 0.0])
       item.text_payload = "high-energy intro"
       vectors.UpsertItem(item)

       for hit in vectors.Search(PackedFloat32Array([1.0, 0.0, 0.0]), 3):
           print(hit.id, " ", hit.distance)
       vectors.Close()

Function Helpers
----------------

The function layer currently splits into small inline helpers plus larger image
and signal-processing utilities.

Scalar And Text
~~~~~~~~~~~~~~~

`PDJE_UTIL::function::clamp` and `slugify` are the smallest maintained public
helpers.

- `clamp(ClampArgs)` clamps a floating-point value and returns
  `Result<double>`
- `slugify(SlugifyArgs, EvalOptions)` normalizes text into a delimiter-based
  slug and rejects alphanumeric separators
- `EvalOptions` currently carries an optional `CacheContext*`
- `CacheContext` exists as a lightweight movable handle; the shipped inline
  helpers shown here do not require a populated cache context

Clamp and slug examples:

.. code-block:: c++

   #include "util/PDJE_Util.hpp"

   auto gain = PDJE_UTIL::function::clamp(
       { .value = 1.35, .min_value = 0.0, .max_value = 1.0 });
   if (gain.ok()) {
       std::cout << "normalized gain: " << gain.value() << std::endl;
   }

   auto slug = PDJE_UTIL::function::slugify(
       { .input = "Project DJ Engine", .separator = '-' });
   if (slug.ok()) {
       std::cout << slug.value() << std::endl; // "project-dj-engine"
   }

   auto invalid = PDJE_UTIL::function::slugify(
       { .input = "Project DJ Engine", .separator = 'x' });
   if (!invalid.ok()) {
       std::cerr << invalid.status().message << std::endl;
   }

Image Helpers
~~~~~~~~~~~~~

The image surface is split into a generic WebP writer path and a waveform
generator path.

Generic WebP writer:

.. code-block:: c++

   #include "util/function/image/WebpWriter.hpp"

Current public types in that header:

- `RasterPixelFormat`
- `RasterImageView`
- `EncodeWebpArgs`
- `WriteWebpArgs`
- `encode_webp(...)`
- `write_webp(...)`

Current source-backed behavior:

- validates image dimensions, stride, and buffer layout
- accepts `gray8`, `gray_alpha8`, `rgb8`, and `rgba8` raster views
- returns encoded WebP bytes from `encode_webp(...)`
- writes encoded bytes to disk with `write_webp(...)`
- validates `compression_level` in the `[-1, 9]` range before encoding

Encode and write example:

.. code-block:: c++

   #include "util/function/image/WebpWriter.hpp"

   const std::vector<std::uint8_t> rgba{ 255, 0, 0, 255 };

   auto encoded = PDJE_UTIL::function::image::encode_webp(
       { .image =
             {
                 .pixels = rgba,
                 .width = 1,
                 .height = 1,
                 .stride = 0,
                 .pixel_format = PDJE_UTIL::function::image::RasterPixelFormat::rgba8,
             } });

   if (!encoded.ok()) {
       std::cerr << encoded.status().message << std::endl;
       return;
   }

   auto written = PDJE_UTIL::function::image::write_webp(
       { .image =
             {
                 .pixels = rgba,
                 .width = 1,
                 .height = 1,
                 .stride = 0,
                 .pixel_format = PDJE_UTIL::function::image::RasterPixelFormat::rgba8,
             },
         .output_path = "tmp/red-pixel.webp",
         .compression_level = 1 });
   if (!written.ok()) {
       std::cerr << written.status().message << std::endl;
   }

Waveform WebP generation:

.. code-block:: c++

   #include "util/function/image/WaveformWebp.hpp"

Current public types in that header:

- `EncodedWebpBytes`
- `ChannelWaveformWebps`
- `WaveformWebpBatch`
- `EncodeWaveformWebpArgs`
- `encode_waveform_webps(...)`

Current source-backed behavior and tests cover:

- argument validation
- interleaved PCM channel splitting
- min/max aggregation per output column
- incomplete chunk padding
- transparent background output
- deterministic output across single-worker, multi-worker, and auto-worker
  runs

Example:

.. code-block:: c++

   #include "util/function/image/WaveformWebp.hpp"

   std::vector<float> pcm{
       1.0f, -1.0f, 0.25f, -0.25f,
       -0.5f, 0.5f, 0.75f, -0.75f
   };

   auto waveform = PDJE_UTIL::function::image::encode_waveform_webps(
       { .pcm = pcm,
         .channel_count = 2,
         .y_pixels = 64,
         .pcm_per_pixel = 256,
         .x_pixels_per_image = 512,
         .compression_level = 1,
         .worker_thread_count = 0 });

   if (!waveform.ok()) {
       return;
   }

   const auto &batch = waveform.value();
   // batch[channel][image] -> encoded WebP bytes
   for (std::size_t channel = 0; channel < batch.size(); ++channel) {
       for (std::size_t image = 0; image < batch[channel].size(); ++image) {
           std::cout << "channel " << channel
                     << ", image " << image
                     << ", bytes " << batch[channel][image].size()
                     << std::endl;
       }
   }

Signal / STFT Helpers
~~~~~~~~~~~~~~~~~~~~~

The maintained STFT surface lives outside `util/PDJE_Util.hpp` and requires a
direct include:

.. code-block:: c++

   #include "util/function/stft/STFT_Parallel.hpp"

The current public interfaces are:

- `PDJE_PARALLEL::BACKEND_T`
- `PDJE_PARALLEL::Backend`
- `PDJE_PARALLEL::STFT`
- `PDJE_PARALLEL::WINDOW_LIST`
- `PDJE_PARALLEL::POST_PROCESS`

The current runtime model from the source tree is:

- `STFT` always constructs a serial backend
- `STFT` calls `Backend::LoadBackend()` and then reads the selected
  `BACKEND_T` through `PrintBackendType()`
- if OpenCL loads successfully, `STFT` tries to construct `OPENCL_STFT`
- if OpenCL startup or execution fails, `STFT` falls back to `SERIAL`
- the current backend loader switches between `OPENCL` and `SERIAL`
- `BACKEND_T::METAL` exists in the enum, but the shipped runtime loader does
  not currently select it

`POST_PROCESS` is the main post-chain contract:

- `to_bin`
- `toPower`
- `mel_scale`
- `to_db`
- `normalize_min_max`
- `to_rgb`

`POST_PROCESS::check_values()` currently applies the chain rules used by the
implementation:

- `to_rgb` implies `normalize_min_max` and `mel_scale`
- `mel_scale` implies `to_bin` and `toPower`

The util tests currently validate:

- serial backend stability across repeated calls
- switching across cached FFT sizes
- mel filter bank generation
- mel, mel+db, and RGB reduction paths
- OpenCL runtime shim caching and backend selection
- CMRC resource packaging for `STFT_MAIN.cl`

Example:

.. code-block:: c++

   #include "util/function/stft/STFT_Parallel.hpp"

   std::vector<float> pcm(512, 0.0f);

   PDJE_PARALLEL::STFT stft;
   PDJE_PARALLEL::POST_PROCESS post;
   post.mel_scale = true;
   post.to_db = true;
   post.check_values();

   auto [real_out, imag_out] = stft.calculate(
       pcm,
       PDJE_PARALLEL::WINDOW_LIST::HANNING,
       10,
       0.5f,
       post);

   if (!real_out.empty()) {
       std::cout << "first bin: " << real_out.front() << std::endl;
   }

Godot MIR wrapper examples:

.. code-block:: gdscript

   var mir := PDJE_MIR.new()
   var pcm := PackedFloat32Array()
   pcm.resize(1024)

   var stft_frames := mir.STFT_PCM_DATA(
       pcm,
       1,
       PDJE_MIR.HANNING,
       10,
       0.5,
       true,
       true,
       true,
       true,
       true,
       true)
   for frame in stft_frames:
       print(frame.real.size(), " ", frame.imag.size())

.. code-block:: gdscript

   var mir := PDJE_MIR.new()
   var cache_db := PDJE_KeyValueDB.new()
   cache_db.Open("user://pdje-cache/waveforms", true)

   var images := mir.SoundToWaveform(
       $PDJE_Wrapper,
       cache_db,
       "music-title",
       "composer",
       128.0,
       256,
       4096,
       256)
   for webp_bytes in images:
       print(webp_bytes.size())

If you need to probe runtime availability directly, the loader entrypoint lives
in:

.. code-block:: c++

   #include "util/common/BackendLoader/OpenCL_Loader.hpp"

And the capability query is:

.. code-block:: c++

   bool ready = PDJE_PARALLEL::EnsureOpenCLRuntimeLoaded();

AI Namespace
------------

`PDJE_UTIL::ai` is an active utility surface in the current source tree. It
owns a small generic ONNX Runtime facade and the Beat This beat/downbeat
detection pipeline used by the wrapper layer.

The stable public headers are direct includes:

.. code-block:: c++

   #include "util/ai/AI.hpp"
   #include "util/ai/beat_this/BeatThis.hpp"

The generic ONNX Runtime facade is intentionally small:

- `OnnxSessionOptions`
  controls thread counts and graph optimization level.
- `FloatTensor`
  carries a dense float tensor as `shape` plus flattened `values`.
- `NamedFloatTensor`
  pairs a model input or output name with a `FloatTensor`.
- `OnnxSession`
  owns an ONNX Runtime session, exposes model input/output names, and runs
  named float tensors through the loaded model.

This generic tensor/session API is a native utility surface. It is not exposed
directly as the current Godot-facing API.

Native ONNX session shape:

.. code-block:: c++

   #include <array>
   #include "util/ai/AI.hpp"

   PDJE_UTIL::ai::OnnxSession session(
       "path/to/model.onnx",
       { .intra_op_num_threads = 1,
         .inter_op_num_threads = 1,
         .optimization_level =
             PDJE_UTIL::ai::OnnxOptimizationLevel::EXTENDED });

   PDJE_UTIL::ai::NamedFloatTensor input{
       .name = session.input_name(0),
       .tensor =
           {
               .shape = { 1, 4 },
               .values = { 0.0f, 0.25f, 0.5f, 1.0f },
           },
   };

   std::array<PDJE_UTIL::ai::NamedFloatTensor, 1> inputs{ input };
   auto outputs = session.run(inputs);
   for (const auto &output : outputs) {
       std::cout << output.name
                 << " values=" << output.tensor.values.size()
                 << std::endl;
   }

Beat This Detection
~~~~~~~~~~~~~~~~~~~

Beat This is exposed through the native convenience type
`PDJE_UTIL::ai::BeatThisDetector`.

Current public types:

- `BeatThisFrontendConfig`
  configures the frontend sample rate, FFT size, hop length, mel-bin count,
  padding, mel range, mel formula, normalization, and window function.
- `BeatDetectionResult`
  returns sorted beat and downbeat timestamps in seconds.
- `BeatThisDetector`
  owns the configured model/session/frontend pipeline and runs detection from
  mono PCM.

The source-backed flow is:

1. accept mono PCM samples plus the input sample rate
2. resample and prepare the waveform for the Beat This frontend
3. compute a log-mel spectrogram with the PDJE STFT/mel helpers
4. run ONNX inference against the Beat This model
5. post-process logits into beat and downbeat timestamps

Minimal native shape:

.. code-block:: c++

   #include "util/ai/beat_this/BeatThis.hpp"

   std::vector<float> mono_pcm = /* mono samples */;
   PDJE_UTIL::ai::BeatThisDetector detector("path/to/model.onnx");
   auto result = detector.detect(mono_pcm, 44100);

   // result.beats and result.downbeats are timestamps in seconds.
   for (double beat_seconds : result.beats) {
       std::cout << beat_seconds << std::endl;
   }

The default native detector constructor uses the build-configured Beat This
model path when one is available. Do not describe model packaging or runtime
deployment as universal; verify the current checkout and build configuration
before making distribution claims.

Godot Wrapper Surface
~~~~~~~~~~~~~~~~~~~~~

The Godot wrapper exposes Beat This through wrapper-owned Godot classes:

- `PDJE_AI`
  a `Node` facade with `CreateBeatThisDetector(model_path)`.
- `PDJE_BeatThisDetector`
  a `RefCounted` handle that owns a native
  `PDJE_UTIL::ai::BeatThisDetector`.
- `PDJE_BeatThisResult`
  a `RefCounted` result object with `beats` and `downbeats`
  `PackedFloat64Array` properties.

Wrapper initialization validates that the model path is non-empty, exists,
points to a regular file, and has the `.onnx` extension before constructing the
native detector.

`PDJE_BeatThisDetector.DetectPCM(pcm, channel_count, sample_rate)` accepts
interleaved `PackedFloat32Array` audio, validates the channel count, sample
rate, and frame alignment, downmixes the input to mono, and returns beat and
downbeat timestamps in seconds.

`PDJE_BeatThisDetector.DetectMusic(core_api, music_title, composer, bpm)` follows
the existing MIR-style wrapper route: it requires an initialized
`PDJE_Wrapper`, searches music through the core engine, requests mono PCM from
the matched music data, and runs Beat This against the core decoder sample
rate.

The wrapper reports failures with null `Ref<PDJE_BeatThisResult>` values plus
method-level diagnostic errors. It does not expose raw ONNX Runtime sessions,
tensors, or model IO to Godot scripts.

Godot AI wrapper examples:

.. code-block:: gdscript

   var ai := PDJE_AI.new()
   var detector := ai.CreateBeatThisDetector("res://models/beat_this.onnx")
   if detector == null:
       return

   var interleaved_pcm := PackedFloat32Array()
   interleaved_pcm.resize(44100)
   var result := detector.DetectPCM(interleaved_pcm, 1, 44100)
   if result != null:
       print(result.beats)
       print(result.downbeats)

.. code-block:: gdscript

   var ai := PDJE_AI.new()
   var detector := ai.CreateBeatThisDetector("res://models/beat_this.onnx")
   if detector == null:
       return

   var result := detector.DetectMusic(
       $PDJE_Wrapper,
       "music-title",
       "composer",
       128.0)
   if result != null:
       for downbeat in result.downbeats:
           print(downbeat)
