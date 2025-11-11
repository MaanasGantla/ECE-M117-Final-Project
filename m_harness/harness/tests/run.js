import fs from "fs";
import path from "path";
import { chromium } from "playwright"; // ✅ correct import

function readPlan(planPath) {
  if (!fs.existsSync(planPath)) {
    throw new Error(`plan.json not found at ${planPath}. Did you run the generator?`);
  }
  const raw = fs.readFileSync(planPath, "utf-8");
  return JSON.parse(raw);
}

async function injectSnippet(page, htmlPath) {
  const html = fs.readFileSync(htmlPath, "utf-8");
  await page.evaluate((snippet) => {
    const container = document.getElementById("injection-root") || document.body;
    const template = document.createElement("template");
    template.innerHTML = snippet;

    const nodes = Array.from(template.content.childNodes);
    nodes.forEach((node) => {
      if (node.nodeName === "SCRIPT") {
        const script = document.createElement("script");
        Array.from(node.attributes || []).forEach((attr) => {
          script.setAttribute(attr.name, attr.value);
        });
        script.textContent = node.textContent || "";
        container.appendChild(script);
      } else {
        container.appendChild(node);
      }
    });
  }, html);
}

async function assertMarker(page) {
  const marker = await page.evaluate(() => globalThis.__PG_MARKER || window.__PG_MARKER);
  if (marker) return { ok: true, mode: "window.__PG_MARKER", value: marker };

  const attr = await page.evaluate(() => {
    const el = document.querySelector("[data-pg-marker]");
    return el ? el.getAttribute("data-pg-marker") : null;
  });
  if (attr) return { ok: true, mode: "data-pg-marker", value: attr };

  return { ok: false };
}

async function main() {
  // ✅ context variables: define once here for clarity
  const OUT_DIR = process.env.OUT_DIR || path.resolve(process.cwd(), "./sample_out");
  console.log("[debug] OUT_DIR resolved to:", OUT_DIR);
  
  const BASE_URL = process.env.BASE_URL || "http://localhost:3000/";
  const planPath = path.join(OUT_DIR, "plan.json");

  const plan = readPlan(planPath);
  const browser = await chromium.launch();
  const page = await browser.newPage();

  console.log(`[harness] Navigating to ${BASE_URL}`);
  await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });

  let pass = 0, fail = 0;

  for (const item of plan.items || []) {
    const filePath = path.resolve(OUT_DIR, item.artifact.replace(/^out\//, "").replace(/^\.\//, ""));
    if (!fs.existsSync(filePath)) {
      console.error(`[harness] Missing artifact: ${filePath}`);
      fail++;
      continue;
    }

    console.log(`[harness] Injecting ${item.template_id} (${item.finding_type}) from ${filePath}`);
    await injectSnippet(page, filePath);

    await page.waitForTimeout(300); // let scripts execute

    const res = await assertMarker(page);
    if (res.ok) {
      console.log(`[harness] ✅ Marker detected via ${res.mode}: ${res.value}`);
      pass++;
    } else {
      console.error(`[harness] ❌ Marker NOT detected.`);
      fail++;
    }
  }

  await browser.close();
  console.log(`[harness] Done. Passed: ${pass}, Failed: ${fail}`);
  process.exit(fail ? 1 : 0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
