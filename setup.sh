#!/usr/bin/env bash

QUIET_FLAG="--quiet"
BREW_INSTALL_CMD="/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""

if ! command -v brew &>/dev/null; then
  echo "Homebrew is not installed."
  echo "To install, run:"
  echo "$BREW_INSTALL_CMD"
  read -r -p "Do you want to install Homebrew now? (y/n): " INSTALL_BREW

  if [[ "$INSTALL_BREW" =~ ^[Yy]$ ]]; then
    eval "$BREW_INSTALL_CMD" &>/dev/null
  else
    echo "Homebrew is required. Install it manually and rerun this script."
    exit 1
  fi
fi

if ! command -v pipx &>/dev/null; then
  echo "Installing pipx..."
  brew install pipx $QUIET_FLAG &>/dev/null
fi

pipx ensurepath &>/dev/null

export PATH="$HOME/.local/bin:$PATH"

echo "Installing Poetry..."
pipx install poetry $QUIET_FLAG &>/dev/null

echo "Installing dependencies..."
poetry install $QUIET_FLAG &>/dev/null

echo "Checking build..."
bash ./build.sh $QUIET_FLAG &>/dev/null

echo "Script execution completed successfully."
exit 0