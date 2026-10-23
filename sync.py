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
        "agents": ["curated-archive-stockroom"],
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
        "agents": ["disk-janitor", "drive-janitor", "bir-watch", "portal-health"],
        "notes": "launchd crons, Stop hook, SessionStart hook, weekly DGM consolidator",
    },
    {
        "region": "BRAIN STEM",
        "role": "Autonomic survival",
        "agents": ["phoenix", "crypto-trader-manager", "marquee-manager"],
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
        "agents": ["hype-scout"],
        "notes": "Proven Ledger, DGM promotion path",
    },
    {
        "region": "NIGHT CONSOLIDATION",
        "role": "Replay, weekly sweep",
        "agents": ["prompt-engineer"],
        "notes": "DGM Saturday consolidator, weekly bloat sweep, weekly hedging audit",
    },
    {
        "region": "OPTIC / AUDITORY CORTEX",
        "role": "Input streams",
        "agents": ["watcher"],
        "notes": "Playwright, Chrome DevTools Protocol, Gemini vision, screen recorder",
    },
    {
        "region": "FUSIFORM FACE AREA",
        "role": "Identity recognition",
        "agents": ["juice-meter", "logo-hunter"],
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
        "agents": ["appsbuilder", "arcane", "canva", "secsender", "secbatch", "marquee", "reel", "frontend-design", "tiktok-review-replier"],
    },
    {
        "region": "PARIETAL LOBE",
        "role": "Spatial attention",
        "agents": ["tabi", "kia-expert"],
        "notes": "FOREMAN docket focus, two ordering presentation rule",
    },
    {
        "region": "LANGUAGE CENTER",
        "role": "Broca and Wernicke",
        "agents": ["siren", "sensei"],
    },
    {
        "region": "SPECIALIZED NEOCORTEX",
        "role": "Domain expert circuits",
        "agents": ["pse-trader", "crypto-trader", "gabfx-trader", "gabfx-manager", "trader-dgm", "curated-archive-tiktoker", "curated-archive-shopee", "curated-archive-lazada", "curated-archive-website", "curated-archive-cs"],
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
    {"name": "SEAL", "phase": "4", "status": "LIVE", "desc": "Auto BIR 2307 issuance from the supplier portal with a public verify page"},
    {"name": "RECON", "phase": "5", "status": "LIVE", "desc": "Reconciliation, auto cross checks transactions against source"},
    {"name": "LEDGER", "phase": "6", "status": "PARTIAL", "desc": "Folders, OT, leave, reimbursement, disbursement live. Payroll compute pending"},
    {"name": "SANCTUM", "phase": "7", "status": "LIVE", "desc": "CFO eyes only layer. Equity, cap table, sensitive comp, car loan alert"},
    {"name": "GATE", "phase": "8", "status": "LIVE", "desc": "Multi level approval chains without third party software"},
    {"name": "Petty Cash", "phase": "9", "status": "LIVE", "desc": "Float register, submissions and one click email approvals"},
    {"name": "Payroll Bridge", "phase": "10", "status": "LIVE", "desc": "Auto fires 10th and 25th, validates payees, alerts CEO"},
    {"name": "COMPLIANCE", "phase": "11", "status": "LIVE", "desc": "Supplier accreditation portal, expiry driven blocking on permits and ITR"},
]

def film_count() -> int:
    try:
        return len(json.loads((ROOT / "letterboxd-truth" / "truth.json").read_text())["films"])
    except Exception:
        return 1599


FILM_COUNT = film_count()

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
        "stack": "Python, Playwright, Chrome DevTools Protocol, AppleScript",
        "ship": "2026-05-12",
        "tagline": "RPA on a banking UI that has no public API. Moves real payroll money with a readback gate, duplicate guard and halt on ambiguity.",
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
        "tagline": f"Independent film creator site, {FILM_COUNT:,} films rated, 400+ written reviews. AI predictor embedded as a member benefit.",
        "metrics": ["7 monetization models wired", "Letterboxd export to media brand"],
        "link": "https://arwinreviews.com",
    },
    {
        "title": "Curated Archive store",
        "stack": "Apps Script, Sheets, Xendit, GitHub Pages",
        "ship": "2026-06-07",
        "tagline": "Fragrance decant ecommerce on Google free tier. GCash, Maya, card. PH wide shipping.",
        "metrics": ["283 product catalog, 1,121 SKUs, the price origin for 3 marketplaces", "Zero hosting cost"],
        "link": "https://curated-archive.com",
    },
    {
        "title": "GRIDDLE, food cart operating system",
        "stack": "Apps Script, Sheets, Drive, HtmlService",
        "ship": "2026-09",
        "tagline": "Runs a food cart business end to end from a phone. Shift open, close and remit, variance math, spend book, request and approval gate, bank recon, owner dashboard.",
        "metrics": ["Phone first crew screens, no Google account needed", "Auto alerts on cash variance, late remit and big spends", "Every delete logged for full rebuild"],
    },
    {
        "title": "PABAON order site",
        "stack": "Vanilla JS, PWA, GitHub Pages",
        "ship": "2026-10-23",
        "tagline": "Online ordering storefront for a kare kare brand. Cart, delivery or pick up, GCash checkout, installable on the phone.",
        "metrics": ["Installable PWA", "Zero hosting cost"],
        "link": "https://bigbamwolf.github.io/pabaon/",
    },
    {
        "title": "Pixelens Employee Portal",
        "stack": "Apps Script, Sheets, Google SSO, HtmlService",
        "ship": "Live @v218",
        "tagline": "Branded staff portal on the CITADEL finance OS. Petty cash, reimbursements, OT and leave filing feeding a one click CEO and CFO approval chain, plus an HR Hub with policies, forms and a live directory.",
        "metrics": ["Google SSO matched against the employee roster", "Same approval email flow as the finance back office"],
    },
    {
        "title": "A&D Employee Portal + Android app",
        "stack": "Apps Script, Sheets, PWA, Trusted Web Activity APK",
        "ship": "2026-10-22",
        "tagline": "Staff portal built inside the GRIDDLE cart OS. OT, leave, reimbursement, profile and account admin with a COO review then CFO approve chain, shipped as an installable Android app.",
        "metrics": ["Salted hash sign in, session tokens, lockout after 5 wrong tries", "APK packaged with no local Android SDK"],
    },
    {
        "title": "Supplier billing portal",
        "stack": "Apps Script (V2 live) and Streamlit (V3), Sheets, Drive",
        "ship": "V2 live @34",
        "tagline": "Suppliers log in, file billing against POs, upload invoices and track payables. Admin side runs the inbox, payables board, email logs and PO register.",
        "metrics": ["Feeds the InstaPay payment pipeline", "Auto issued BIR 2307 certificates"],
    },
    {
        "title": "Supplier accreditation portal",
        "stack": "Streamlit, Sheets, Drive Shared Drive, fillable PDFs",
        "ship": "2026-05-30",
        "tagline": "Self serve vendor onboarding. Applicants upload permits and BIR documents, the system checks expiry and blocks stale paperwork, admins review with a full audit trail.",
        "metrics": ["Expiry driven blocking on Mayor's Permit and ITR", "Self healing Drive uploads"],
    },
    {
        "title": "CITADEL Finance OS",
        "stack": "Apps Script, Sheets, Drive, Gmail, 287 files, 80k lines",
        "ship": "10 of 11 ramparts live",
        "tagline": "A custom ERP built by AI on Google free tier. Beneficiaries registry, approvals, ledger, petty cash, payroll bridge, CFO only layer, sealed bank perimeter, full audit trail.",
        "metrics": ["Multi level approval chains with no third party software", "Single source of truth registry across every money flow"],
    },
    {
        "title": "Payroll Bridge",
        "stack": "Python, launchd, RPA",
        "ship": "Live",
        "tagline": "Fires on the 10th and 25th, validates every payee against the beneficiaries registry, runs the bank batch upload and alerts the CEO.",
        "metrics": ["Zero touch payroll run", "Double pay guard against the reconcile ledger"],
    },
    {
        "title": "SECSENDER single payment sender",
        "stack": "Python, Chrome CDP, AppleScript",
        "ship": "Proven live",
        "tagline": "Single bank transfer end to end on a banking UI with no API. Fill, submit, verify Posted, isolate the receipt, draft the payment confirmation, reconcile, log out.",
        "metrics": ["Readback gate before every fire", "Duplicate send guard"],
    },
    {
        "title": "Messenger Bridge",
        "stack": "Python, Playwright, 3 tier name resolver",
        "ship": "Live",
        "tagline": "After every payment confirmation email, auto sends a Messenger touch base to the payee with human like jitter and a self training contact resolver.",
        "metrics": ["Random 5 to 15 minute jitter", "Resolver learns from every correction"],
    },
    {
        "title": "SecBank batch generator",
        "stack": "Python, fixed width file spec",
        "ship": "Live",
        "tagline": "Turns pasted name and amount lines into a bank ready batch upload file, with beneficiary lookup, duplicate name disambiguation and leading zero preservation.",
        "metrics": ["Bank code validation", "Leading zero safe account numbers"],
    },
    {
        "title": "Grab invoice automation",
        "stack": "Python, Gmail, PDF parsing",
        "ship": "Monthly SOP",
        "tagline": "Scans Gmail for corporate ride billing PDFs, builds the payment batch and splits out personal consumption automatically.",
        "metrics": ["Encrypted PDF extraction", "Personal vs company split"],
    },
    {
        "title": "Petty Cash module",
        "stack": "Apps Script, Sheets, Gmail",
        "ship": "Live",
        "tagline": "Float register, submissions and one click email approvals with a daily autonomous digest.",
        "metrics": ["Bill required rule", "Fully autonomous daily run"],
    },
    {
        "title": "Manning Builder",
        "stack": "Apps Script bound to Sheets",
        "ship": "Live",
        "tagline": "Production manager converts per shoot crew lists into purchase orders, auto filling bank, email, mobile and TIN from the finance registry.",
        "metrics": ["Zero retyping of payee data", "Feeds the supplier billing portal"],
    },
    {
        "title": "BIR 2307 generator + landing site",
        "stack": "Streamlit, PDF overlay, static site",
        "ship": "Live",
        "tagline": "Bulk BIR Form 2307 withholding certificates in about 2 minutes from a supplier database, with a public landing site, pricing and FAQ.",
        "metrics": ["PDF overlay on the official form", "Bulk certificate runs"],
    },
    {
        "title": "BIR Watch",
        "stack": "Python, launchd, Sheets",
        "ship": "Daily 08:00",
        "tagline": "Watches the tax bureau for new regulations and circulars, ranks them by business impact and logs every issuance to a ledger.",
        "metrics": ["Impact ranking per business", "Daily automatic scan"],
    },
    {
        "title": "OR/SI Drive sync",
        "stack": "Python, Drive API",
        "ship": "2026-10-12",
        "tagline": "Ships scanned official receipts and invoices from disk to the right business Drive folders every week and flags double serials.",
        "metrics": ["Weekly scheduled run", "Duplicate serial detection"],
    },
    {
        "title": "MARQUEE review cross poster",
        "stack": "Python, Playwright, OMDb, PIL, Instagram",
        "ship": "Live",
        "tagline": "Harvests my film reviews off Facebook, enriches them with credits, resolves verified studio and streaming handles, renders branded cards and stages Instagram posts.",
        "metrics": ["Verified handle tagging only", "Queue and approve, never blind posts"],
    },
    {
        "title": "REEL review card renderer",
        "stack": "Python, PIL, brand contract",
        "ship": "Live",
        "tagline": "Script fillable movie review cards for the whole back catalogue on the locked ARWIN REVIEWS brand, half star aware.",
        "metrics": ["400+ reviews renderable without a design hour", "Reject list enforced in code"],
    },
    {
        "title": "Letterboxd growth engine",
        "stack": "Python, Playwright, launchd, manager",
        "ship": "Live",
        "tagline": "Four campaigns, growth follows, unfollow sweep, courtesy follow backs and a 30 day clock, with a quality gate, a manager that reads state not logs, and fault alerts.",
        "metrics": ["Liker predictor model from real follow data", "Per leg freshness checks catch silent stalls"],
    },
    {
        "title": "RELAY model ladder",
        "stack": "Python, Claude headless CLI",
        "ship": "Live",
        "tagline": "When a Claude usage cap hits, the task drops one model tier and keeps going instead of stopping.",
        "metrics": ["Wired into the comment drafter", "No task blocked by a model cap"],
    },
    {
        "title": "Watch scheduler",
        "stack": "Python, JSON ledger",
        "ship": "Live",
        "tagline": "Four lane movie watch schedule with point scoring and weekly point history, auto logging cinema trips and spend.",
        "metrics": ["Durable watched ledger", "Auto ranked list creation at 5 films"],
    },
    {
        "title": "Juice Meter + Deal Meter",
        "stack": "Apps Script, Gemini vision, Cloudflare",
        "ship": "Live",
        "tagline": "Photograph a fragrance bottle and get the ml left, then the floor, fair and instant profit buy price off the live price ladder.",
        "metrics": ["Branded subdomain", "Fixed the thinking token truncation trap"],
    },
    {
        "title": "Curated Archive stock sync",
        "stack": "Python, append only event bus, Sheets",
        "ship": "Built",
        "tagline": "A sale on any of four channels becomes one event, converts to ml off the real bottle and pushes new stock to the other three.",
        "metrics": ["Idempotent by order and line", "Queues pushes when a seller session is down"],
    },
    {
        "title": "SCOUT demand scout",
        "stack": "Python, order history, Playwright",
        "ship": "Live",
        "tagline": "Judges whether a fragrance will sell as decants before money leaves, from inside sales velocity and outside marketplace demand.",
        "metrics": ["Classifier fit 7 of 7 on labelled wins and duds", "Never reports an unreadable surface as zero demand"],
    },
    {
        "title": "Shopee blacklist watch",
        "stack": "Python, launchd",
        "ship": "Live",
        "tagline": "The marketplace has no buyer block, so a watcher matches every new order against a blacklist and alerts before shipping.",
        "metrics": ["Catches bad buyers before dispatch", "Runs headless"],
    },
    {
        "title": "Pixelens Hunter",
        "stack": "Python, SMTP verification",
        "ship": "Built",
        "tagline": "Self hosted clone of a paid lead database backend. Discovers names, infers email patterns and verifies addresses for free.",
        "metrics": ["Replaces a paid subscription", "Pattern inference plus live verification"],
    },
    {
        "title": "Pixelens Lead Engine",
        "stack": "Apps Script, Gmail",
        "ship": "Built",
        "tagline": "Email scraper and blaster with follow up waves, replacing a paid sales tool.",
        "metrics": ["Wave based follow ups", "Zero subscription cost"],
    },
    {
        "title": "Pixelens Reddit lead scanner",
        "stack": "Python, RSS, launchd",
        "ship": "Live hourly",
        "tagline": "Finds people paying for video and creative work every hour and filters out false leads.",
        "metrics": ["RSS route around blocked APIs", "Lead filter tuned on real misses"],
    },
    {
        "title": "Client Engine + Automation Audit",
        "stack": "Static site, form capture",
        "ship": "2026-10-21",
        "tagline": "Sales system plus a live automation audit lead magnet on the Pixelens site.",
        "metrics": ["Live lead capture", "Feeds the outreach pipeline"],
        "link": "https://pixelensadvertising.com/audit",
    },
    {
        "title": "Site promo scheduler",
        "stack": "Python, Playwright, launchd",
        "ship": "Live weekly",
        "tagline": "Weekly feature spotlight posts for three websites with the link dropped in the first comment.",
        "metrics": ["Mon, Wed, Fri cadence", "Feature first, never generic"],
    },
    {
        "title": "CERBERUS browser ladder",
        "stack": "Playwright, Codex Chrome Control, agent-browser, browser-use",
        "ship": "Live",
        "tagline": "Four head browser automation escalation routed by reading the failure. Auth failures go to the live browser head, DOM drift goes to the agent head, discoveries get written back as cheap scripts.",
        "metrics": ["2 transports, 4 heads", "Guards refuse money and outward surfaces"],
    },
    {
        "title": "WRENCH car expert",
        "stack": "Python deterministic brain, owner manual, recall data",
        "ship": "Live",
        "tagline": "Ownership brain for a hybrid minivan. Severe schedule maintenance engine, real fuel economy, cost per km, fault code decode and shop upsell defense.",
        "metrics": ["Every spec tiered by source", "Gaps declared, never guessed"],
    },
    {
        "title": "Cutsmith video pipeline",
        "stack": "Python, ffmpeg, scene detection, transcripts",
        "ship": "Live",
        "tagline": "Studies raw footage against final edits to turn my editing style into a repeatable recipe, with a QA warden that verifies every cut frame by frame.",
        "metrics": ["Editing rulebook as recipe.json", "Frame level cut verification"],
    },
    {
        "title": "CANVA design agent",
        "stack": "Canva MCP, Python",
        "ship": "Live",
        "tagline": "Finds, edits and exports designs and generates branded cards from a template in its own session so design work never pollutes a website build.",
        "metrics": ["Template driven card generation", "Clean export routing"],
    },
    {
        "title": "Watcher",
        "stack": "Swift native recorder, accessibility tree, Python",
        "ship": "2026-05-11",
        "tagline": "I demonstrate a task while narrating and it produces a replayable lesson that other agents load before doing the task themselves.",
        "metrics": ["Screen, mouse, keyboard and AX tree capture", "Lessons replayable by any agent"],
    },
    {
        "title": "Face search",
        "stack": "Python, ArcFace, Drive API",
        "ship": "Proven",
        "tagline": "Finds every photo of a person across local disk, camera cards, personal Drive and the business Drive.",
        "metrics": ["4 storage surfaces in one search", "Embedding based matching"],
    },
    {
        "title": "EXODUS + ARK",
        "stack": "Python, Playwright",
        "ship": "Proven",
        "tagline": "Pulls entire ChatGPT projects with full message trees into the local Claude brain, with scheduled backup snapshots before history prunes.",
        "metrics": ["Full message trees preserved", "Daily and weekly backup watchers"],
    },
    {
        "title": "Birthday alerter",
        "stack": "Python, launchd",
        "ship": "Live",
        "tagline": "Weekly digest of upcoming staff and supplier birthdays from the live finance registry and roster sheets.",
        "metrics": ["Monday 7am digest", "Feeds the morning briefing"],
    },
    {
        "title": "PSE trader + PH Stocks",
        "stack": "Python, DGM loop, PSE data",
        "ship": "Live signals",
        "tagline": "Philippine stock signal agents with 7 playbooks, six pre flight gates, fee aware sizing and a foreign flow confirmation layer.",
        "metrics": ["Backtested on 120 real trades", "Signals only, no auto execution"],
    },
    {
        "title": "Crypto trader paper bot + manager",
        "stack": "Python, launchd, watchdog",
        "ship": "Paper live",
        "tagline": "Daily close trend and momentum bot for BTC, ETH and SOL with a regime gate, ATR stops and a supervisor that catches derailment.",
        "metrics": ["Backtest PF 3.82, max drawdown 6.9 percent", "Watchdog checks stops, stacking and stale data"],
    },
    {
        "title": "Empire infrastructure",
        "stack": "Python, launchd, Claude Code hooks and mods",
        "ship": "Live",
        "tagline": "REAPER kills zombie processes, BOOTGUARD revives jobs that fail to load, a global gate runs heavy jobs one at a time, RADAR auto files and fixes failed jobs, Claude Guardian recovers a hung app, EMPIREHUD and a session titler live inside Claude Code, a travel switch pauses everything for trips, and janitors keep disk and Drive clean.",
        "metrics": ["Self healing scheduler on an 8GB machine", "Failed jobs auto filed and fixed"],
    },
    {
        "title": "Pixelens website",
        "stack": "Static site, Cloudflare Pages",
        "ship": "Live",
        "tagline": "Agency site for video production, events and creative work in Metro Manila.",
        "metrics": ["Zero hosting cost", "Lead magnet built in"],
        "link": "https://pixelensadvertising.com",
    },
    {
        "title": "Forex Funnel sites",
        "stack": "Static sites",
        "ship": "Built",
        "tagline": "Two lead funnels, a private wealth desk that filters for high minimum investors and a forex education funnel.",
        "metrics": ["Qualifying lead filter", "Referral commission model"],
    },
    {
        "title": "Client and product sites",
        "stack": "Static sites, PWA",
        "ship": "Built",
        "tagline": "SME financing funnel, KaloriPH, PisoFlow finance operations for SMEs, WinSign mobile document signing app, and ten demo sites for Mandaluyong small businesses.",
        "metrics": ["14 sites shipped", "Installable PWA signing app"],
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
    {"label": "Swift (macOS)", "kind": "core"},
    {"label": "Claude Code (hooks, plugins, subagents)", "kind": "ai"},
    {"label": "Claude headless CLI", "kind": "ai"},
    {"label": "MCP (Model Context Protocol)", "kind": "ai"},
    {"label": "Multi agent orchestration", "kind": "ai"},
    {"label": "Codex CLI", "kind": "ai"},
    {"label": "Gemini vision", "kind": "ai"},
    {"label": "ArcFace face embeddings", "kind": "ai"},
    {"label": "RAG patterns", "kind": "ai"},
    {"label": "Playwright", "kind": "automation"},
    {"label": "Chrome DevTools Protocol", "kind": "automation"},
    {"label": "agent-browser / browser-use", "kind": "automation"},
    {"label": "AppleScript", "kind": "automation"},
    {"label": "launchd", "kind": "automation"},
    {"label": "GitHub Actions", "kind": "automation"},
    {"label": "ffmpeg", "kind": "automation"},
    {"label": "PIL image rendering", "kind": "automation"},
    {"label": "Google Sheets API", "kind": "data"},
    {"label": "Drive API", "kind": "data"},
    {"label": "Gmail API and IMAP", "kind": "data"},
    {"label": "Calendar API", "kind": "data"},
    {"label": "OMDb API", "kind": "data"},
    {"label": "GitHub Pages", "kind": "deploy"},
    {"label": "Cloudflare", "kind": "deploy"},
    {"label": "PWA and Android TWA", "kind": "deploy"},
    {"label": "MetaTrader 5 (EA)", "kind": "trading"},
    {"label": "Binance and PSE market data", "kind": "trading"},
    {"label": "Tizen WebSocket", "kind": "iot"},
    {"label": "Wake on LAN", "kind": "iot"},
    {"label": "Kia Connect telematics", "kind": "iot"},
    {"label": "Xendit payments", "kind": "fintech"},
    {"label": "InstaPay (PH bank rails)", "kind": "fintech"},
    {"label": "BIR (PH tax)", "kind": "fintech"},
]

HEADLINERS = [
    "{shipped} systems in production across finance, ecommerce, sales, media and trading, not demos",
    "{agents} specialized agents orchestrated across an 18 region brain map, each with a single owned job",
    "Moves real payroll and supplier money end to end through a bank UI with no public API, with readback gates and duplicate send guards",
    "CITADEL Finance OS: an 80k line custom ERP on Google free tier, approvals, ledger, payroll and a sealed bank perimeter",
    "Event driven 4 channel stock sync: one sale on any channel converts to ml and updates the other three",
    "Replaced paid SaaS with free self hosted tools: lead database, email engine, document signing, BIR certificate generator",
    "Self healing ops: failed jobs are auto filed and auto fixed, zombie processes reaped, heavy jobs queued on an 8GB machine",
    "PHOENIX persistent runner: long tasks survive usage limits and context resets until DONE",
    "Live trading bots with supervisor agents and watchdogs that catch derailment, not just crashes",
    f"ARWIN REVIEWS: {FILM_COUNT:,} film media brand with an AI predictor, review cards and cross posting on autopilot",
]


SYSTEM_CATEGORIES = [
    ("Finance and payments", "Real money moved through banks with no public API, tax and receipts on autopilot.", [
        "InstaPay batch pipeline", "SECSENDER single payment sender", "Payroll Bridge", "Messenger Bridge",
        "SecBank batch generator", "Grab invoice automation", "BIR 2307 generator + landing site", "BIR Watch", "OR/SI Drive sync"]),
    ("Business platforms and portals", "ERP, staff and supplier portals that run two companies day to day.", [
        "CITADEL Finance OS", "Pixelens Employee Portal", "Supplier billing portal", "Supplier accreditation portal",
        "Petty Cash module", "Manning Builder", "GRIDDLE, food cart operating system", "A&D Employee Portal + Android app"]),
    ("Ecommerce", "A four channel fragrance store and a food ordering site, with AI on the buy and sell side.", [
        "Curated Archive store", "Curated Archive stock sync", "Juice Meter + Deal Meter", "SCOUT demand scout",
        "Shopee blacklist watch", "PABAON order site"]),
    ("Sales and lead generation", "Self hosted replacements for paid lead tools, plus inbound lead magnets.", [
        "Pixelens Hunter", "Pixelens Lead Engine", "Pixelens Reddit lead scanner", "Client Engine + Automation Audit", "Site promo scheduler"]),
    ("Media and content", "A film media brand and creative pipelines that publish on their own.", [
        "ARWIN REVIEWS", "MARQUEE review cross poster", "REEL review card renderer", "Letterboxd growth engine",
        "Watch scheduler", "Cutsmith video pipeline", "CANVA design agent"]),
    ("AI agents and orchestration", "The multi agent layer: memory, persistence, routing, self evolution and guardrails.", [
        "PHOENIX, persistent task runner", "DGM self evolving agent loop", "Session Mesh + Knowledge Bus", "RELAY model ladder",
        "CERBERUS browser ladder", "FOREMAN production manager", "NERVE overcaution watchdog", "Watcher", "EXODUS + ARK",
        "ARCANE device sorcerer", "WRENCH car expert", "Face search", "Birthday alerter"]),
    ("Trading", "Signal agents and live bots, each with a supervisor that catches derailment.", [
        "GAB FX live forex bot + supervisor", "PSE trader + PH Stocks", "Crypto trader paper bot + manager"]),
    ("Infrastructure and reliability", "Self healing ops that keep everything above running on one 8GB laptop.", [
        "Empire infrastructure"]),
    ("Websites", "Agency, funnel, product and client sites.", [
        "Pixelens website", "Forex Funnel sites", "Client and product sites"]),
]


def categorize_systems() -> tuple[list[dict], list[dict]]:
    by_title = {s["title"]: s for s in SHIPPED_SYSTEMS}
    ordered, groups, seen = [], [], set()
    for name, blurb, titles in SYSTEM_CATEGORIES:
        items = [by_title[t] for t in titles if t in by_title]
        for item in items:
            ordered.append({**item, "category": name})
            seen.add(item["title"])
        groups.append({"name": name, "blurb": blurb, "count": len(items)})
    leftovers = [s for s in SHIPPED_SYSTEMS if s["title"] not in seen]
    if leftovers:
        print("  uncategorized:", ", ".join(s["title"] for s in leftovers))
        ordered += [{**s, "category": "Other"} for s in leftovers]
        groups.append({"name": "Other", "blurb": "", "count": len(leftovers)})
    return ordered, groups


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
    systems_ordered, system_categories = categorize_systems()

    data = {
        "meta": {
            "last_synced_utc": utcnow_iso(),
            "version": "1.0.0",
            "source": "auto generated by sync.py from production empire data",
        },
        "owner": {
            "name": "Arwin Edward M. Bagaslao",
            "callsign": "Boss",
            "headline": "AI Engineer shipping production multi agent systems that run real businesses",
            "location": "Asia / Manila (PHT)",
            "email": "arwinbagaslao@gmail.com",
            "summary": (
                f"I build AI systems that run real businesses, not demos. "
                f"{shipped_systems} systems in production across finance, ecommerce, sales and media, "
                f"orchestrated by {agent_count} specialized agents. "
                "My code moves real payroll and supplier money through a bank with no public API, "
                "runs an 80k line finance ERP on Google free tier, "
                "built event driven stock sync across four sales channels, "
                "and heals its own scheduler when jobs fail. "
                "I own the whole loop, from the business problem to the deployed and monitored system, "
                "and I replace paid SaaS with tools that cost nothing to run."
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
        "headliners": [h.format(shipped=shipped_systems, agents=agent_count) for h in HEADLINERS],
        "brain_regions": BRAIN_REGIONS,
        "empty_seats": EMPTY_SEATS,
        "citadel_ramparts": CITADEL_RAMPARTS,
        "shipped_systems": systems_ordered,
        "system_categories": system_categories,
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
