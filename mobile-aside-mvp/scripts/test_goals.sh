#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'find "$WORK" -type f -delete; find "$WORK" -depth -type d -empty -delete' EXIT
javac -encoding UTF-8 -d "$WORK" "$ROOT/app/src/main/java/ai/decisionos/aside/GoalRules.java" "$ROOT/app/src/main/java/ai/decisionos/aside/DiscoveryProviders.java" "$ROOT/scripts/TestGoalRules.java"
java -cp "$WORK" TestGoalRules
