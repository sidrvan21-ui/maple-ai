# Part 0 — Porter research dump

## Plain English

We did **not** build the Maple app yet. We simulated a real product team’s messy fieldwork for **Porter** (Vancouver-first building concierge: instant alerts + daily / weekly / monthly digests).

77 markdown files live in nine folders. They disagree on purpose. Maple will admit **one folder per HITL gate**, as if the next pack of research just arrived.

## Why it exists

Agentic RAG looks powerful only if it has many documents to decompose, grade, and contradict. One clean mega-file would either leak Stage 9 into Discovery or give the model nothing to do.

No SQL in this corpus. Numbers hide in memos and markdown tables. SQLite is for Maple’s checkpointer later, not for Porter evidence.

## What we created

Root: [data/raw_inputs/README.md](../../data/raw_inputs/README.md) — cast, fights, folder list.

| Folder | Count | What a real team would have dumped |
|---|---|---|
| `s1_discovery/` | 13 | Interviews (Priya, Marcus, Helen, Derek, Antoine), incomplete VoC, desk research, BuildingLink/Flagship notes, Slack, two conflicting TAM scraps, PIPA notes |
| `s2_strategy/` | 8 | Pricing fight, Ansoff, LTV napkin, AGM seasonality, digest capability, Maya “don’t be BuildingLink” email, BMC stickies, unapproved OKRs |
| `s3_scoping/` | 8 | Feature dump, messy RICE inputs, push-fatigue, PIPA musts, Now/Next/Later, MoSCoW Slack fight, stories, Kano |
| `s4_development/` | 8 | Sprints, push defects (P-23 title leak), Vancouver TZ bug, Cooper + Cedar usability, Helen change request, beta questions, standup |
| `s5_qualify/` | 8 | Two beta diaries, unit-roll blocker, Derek PM pain, PIPA checklist, go/no-go email, bad sales one-pager, support |
| `s6_launch/` | 8 | Day-0 (2026-09-09), open-rate **markdown table**, store quotes, missed alerts, war room, honest demand-gen, Slack, first-week status |
| `s7_growth/` | 8 | Cohorts (7 buildings), 07:30 vs 18:00 A/B, PLG almost failed, AARRR, experiment log, WeChat hole, referral, risks |
| `s8_maturity/` | 8 | Cost/building, NPS-ish quotes, “we became email again,” second SKU temptation, debt, support load, portfolio, finance cousin |
| `s9_sunset/` | 8 | **Kill SMS add-on, not Porter Notice**, churn, contract clause, 90-day letter, PIPA export, decline narrative, migration, EOL RACI |

## Cast (memorize — they persist across stages)

- **Priya Sharma** — renter, The Cooper, Yaletown. Wants 07:30 daily. Muted WhatsApp (214 unread).
- **Marcus Chen** — owner, Village Lofts, Olympic Village. Daily OFF. Monthly finance. Per-door $2.50–4.
- **Helen Okonkwo** — Cooper president. **184 + 6 CRUs**. Hates per-door. Year-1 cap $1,200. No unit numbers in blasts (PIPA).
- **Derek Walsh** — Cascade PM. Loves BuildingLink. Will not rip it. Magic link or he walks.
- **Antoine Leclerc** — Shoreline concierge. Fat button. Packages out of wedge.
- **Gita** — Cedar & 10th, Mount Pleasant, no desk. Backup publisher after Kelowna week.
- Internal: **Jules** (research), **Samir** (privacy-ish), **Mina** (design/support), **Nikhil** (eng), **Ravi** (founder, 248k TAM, “concierge” branding).

## Intentional fights (do not average)

| Fight | Sides |
|---|---|
| Cooper size | Priya ~160 / Derek sheet 180 / Helen **184** |
| TAM | Ravi **248k** apartments / Derek 170–190k / Samir **90k ± 20k** managed doors |
| Price | Helen flat building / Marcus per-door / Ravi $3.50 × 248k |
| Daily digest | Priya ON / Marcus OFF / Helen will not write it (compile only) |
| BuildingLink | Derek keep / Helen never |
| Stage 9 | Sunset **SMS Instant SKU**, Porter Notice survives |

## How we made it

Hand-authored markdown (not `generate_lifecycle_data.py` yet). Same people and buildings reused so agentic RAG can cite across stages. Voice is Slack, interviews, emails, incomplete drafts — not polished PRDs.

## Interview script

**Q: Why not one file?**  
A: Stage-gated admit. One file leaks the future or forces fake splits. Agentic RAG needs many docs to decompose.

**Q: Why no SQL?**  
A: The demo is “can the agent read a research dump?” SQL can come later as a tool. Discovery must work on transcripts alone.

**Q: What’s the beachhead?**  
A: Vancouver, 80–400 unit stratas. Dual buyer: resident + council/PM. Wedge is notification reliability + digest cadence, not BuildingLink.

**Q: What’s the privacy constraint?**  
A: BC PIPA. Strata is controller, Porter is processor. No unit numbers in blasts.

**Q: What does approve do to this data?**  
A: Unlocks the next folder. Later nodes still see prior folders. Signed artifacts get indexed only after HITL.

## Gotchas

- Cooper is not managed by Derek personally (Cascade firm, assigned manager “Pat”). Easy to conflate.
- Marcus’s building (Village Lofts) is **not** a beta. He is research only. Growth file even jokes we aren’t in his building.
- Ravi’s 248k is dwelling stock, not SAM.
- Stage 9 is a **feature** EOL, not company death. If the sunset node shuts Porter Notice, it misread the folder.

## How to demo (today)

Open `data/raw_inputs/s1_discovery/` and read Priya vs Helen vs the two TAM scraps. That is the Stage 1 corpus.

## On to next

Part 1 — empty building: FastAPI, Next stub, Docker Compose, OpenAPI, JWT role stub. No RAG yet.
