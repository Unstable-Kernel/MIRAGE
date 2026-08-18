#!/usr/bin/env node
/**
 * MIRAGE's npm package intentionally launches the canonical Python CLI instead
 * of duplicating the engineering runtime in JavaScript.
 */
import { spawnSync } from "node:child_process";

const command = process.env.MIRAGE_COMMAND || "mirage";
const result = spawnSync(command, process.argv.slice(2), {
  stdio: "inherit",
  shell: process.platform === "win32",
});

if (result.error?.code === "ENOENT") {
  console.error("MIRAGE runtime was not found.");
  console.error("Install the Python distribution when it is published: python -m pip install mirage-engineering");
  console.error("For source development, follow https://github.com/Unstable-Kernel/MIRAGE#readme");
  process.exitCode = 127;
} else if (result.error) {
  console.error(`Unable to start MIRAGE: ${result.error.message}`);
  process.exitCode = 1;
} else {
  process.exitCode = result.status ?? 1;
}
