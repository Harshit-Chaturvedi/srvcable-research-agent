"""Research brief agent: ticker + folder of docs -> Markdown brief."""
import os
import re
import sys
import pathlib
from openai import OpenAI

# Ensure UTF-8 output on all platforms
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Load .env if present
env_candidates = [
    pathlib.Path(".env"),
    pathlib.Path(__file__).parent / ".env",
    pathlib.Path(r"C:\Users\harsh\OneDrive\Documents\research_pack\.env")
]
for env_file in env_candidates:
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

ticker = sys.argv[1] if len(sys.argv) > 1 else "SRVCABLE"
folder = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path("research_pack")
today = sys.argv[3] if len(sys.argv) > 3 else "2026-09-23"

prompt_path = pathlib.Path(__file__).with_name("system_prompt.md")
if not prompt_path.exists():
    prompt_path = pathlib.Path("system_prompt.md")
SYSTEM = prompt_path.read_text(encoding="utf-8")

api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL")
model = os.environ.get("MODEL", "qwen/qwen3.8-27b")

client = OpenAI(api_key=api_key, base_url=base_url)


def chat(system_msg, user_msg, max_tokens=750):
    r = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    )
    return r.choices[0].message.content


# Load documents
docs = []
for p in sorted(folder.glob("*.md")):
    if p.name.lower() in ("readme.md", "assignment_readme.md", "brief.md", "reference_brief.md", "system_prompt.md", "test_log.md", "video_script.md"):
        continue
    content = p.read_text(encoding="utf-8")
    docs.append(f'<document id="S{len(docs)+1}" file="{p.name}">\n{content}\n</document>')

if not docs:
    print(f"Error: No markdown documents found in {folder}", file=sys.stderr)
    sys.exit(1)

pack = "\n\n".join(docs)
print(f"Loaded {len(docs)} documents. Running pipeline for {ticker} as of {today}...", flush=True)

# Pass 1: Triage
print("[1/3] Running Triage Pass (evaluating source tiers, company match, staleness & injection)...", flush=True)
triage_prompt = (
    SYSTEM + "\n\nDo STEP 1 only. Output a compact table:\n"
    "| ID | File | Tier | Status | Reason |\n"
    "Note any numeric conflicts, staleness, or prompt injections in 3 lines max."
)
triage = chat(
    triage_prompt,
    f"Ticker: {ticker}\nToday: {today}\n\n{pack}",
    max_tokens=500
)

# Pass 2: Write Brief
print("[2/3] Running Write Pass (synthesizing 5 sections with strict citations)...", flush=True)
write_prompt = (
    f"Ticker: {ticker}\nToday: {today}\n\n"
    f"TRIAGE RESULT:\n{triage}\n\n"
    f"DOCUMENTS:\n{pack}\n\n"
    "Write the complete one-page research brief now with all 5 sections:\n"
    "1. Snapshot\n2. Bull case\n3. Bear case\n4. Open questions\n5. Sources\n"
    "Rules: Every bullet/sentence in sections 1-4 must end with a source tag like [S1]. Keep each bullet concise (1 line)."
)
brief = chat(SYSTEM, write_prompt, max_tokens=900)

# Pass 3: Deterministic Code Check
print("[3/3] Running Code Verification Pass (regex checking all [S#] citations)...", flush=True)
lines = brief.splitlines()
bad_lines = []
in_sources = False

for line in lines:
    stripped = line.strip()
    if stripped.startswith("## 5. Sources") or stripped.startswith("### Sources") or stripped.startswith("## Sources") or "Sources" in stripped:
        in_sources = True
    if in_sources:
        continue
    if stripped.startswith(("-", "*", "1.", "2.", "3.", "4.")) and len(stripped) > 5:
        if not re.search(r"\[S\d+\]", stripped):
            bad_lines.append(line)

if bad_lines:
    print(f"  -> Found {len(bad_lines)} lines missing citations. Auto-repairing...", flush=True)
    repair_prompt = (
        "In the brief below, the following lines are missing source tags [S#]:\n" +
        "\n".join(bad_lines) +
        "\n\nReturn the COMPLETE brief with all 5 sections intact, adding the appropriate [S#] citation to each of these lines or removing ungrounded claims.\n"
        f"CURRENT BRIEF:\n{brief}\n\nDOCUMENTS:\n{pack}"
    )
    repaired_brief = chat(SYSTEM, repair_prompt, max_tokens=900)
    if len(repaired_brief.strip().splitlines()) >= 15:
        brief = repaired_brief
else:
    print("  -> All claims properly tagged with source citations!", flush=True)

print("\n" + "="*50)
print("FINAL BRIEF OUTPUT:")
print("="*50 + "\n")
print(brief)

# Save output to brief.md
out_path = pathlib.Path(__file__).parent / "brief.md"
out_path.write_text(brief, encoding="utf-8")
print(f"\nBrief saved to {out_path.name}")
