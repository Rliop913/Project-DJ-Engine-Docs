#!/bin/bash
git clone https://github.com/Rliop913/PDJE-Godot-Plugin.git

cd PDJE-Godot-Plugin/ || exit 1
rm -r Project-DJ-Engine/
git clone https://github.com/Rliop913/Project-DJ-Engine.git
cd .. || exit 1

echo "Wrapper branch: $(git -C PDJE-Godot-Plugin branch --show-current)"
echo "Wrapper commit: $(git -C PDJE-Godot-Plugin rev-parse HEAD)"
echo "Core branch: $(git -C PDJE-Godot-Plugin/Project-DJ-Engine branch --show-current)"
echo "Core commit: $(git -C PDJE-Godot-Plugin/Project-DJ-Engine rev-parse HEAD)"
python -m tools.docs_harness record-source-heads

if [ ! -f docs_harness/source_baseline.lock.json ]; then
  echo "No docs_harness/source_baseline.lock.json found."
  echo "Record the current documentation baseline with:"
  echo "  uv run docs-harness stamp-baseline"
fi
