# DESIGN.md: POLARIS

Direction for the POLARIS dashboard ("consoles" for Babak 1) and the landing page.
Written before the UI, not after. Filter applied on top: `antislop.md` + skill files.

## Design Read

> Reading this as: a **situational-awareness console** for **SOC operators / TNI AD cyber
> personnel** working an IT/OT network, in a **dense instrument-panel** language (think
> an operations console, not a SaaS marketing site), dial **ENERGY 2 / RHYTHM 2 / MOTION 2**.

## Why this is not a generic admin dashboard

The product's whole argument is *"a sensor nobody trips by accident"*. The interface
therefore has to read like an **instrument**, not a dashboard template: flat, dense,
one alert at a time in focus, no decoration competing with the incident.

## Dials

| Dial | Value | What it buys |
|---|---|---|
| ENERGY | 2 | Says hello through the **incident**, not through decoration. Header is quiet; the alert list is loud. |
| RHYTHM | 2 | Three panels with **different widths and different internal composition** (a raw feed, clickable incident cards, an aggregate profile column). Not one repeated card grid. |
| MOTION | 2 | Hover and focus transitions only, plus a **single attention cue** when a new incident lands. No loops, no float, no parallax. Honours `prefers-reduced-motion`. |

## Palette

Two scales, kept deliberately separate:

1. **Identity scale** (this is the brand): charcoal neutrals + **one accent, teal `#5eead4`**.
2. **Semantic scale** (system status, not brand): the standard severity traffic ramp.

Keeping them separate is the reason a red badge never gets mistaken for the accent, and
the reason the accent can be reserved for interaction only.

| Token | Hex | Use | Contrast (computed) |
|---|---|---|---|
| `--bg` | `#0e1116` | page | |
| `--panel` | `#161a20` | panel surface | text `#e9edf2` = 14.85:1, muted `#9aa5b1` = 6.98:1 |
| `--panel-2` | `#1c2128` | card / row surface | muted = 6.47:1 |
| `--line` | `#2b323c` | decorative separation between static panels | non-control, see note |
| `--line-strong` | `#647082` | boundary of **interactive** cards | 3.48:1 vs `--panel` |
| `--text` | `#e9edf2` | primary text | 14.85:1 |
| `--muted` | `#9aa5b1` | secondary text | 6.98:1 |
| `--accent` | `#5eead4` | focus ring, live state, active selection **only** | 11.80:1 |
| `--sev-critical` | `#ff6b6b` | severity | 6.29:1 on panel; `#ff7b7b` on tint = 7.05:1 |
| `--sev-high` | `#ff9f43` | severity | 8.56:1; on tint 8.87:1 |
| `--sev-medium` | `#e8c547` | severity | 10.40:1; on tint 10.00:1 |
| `--sev-low` | `#6ddb8f` | severity | 10.13:1; on tint 10.21:1 |

Verified with `antislop-human/scripts/contrast-check.py`, not by eye.

**Note on `--line` (1.32:1).** WCAG 1.4.11 asks for 3:1 on information needed to identify
*components and states*. Static panels are separated by surface colour plus layout, and a
quiet hairline reads as decoration, so it stays subtle by intent. Anything a user must
*operate* (incident cards, buttons, inputs) uses `--line-strong` at 3.48:1 or the accent.

## Typography

- **UI face:** system UI stack (`ui-sans-serif, system-ui, "Segoe UI", Roboto`).
  Reason: the console runs on whatever operator machine is at hand, including air-gapped
  boxes where a webfont may not be reachable. A system face is the honest choice, and it
  keeps the binary small.
- **Data face:** `ui-monospace` for IPs, ports, hashes, MITRE IDs.
  Reason: these are compared character by character; monospace prevents misreading.
- No wide-tracked uppercase as a default. Micro-labels are lowercase with small tracking
  (0.02em) because the console already carries density; uppercase was adding noise.
  Uppercase survives in one place only: the severity status word, where shouting is real
  information.

## Radius / elevation / glow (dose caps)

- Radius scale `4 / 8 / 12` plus one pill (`999px`) for status chips only.
  Reason: the pill is a status affordance, not a shape for every element.
- Shadow: **none** anywhere. The console is a flat instrument; elevation is not part of
  the model. Hierarchy comes from surface colour and border weight.
- Glow: **one** place, the CRITICAL incident stripe and its surface tint, because severity
  is the one thing allowed to grab attention. No glow on the logo, header, or panels.

## Emblem

A hexagon outline with a single dot at the centre, drawn inline as SVG in `currentColor`.
Reason: the hexagon reads as an industrial/OT cell; the dot is the decoy point an intruder
cannot resist touching. It is geometric on purpose, not a stock sparkle/diamond glyph.

## Theme

Dark only, and that is a decision with a reason: this screen is used in a monitoring room,
often at night, next to other dark consoles. It is not "dark because tech". No toggle is
shipped, so R-34 has nothing to break.

## Copy rules for this project

- No em dash. Use commas, colons, or parentheses.
- No marketing adjectives. Severity is stated, not sold.
- Every number on screen comes from the running system (event counts, scores, ports).
  Nothing is hardcoded for looks. Where a value is a placeholder it is labelled as one.

## References (observed, then filtered)

Pulled with the Awwwards MCP (`search_sites`, `get_site_details`, `create_design_brief`).
These are grammar sources, not templates. Nothing is copied wholesale.

| Reference | What was observed | What we took | What we deliberately did not take |
|---|---|---|---|
| **CROX** `crox` (precision engineering studio) | Tiles joined by one seam, nameplate type, numbers placed before adjectives, a `SYSTEM STATUS` label/value block | The **seam-joined tile grid** (1px seam, no gaps, no per-card border), the **nameplate** wordmark with a rule, **value-first readouts**, and the spec-sheet label/value rows | Their off-white/black-orange palette and their decorative wireframe grid (R-07) |
| **Rubens Cantuni** `rubens-cantuni-1` | A computing-era timeline where a monospace pane shows tabular rows | The **dense monospace log row** with a row index and aligned time column | Their retro chrome, window frames, and era-switching gimmick (would be decoration here) |
| **.txt** `txt` | Terminal-as-interface, rows rather than cards | **Row-based** incident list instead of floating cards, with hairlines as the only separator | Their black/white high-contrast marketing layout and page transitions |

Convergent signal across the set: **structure carries the identity, not ornament**. That is
the reason this console has no shadow, no glow, no gradient, and no rounded floating cards.

## Change log (kept short on purpose)

1. Blue/cyan "tech" palette and gradient logo glow removed. Replaced with the charcoal
   plus single teal accent above, because the earlier version was the default AI look (R-01, R-20).
2. Three floating rounded cards replaced by seams, because the console should read as one
   instrument and gaps were doing no work (borrowed from `crox`).
3. Stat readouts reordered to value-first, because an operator reads the number and only
   then the label (borrowed from `crox`: numbers before adjectives).
4. Incident entries changed from decorative cards to rows with a leading score number,
   because the list is scanned, not admired.
5. MITRE techniques grouped by tactic, because a flat 12-chip wall is unreadable.

