# Phase 5 — Court, DLC & Advanced, Settings tabs

Fills the **Court & Character Generation**, **DLC & Advanced Systems** and **Settings & Utilities** tabs (spec 4.8, 4.9). Static checks pass. **Not tested in game.**

New scripted GUIs: `common/scripted_guis/ucm_court_sguis.txt`.

## Court & Character Generation

| Section | Contents |
| --- | --- |
| Character Generation | Character spawner, spawn character / menu, spawn male or female courtier, spawn courtier, child now / child with me (panel) |
| Court Members | Join court ×2, send courtier, invite as guest (panel), antagonize court, group action: clear stress for every courtier |
| Council & Court Positions | Appoint the target as chancellor, steward, marshal, spymaster, court chaplain, court physician, tutor, bodyguard, champion, master assassin or royal architect (panel); change or finish council tasks |
| Court Tools | Court purge & recruit, court position reshuffle, talent finder, bulk guardians, the three cure decisions (decisions, act on you) |
| Prison & Hostages | Imprison, quick imprison, take or free hostage, family hostages (panel) |
| Removal & Death | Retire or depose, depose (panel), banish (panel), murder, slay, execute (panel), suicide. Labelled as not undoable. |

Automated court appointments and court cleanup (spec 4.8) are the baseline's court decisions above. No new automation was added.

## DLC & Advanced Systems

| Section | New | Linked |
| --- | --- | --- |
| Regencies & Diarchies | Start regency / co-monarchy / vizierate for the target; second character becomes the diarch; power swing −/+ by step; end diarchy | |
| Schemes | | Buff, complete, clear agents, infinite schemes; end or expose the target's schemes (panel) |
| Inspirations | | Inspire, sponsor |
| Legends | | Legend seeds; legend spread always-on (panel) |
| Activities | | Duel or board game, hunt success, tournament score, pet story, coronation law and guests |
| Domiciles & Adventurers | | Move domicile, make adventurer, task contracts, patrons, travel to ruler, arrive now (panel) |
| Epidemics | | Spawn epidemic; give the target any of eight diseases (panel) |
| Struggles & Cycles | | Dynastic cycle, Silk Road, mandala, Great Steppe, nomad mandate, Ming currency |
| Events & Debugging | | Debug event menu, effect localization test |

Many of these baseline interactions are debug-only. Their buttons only appear with CK3's debug mode on, which the Settings tab can toggle.

## Settings & Utilities

- **This Menu:** clear second character; reset menu (also resets step to 1).
- **Classic Menus:** the original event-based main menu, the decision sub-menu editor and the mod information decision.
- **Debug Mode:** debug mode helper.

## Not done

- **Spec 4.9 activity costs, phase skipping and inspiration completion:** no baseline tools were found beyond the linked interactions. The classic event menu has activity cheats.
- **Government-specific systems** beyond those listed are reachable through the classic menus.

## In-game test checklist

1. Court: appoint an NPC as chancellor from the menu. They take the seat.
2. DLC: on an adult NPC ruler, Start Regency → Make Second Character the Diarch. Their diarchy shows the second character.
3. Settings → Classic Menus: the event main menu opens.
4. Check `error.log` for `ucm_` lines.
