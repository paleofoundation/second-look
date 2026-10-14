import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { readExecutionProfile } from "./execution-profile.mjs";

const [command, ...args] = process.argv.slice(2);
if (!["dev", "build"].includes(command)) throw new Error("Expected dev or build.");
if (command === "build") {
  const outcomes = spawnSync(process.execPath, [fileURLToPath(new URL("./check-outcome-summaries.mjs", import.meta.url))], { stdio: "inherit" });
  if (outcomes.error) throw outcomes.error;
  if (outcomes.status !== 0) process.exit(outcomes.status ?? 1);
  const grading = spawnSync(process.execPath, [fileURLToPath(new URL("./evidence-assessments.mjs", import.meta.url)), "--check"], { stdio: "inherit" });
  if (grading.error) throw grading.error;
  if (grading.status !== 0) process.exit(grading.status ?? 1);
  const readerBoundary = spawnSync(process.execPath, [fileURLToPath(new URL("./verify-reader-boundary.mjs", import.meta.url)), "--source-only"], { stdio: "inherit" });
  if (readerBoundary.error) throw readerBoundary.error;
  if (readerBoundary.status !== 0) process.exit(readerBoundary.status ?? 1);
  const check = spawnSync(process.execPath, [fileURLToPath(new URL("./update-guide-marketing-hashes.mjs", import.meta.url)), "--check"], { stdio: "inherit" });
  if (check.error) throw check.error;
  if (check.status !== 0) process.exit(check.status ?? 1);
  const assets = spawnSync(process.execPath, [fileURLToPath(new URL("./verify-guide-assets.mjs", import.meta.url))], { stdio: "inherit" });
  if (assets.error) throw assets.error;
  if (assets.status !== 0) process.exit(assets.status ?? 1);
}
const managedLinux = readExecutionProfile() === "managed-linux";

if (managedLinux && command === "build") {
  const result = spawnSync("bash", [
    fileURLToPath(new URL("./build-verified.sh", import.meta.url)), ...args,
  ], { stdio: "inherit" });
  if (result.error) throw result.error;
  process.exit(result.status ?? 1);
}

// Import in this process so the preview owner retains its PID and signals.
const cli = new URL(managedLinux
  ? "../node_modules/vite/bin/vite.js"
  : "../node_modules/vinext/dist/cli.js", import.meta.url);
process.argv = [process.execPath, fileURLToPath(cli), command,
  ...(!managedLinux && command === "dev" ? ["--port", "5173"] : []), ...args];
await import(cli.href);
