#!/bin/bash
cd PDJE-Godot-Plugin/ || exit 1
git pull origin master
cd Project-DJ-Engine || exit 1
git pull origin main
cd ../.. || exit 1

echo "Wrapper branch: $(git -C PDJE-Godot-Plugin branch --show-current)"
echo "Wrapper commit: $(git -C PDJE-Godot-Plugin rev-parse HEAD)"
echo "Core branch: $(git -C PDJE-Godot-Plugin/Project-DJ-Engine branch --show-current)"
echo "Core commit: $(git -C PDJE-Godot-Plugin/Project-DJ-Engine rev-parse HEAD)"
python -m tools.docs_harness record-source-heads
echo "Documentation baseline was not updated."
echo "Inspect pending source deltas with:"
echo "  uv run docs-harness diff-context --json"
