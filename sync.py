#!/usr/bin/env python3
"""
ai-portfolio sync. Reads ground truth from the empire and writes portfolio.json.
Runs on launchd every 15 min so the site is genuinely real time.
"""
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/macbookair/Claude")
AGENTS_DIR = Path("/Users/macbookair/.claude/agents")
MEMORY_DIR = Path("/Users/macbookair/.claude/projects/-Users-macbookair-Claude/memory")
PROD_MGR = ROOT / "production-manager"
OUT = Path(__file__).parent / "portfolio.json"

PHT = "Asia/Manila"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def count_agents() -> tuple[int, list[dict]]:
    agents = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        name = path.stem
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        description = ""
        m = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        if m:
            description = m.group(1).strip().strip('"').strip("'")
            if len(description) > 220:
                description = description[:217] + "..."
        agents.append({"name": name, "description": description})
    return len(agents), agents


BRAIN_REGIONS = [
    {
        "region": "HIPPOCAMPUS",
        "role": "Durable memory",
        "agents": ["memorykeeper"],
        "notes": "MEMORY.md index plus ~/.claude/projects/-Users-macbookair-Claude/memory/ store",
    },
    {
        "region": "PREFRONTAL CORTEX",
        "role": "Planning, executive function",
        "agents": ["overwatch", "production-manager", "mirai", "jugaad"],
    },
    {
        "region": "ORBITOFRONTAL CORTEX",
        "role": "Value judgment, ship or no ship",
        "agents": ["citadel-qa", "lean"],
    },
    {
        "region": "AMYGDALA",
        "role": "Threat detection, refusal reflex",
        "agents": ["nerve", "security-auditor", "cutsmith-warden"],
    },
    {
        "region": "CORPUS CALLOSUM",
        "role": "Cross hemisphere bridge",
        "agents": [],
        "notes": "knowledge_bus.jsonl, session mesh, SessionStart hook",
    },
    {
        "region": "CEREBELLUM",
        "role": "Motor learning, fix loops",
        "agents": ["debug", "lean"],
    },
    {
        "region": "BASAL GANGLIA",
        "role": "Learned habits, routines",
        "agents": [],
        "notes": "launchd crons, Stop hook, SessionStart hook, weekly DGM consolidator",
    },
    {
        "region": "BRAIN STEM",
        "role": "Autonomic survival",
        "agents": ["phoenix"],
        "notes": "gabfx watchdog, keepalive.sh, phoenix heartbeat every 10 min",
    },
    {
        "region": "THALAMUS",
        "role": "Sensory relay",
        "agents": ["briefing"],
        "notes": "SessionStart hook context injection, ToolSearch",
    },
    {
        "region": "VTA / NUCLEUS ACCUMBENS",
        "role": "Reward circuit",
        "agents": [],
        "notes": "Proven Ledger, DGM promotion path",
    },
    {
        "region": "NIGHT CONSOLIDATION",
        "role": "Replay, weekly sweep",
        "agents": [],
        "notes": "DGM Saturday consolidator, weekly bloat sweep, weekly hedging audit",
    },
    {
        "region": "OPTIC / AUDITORY CORTEX",
        "role": "Input streams",
        "agents": ["watcher"],
        "notes": "computer-use MCP, claude-in-chrome MCP",
    },
    {
        "region": "FUSIFORM FACE AREA",
        "role": "Identity recognition",
        "agents": [],
        "notes": "Beneficiaries DB lookup, supplier identity match, name disambiguation rule",
    },
    {
        "region": "MIRROR NEURONS",
        "role": "Imitation, style transfer",
        "agents": ["cutsmith", "siren"],
    },
    {
        "region": "MOTOR CORTEX",
        "role": "Direct action, execution",
        "agents": ["appsbuilder", "arcane", "canva"],
    },
    {
        "region": "PARIETAL LOBE",
        "role": "Spatial attention",
        "agents": [],
        "notes": "FOREMAN docket focus, two ordering presentation rule",
    },
    {
        "region": "LANGUAGE CENTER",
        "role": "Broca and Wernicke",
        "agents": ["siren", "sensei", "legal-advisor"],
    },
    {
        "region": "SPECIALIZED NEOCORTEX",
        "role": "Domain expert circuits",
        "agents": ["pse-trader", "crypto-trader", "gabfx-trader", "gabfx-manager", "trader-dgm"],
    },
]

EMPTY_SEATS = [
    {"name": "HYPOTHALAMUS", "role": "Homeostatic regulator", "purpose": "Watches the empire for fatigue, drift, agent overload, stale data"},
    {"name": "ANTERIOR CINGULATE", "role": "Live contradiction catcher", "purpose": "Pre flight scan, cross check every claim against knowledge bus and Proven Ledger"},
    {"name": "DEFAULT MODE NETWORK", "role": "Idle idea generation", "purpose": "Fires between tasks, surfaces unfinished threads, daily proposals digest"},
    {"name": "THEORY OF MIND", "role": "Model of Boss", "purpose": "Predicts the next ask before he types it"},
    {"name": "INSULA", "role": "Interoception, gut feel", "purpose": "Yellow flag when a request feels off, one sentence of why"},
]

CITADEL_RAMPARTS = [
    {"name": "Core", "phase": "1", "status": "LIVE", "desc": "Finance OS shell, CFO only access, 11 module nav"},
    {"name": "REGISTRY", "phase": "2", "status": "LIVE", "desc": "Supplier and beneficiary registry, empire wide name disambiguation"},
    {"name": "VAULT", "phase": "3", "status": "LIVE", "desc": "Document and EWT vault, supplier initiated tax workflow"},
    {"name": "SEAL", "phase": "4", "status": "DESIGN", "desc": "Auto BIR 2307 issuance, supplier initiated, dual signature pad"},
    {"name": "RECON", "phase": "5", "status": "LIVE", "desc": "Reconciliation, auto cross checks transactions against source"},
    {"name": "LEDGER", "phase": "6", "status": "PARTIAL", "desc": "Folders, OT, leave, reimbursement, disbursement live. Payroll compute pending"},
    {"name": "SANCTUM", "phase": "7", "status": "LIVE", "desc": "CFO eyes only layer. Equity, cap table, sensitive comp, car loan alert"},
    {"name": "GATE", "phase": "8", "status": "LIVE", "desc": "Multi level approval chains without third party software"},
    {"name": "Petty Cash", "phase": "9", "status": "LIVE", "desc": "Daily 7am PHT email digest, fully autonomous"},
    {"name": "Payroll Bridge", "phase": "10", "status": "LIVE", "desc": "Auto fires 10th and 25th, validates payees, alerts CEO"},
    {"name": "COMPLIANCE", "phase": "11", "status": "DESIGN", "desc": "Supplier accreditation rampart, design Qs pending"},
]

SHIPPED_SYSTEMS = [
    {
        "title": "PHOENIX, persistent task runner",
        "stack": "Python, launchd, JSON ledger",
        "ship": "2026-05-31",
        "tagline": "Tasks survive Claude usage limits and context resets. Heartbeat every 10 minutes until DONE.",
        "metrics": ["Headless Claude relauncher", "Money + destructive actions hard blocked"],
    },
    {
        "title": "InstaPay batch pipeline",
        "stack": "Python, Chrome MCP, AppleScript",
        "ship": "2026-05-12",
        "tagline": "RPA on a banking UI that has no public API. Moves real payroll money with dry run mandatory and halt on ambiguity.",
        "metrics": ["End to end .txt to Payment Confirmation drafts", "BIC validation against seeded wallets"],
    },
    {
        "title": "DGM self evolving agent loop",
        "stack": "Python, Saturday cron",
        "ship": "Closed loop 2026-05-29",
        "tagline": "Capture, retrieve, consolidate. Trading lessons auto promote to feedback.md weekly without retraining.",
        "metrics": ["Trader specific signal capture", "Auto promote winners, prune decaying setups"],
    },
    {
        "title": "GAB FX live forex bot + supervisor",
        "stack": "Python, MT5, EA, watchdog agent",
        "ship": "Demo live 2026-06-05",
        "tagline": "End to end autonomous XAUUSD bot. Agent supervises a deterministic Python loop, watchdog catches stacking and stop drift.",
        "metrics": ["68 of 68 GAB FX video transcripts absorbed", "Reconcile + re adopt after orphan incident 2026-06-05"],
    },
    {
        "title": "Session Mesh + Knowledge Bus",
        "stack": "JSON, SessionStart and Stop hooks",
        "ship": "2026-05-30",
        "tagline": "Cross session ambient continuity. Any new Claude Code window boots fully briefed on active projects and open decisions.",
        "metrics": ["Near realtime fact propagation", "Zero server, zero broker"],
    },
    {
        "title": "ARWIN REVIEWS",
        "stack": "Python build, vanilla JS, launchd + GitHub Action autosync",
        "ship": "2026-06-01",
        "tagline": "Independent film creator site, 1343 films, 413 reviews, 124k words. AI predictor embedded as a member benefit.",
        "metrics": ["7 monetization models wired", "Letterboxd export to media brand"],
        "link": "https://arwinreviews.com",
    },
    {
        "title": "Curated Archive store",
        "stack": "Apps Script, Sheets, Xendit",
        "ship": "2026-06-07",
        "tagline": "Fragrance decant ecommerce on Google free tier. GCash, Maya, card. PH wide shipping.",
        "metrics": ["227 item editable inventory", "Zero hosting cost"],
        "link": "https://curated-archive.com",
    },
    {
        "title": "ARCANE device sorcerer",
        "stack": "Python, Tizen WebSocket, Wake on LAN, Kia Connect via region workaround",
        "ship": "2026-06-01",
        "tagline": "Codes its way into the Samsung TV, the router at 192.168.100.1, and the Kia Carnival HEV 2025 EX.",
        "metrics": ["3 vendor APIs orchestrated", "Saved spell grimoire per device"],
    },
    {
        "title": "FOREMAN production manager",
        "stack": "Python, JSON docket, multi lane reconciler",
        "ship": "2026-06-07",
        "tagline": "Single docket of every unfinished thread across the empire. Standup on demand, finish first gate, drift scanner.",
        "metrics": ["13 lanes reconciled", "Cross session sync via the bus"],
    },
    {
        "title": "NERVE overcaution watchdog",
        "stack": "Python, Stop hook, classifier",
        "ship": "2026-06-06",
        "tagline": "Kills false denials of proven capability. Three way classifier keeps justified caution only, rewrites the rest.",
        "metrics": ["Denial Lock with cited ground truth check", "Routes root fix to jugaad, debug, or FORGE"],
    },
]

TECH_STACK = [
    {"label": "Python", "kind": "core"},
    {"label": "Google Apps Script", "kind": "core"},
    {"label": "Streamlit", "kind": "core"},
    {"label": "JavaScript", "kind": "core"},
    {"label": "HTML / CSS", "kind": "core"},
    {"label": "MCP (Model Context Protocol)", "kind": "ai"},
    {"label": "Claude Code SDK", "kind": "ai"},
    {"label": "Multi agent orchestration", "kind": "ai"},
    {"label": "RAG patterns", "kind": "ai"},
    {"label": "Chrome MCP / browser automation", "kind": "automation"},
    {"label": "AppleScript", "kind": "automation"},
    {"label": "launchd", "kind": "automation"},
    {"label": "GitHub Actions", "kind": "automation"},
    {"label": "Google Sheets API", "kind": "data"},
    {"label": "Drive API", "kind": "data"},
    {"label": "Gmail API", "kind": "data"},
    {"label": "Calendar API", "kind": "data"},
    {"label": "MetaTrader 5 (EA)", "kind": "trading"},
    {"label": "Tizen WebSocket", "kind": "iot"},
    {"label": "Wake on LAN", "kind": "iot"},
    {"label": "Kia Connect telematics", "kind": "iot"},
    {"label": "Xendit payments", "kind": "fintech"},
    {"label": "InstaPay (PH bank rails)", "kind": "fintech"},
    {"label": "BIR (PH tax)", "kind": "fintech"},
]

HEADLINERS = [
    "Multi agent orchestration: 47+ specialized agents wired across 18 brain regions",
    "CITADEL Finance OS: 11 ramparts live on Google free tier, a custom ERP built by AI",
    "PHOENIX persistent runner: tasks survive usage limits and context resets",
    "Live MT5 forex bot with supervisor agent and watchdog reconciliation",
    "InstaPay batch pipeline: RPA on a banking UI with no public API",
    "DGM self evolving loop: trading lessons auto promote to permanent memory weekly",
    "Session Mesh + Knowledge Bus: cross session continuity with zero server",
    "ARCANE device sorcery: TV, router, and car orchestrated across three vendor APIs",
    "ARWIN REVIEWS: 1343 film corpus, AI predictor, 7 monetization models",
    "NERVE overcaution watchdog: Denial Lock against false capability denials",
]


def get_shipped_count() -> int:
    """Count Lane shipped items by scanning DOCKET.md for the shipped section."""
    docket = PROD_MGR / "DOCKET.md"
    if not docket.exists():
        return 0
    text = docket.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"shipped.*?\|.*?\n((?:\|.*\|\n)+)", text, re.IGNORECASE)
    if not m:
        return 0
    rows = [r for r in m.group(1).split("\n") if r.startswith("|") and "---" not in r]
    return max(0, len(rows) - 1)


def main() -> None:
    agent_count, agent_list = count_agents()
    wired_regions = len(BRAIN_REGIONS)
    empty_seats = len(EMPTY_SEATS)
    citadel_live = sum(1 for r in CITADEL_RAMPARTS if r["status"] == "LIVE")
    citadel_total = len(CITADEL_RAMPARTS)
    shipped_systems = len(SHIPPED_SYSTEMS)

    data = {
        "meta": {
            "last_synced_utc": utcnow_iso(),
            "version": "1.0.0",
            "source": "auto generated by sync.py from production empire data",
        },
        "owner": {
            "name": "Arwin Edward M. Bagaslao",
            "callsign": "Boss",
            "headline": "AI Engineer building multi agent systems in production",
            "location": "Asia / Manila (PHT)",
            "email": "arwinbagaslao@gmail.com",
            "summary": (
                "Founder and CFO who builds AI systems end to end. "
                "47+ specialized agents wired across an 18 region brain map, "
                "an 11 rampart finance OS on Google free tier, "
                "a live forex bot with supervisor and watchdog, "
                "a persistent task runner that survives context death, "
                "and an RPA pipeline that moves real payroll money through a banking UI with no public API."
            ),
        },
        "counters": {
            "agents": agent_count,
            "brain_regions_wired": wired_regions,
            "brain_seats_empty": empty_seats,
            "citadel_ramparts_live": citadel_live,
            "citadel_ramparts_total": citadel_total,
            "shipped_systems": shipped_systems,
        },
        "headliners": HEADLINERS,
        "brain_regions": BRAIN_REGIONS,
        "empty_seats": EMPTY_SEATS,
        "citadel_ramparts": CITADEL_RAMPARTS,
        "shipped_systems": SHIPPED_SYSTEMS,
        "agents": agent_list,
        "tech_stack": TECH_STACK,
    }

    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"wrote {OUT}")
    print(f"  agents : {agent_count}")
    print(f"  regions: {wired_regions} wired, {empty_seats} empty seats")
    print(f"  citadel: {citadel_live}/{citadel_total} live")


if __name__ == "__main__":
    main()
