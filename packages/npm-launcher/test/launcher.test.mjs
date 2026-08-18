import assert from "node:assert/strict";
import { chmodSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { spawnSync } from "node:child_process";

const launcher = new URL("../bin/mirage.js", import.meta.url);

test("launcher forwards CLI arguments to a configured MIRAGE runtime", () => {
  const directory = mkdtempSync(join(tmpdir(), "mirage-launcher-"));
  const shim = join(directory, "mirage-shim.mjs");
  writeFileSync(shim, "#!/usr/bin/env node\nprocess.stdout.write(process.argv.slice(2).join(' '));\n");
  chmodSync(shim, 0o755);

  const result = spawnSync(process.execPath, [launcher.pathname, "doctor", "--json"], {
    encoding: "utf8",
    env: { ...process.env, MIRAGE_COMMAND: shim },
  });

  assert.equal(result.status, 0);
  assert.equal(result.stdout, "doctor --json");
});

test("launcher gives an actionable error when the Python runtime is absent", () => {
  const result = spawnSync(process.execPath, [launcher.pathname, "doctor"], {
    encoding: "utf8",
    env: { ...process.env, MIRAGE_COMMAND: "mirage-command-that-does-not-exist" },
  });

  assert.equal(result.status, 127);
  assert.match(result.stderr, /Install the Python distribution/);
});
