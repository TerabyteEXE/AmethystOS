#!/usr/bin/env bash
# Shared environment and messages for Kuhl's Fedora + Niri edition.
KUHL_DATA="${XDG_DATA_HOME:-$HOME/.local/share}/kuhl"
KUHL_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/kuhl"
KUHL_BIN="$HOME/.local/bin/kuhl"
kuhl_info() { printf '[kuhl] %s\n' "$*"; }
kuhl_warn() { printf '[kuhl] WARNING: %s\n' "$*" >&2; }
kuhl_error() { printf '[kuhl] ERROR: %s\n' "$*" >&2; return 1; }
