#!/usr/bin/env bash

set -euo pipefail

commit_msg=""
if [[ -n "${1:-}" && -f "$1" ]]; then
  commit_msg="$(head -n 1 "$1" | tr -d '\r\n')"
fi

if [[ -z "$commit_msg" && -n "${LEFTHOOK_COMMIT_MSG:-}" ]]; then
  commit_msg="$(printf '%s' "$LEFTHOOK_COMMIT_MSG" | head -n 1 | tr -d '\r\n')"
fi

if [[ -z "$commit_msg" && -f .git/COMMIT_EDITMSG ]]; then
  commit_msg="$(head -n 1 .git/COMMIT_EDITMSG | tr -d '\r\n')"
fi

if [[ -z "$commit_msg" ]] || printf '%s' "$commit_msg" | grep -qE '^#'; then
  printf '[warn] empty commit message, skipping check.\n'
  exit 0
fi

printf '[check] checking commit: "%s"\n' "$commit_msg"

if ! printf '%s' "$commit_msg" | grep -qE '^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test|git)(\([^)]+\))?: .{1,72}$'; then
  printf '[fail] invalid commit message format, spec: \n'
  printf 'use: <type>(optional scope): short description\n'
  printf 'valid types: build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test, git\n'
  printf 'your message: "%s"\n' "$commit_msg"
  exit 1
fi

if (( ${#commit_msg} > 128 )); then
  printf '[fail] commit message too long, max 128 chars.\n'
  printf 'actual length: %d\n' ${#commit_msg}
  printf 'your message: "%s"\n' "$commit_msg"
  exit 1
fi

description="$(printf '%s' "$commit_msg" | sed -E 's/^[a-z]+(\([^)]+\))?: //')"
if printf '%s' "$description" | grep -qE '^(add|fix|update|change|remove|create)'; then
  printf '[warn] good style in imperative: add, fix, update, etc.\n'
  printf 'your message: "%s"\n' "$commit_msg"
fi

printf '[ok] commit message is valid.\n'
