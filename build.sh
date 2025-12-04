#!/usr/bin/env bash

set -e
set -u
#set -x
set -o pipefail

echo "--- 🛠️ Running Code Proof Pipeline ---"

poetry run ruff format --check
echo "✅ Formatting check passed."

poetry run ruff check .
echo "✅ Linting check passed."

poetry run mypy src/
echo "✅ Type check passed."

CHARACTERS=("beavis" "cheese" "cow" "daemon" "dragon" "fox" "ghostbusters" "kitty" "meow" "miki" "milk" "octopus" "pig" "stegosaurus" "stimpy" "trex" "turkey" "turtle" "tux")

RANDOM_CHARACTER=${CHARACTERS[$RANDOM % ${#CHARACTERS[@]}]}

COMMIT_HASH=$(git rev-parse HEAD 2>/dev/null || echo "N/A")

poetry run cowsay -c "$RANDOM_CHARACTER" --text "$COMMIT_HASH"
