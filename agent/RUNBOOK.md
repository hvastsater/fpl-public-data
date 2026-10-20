# FPL-agent 2.0

Owner: entry 6273717, league 1286090. Timezone Europe/Stockholm.
Never log in to FPL, change the team, buy services or request passwords.

## Source permission gate
The 2026-10-20 review found FPL terms prohibiting automated extraction:
https://fantasy.premierleague.com/help/terms
Public accessibility is not a licence. Do not run or expand collect.py until
written permission or a properly licensed replacement is documented.
The owner approved the pause on 2026-10-20. PR #1 was merged and the refresh
job is now gated off. The three analysis Tasks remain enabled.
Do not use a mirror as a workaround for extraction restrictions.
Use user-supplied material and permitted published editorial research meanwhile.
Do not publish raw licensed datasets or private account information here.

## Every run
Read this runbook, the latest saved decisions and delivery records first.
Verify source timestamps, season, event IDs and the actual official deadline.
Convert with Europe/Stockholm, never a fixed UTC offset. A generated timestamp
alone does not prove that underlying picks, standings and scores are aligned.
Run `python scripts/agent.py docs/latest.json` for an offline consistency audit.
An audit pass does not establish source permission or current bank/FT.
For final calls, require decision-critical team news checked in the last hour;
record actual publication and retrieval timestamps, not an invented fresh date.

## Analysis requirements
Separate facts, projections and analyst judgment. Record missing data explicitly.
Check official club news, injuries, suspensions, training, press conferences,
expected minutes/rotation, penalties/set pieces, xG/xA, shots and big chances,
European/cup workload and rest days, price risk, fixtures over 3–8 GW,
multiple independent models and expert opinions. Never label a ranking formula
as calibrated expected points or several copies of one source as consensus.
Compare ROLL and multiple affordable transfer packages; include hits and the
option value of retained FT. Missing bank/selling prices means conditional plans.
Prioritize long-run points with controlled variance around league ranks 3–7.
Do not chase Theo solely because of his lead. Use minutes and rival captain
exposure to break near-ties. Distinguish squad ownership, start ownership,
realized EO (multipliers/N) and predicted EO. Never infer current rival transfers
from last deadline's public picks. Free Hit squads are temporary, not permanent
transfer histories. Do not call one good realized outcome a good decision.

## Decision memory
Store recommendations under agent/decisions/SEASON/gwNN/PHASE-vNNN.json.
Use initial-v001.json as the shape reference. Never rewrite a past recommendation:
new evidence creates a new revision referencing its predecessor. Freeze alternatives
before deadline; distinguish originally recommended and subsequently executed moves.
Use null for unobserved xP, bank, FT, prices and execution, never zero or guesses.
Each final record needs strategy, exact transfers or ROLL, legal XI, bench 1–3,
bench GK, C/VC, chip or none, contingency and 3–8 GW consequences; validate 15 unique
players, 2 GK/5 DEF/5 MID/3 FWD, max 3 per club, legal XI, costs and selling values.
Conditional advice is not unconditional GO.

## Scheduling and notifications
Retain the three existing Tasks. Pre-analysis is due at 18–30h before deadline;
final at 1–2h. On a delayed final run inside 1h, send a clearly late update once
if still useful and before deadline. Never send GO after deadline.
After-analysis requires both finished and data_checked, not merely last kickoff.
Each run starts by looking for agent/delivery/SEASON-gwNN-PHASE.json and its own
chat delivery history. If sent, remain silent unless material new information
requires a distinctly versioned correction. Record completed delivery only after
delivery is confirmed; keep pending claims separate. GitHub and notifications
are not one atomic transaction: exact-once delivery cannot be guaranteed.
If write access fails, use the same task's delivery history as fallback, disclose
the persistence failure in the substantive report and do not send routine alerts.
Pre-analysis also handles meaningful early price/injury alerts with a stable
news-event key; do not create another recurring task. No change means silence.

## Evaluation
With an authorized, finalized snapshot:
`python scripts/agent.py SNAPSHOT --decision DECISION --output NEW_REVIEW.json`
Never overwrite a review; corrections are versioned. The offline evaluator
records actual gross/net points, hits, rank, picks and chip. It waits for official
finalization and leaves missing counterfactual outcomes null. Resolved effective
alternative picks must use real minutes, legal autosubs, captain fallback and
chip rules before scoring. Do not use raw predicted XI multipliers as realized
multipliers. Transfers must include selling prices and future budget feasibility.
Add nearest-rival relative changes only from two matching finalized GW snapshots.
Review forecast error, minutes error, selection quality and luck separately;
compare pre-registered alternatives, not retrospectively invented optimal teams.
Append actionable lessons with supporting decision IDs and confidence.

## Known limitations at installation
Only one successful collector run was returned by Actions history, at 04:54 UTC
2026-10-20. Current code is newer than that snapshot. No end-to-end scheduled
GitHub write or notification has yet been observed. No permitted replacement
feed, calibrated projection model or fully automated counterfactual simulator
is configured. This is a guarded decision/evaluation foundation, not a finished
autonomous data service.

## Low-effort team continuity (20 October update)
Do not request a weekly screenshot by default. Maintain the last explicitly
confirmed squad and an append-only execution log. A user reply 'gjort' confirms
only the unambiguous latest exact recommendation; never assume a recommendation
was executed from silence. If multiple alternatives exist, clarify which one.
Carry forward unchanged players and track confirmed transfers/chips. FT and bank
may be derived only from a verified baseline, confirmed execution, exact selling
prices and verified current season rules; label derived versus observed values.
Ask a short text question only when missing state changes the recommendation.
A screenshot is optional fallback for a contradiction, not the weekly workflow.
This does not solve automatic fresh rival squads or verify unreported transfers.

FPL Cat is a candidate independent projections source. Its developer page and
terms explicitly allow personal API use: https://fplcat.com/developers and
https://fplcat.com/terms (reviewed 2026-10-20). Use its own forecasts with attribution,
not as an FPL raw-data mirror or proof of current user holdings. The API URL read
failed in this session, so integration is not yet tested or configured.
Plugin discovery found no relevant FPL plugin; this is not an exhaustive claim
about the directory. Play Index advertises read-only squad and league tools, but
source permissions and available access have not been verified; do not connect
or recommend it as an approved solution yet.
