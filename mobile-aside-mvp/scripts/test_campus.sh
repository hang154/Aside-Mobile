#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
javac -encoding UTF-8 -d "$WORK" "$ROOT/app/src/main/java/ai/decisionos/aside/CampusScenario.java" "$ROOT/scripts/TestCampusScenario.java"
java -cp "$WORK" TestCampusScenario
