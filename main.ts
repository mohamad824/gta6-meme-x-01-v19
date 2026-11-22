import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

// gta6-meme-x-01 v19: copy POST.json from the repository into /output.
const repoRoot = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const postPath = join(repoRoot, "POST.json");

// Refuse to hand in a malformed post file: it must parse and name an X post.
const post = JSON.parse(readFileSync(postPath, "utf8")) as { url?: unknown };
if (typeof post.url !== "string" || !/^https:\/\/(x\.com|twitter\.com)\//.test(post.url)) {
  throw new Error("POST.json does not name a valid X post URL");
}
mkdirSync(outDir, { recursive: true });
copyFileSync(postPath, join(outDir, "POST.json"));
