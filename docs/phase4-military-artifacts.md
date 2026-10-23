# Phase 4 — Military, Artifacts and always-on cheats

Fills the **Military & Warfare** and **Artifacts & Equipment** tabs (spec 4.6, 4.7), and adds the baseline's always-on cheats to **Quick Actions** (spec 8.3). Static checks pass. **Not tested in game.**

## How it's built

New button type: **Crozier panel buttons** (`("cz", name)` in `tools/gen_ucm_main_menu.py`). The generator copies the baseline's own button for `ucm_crozier_cheats_sg_<name>` from the character window's cheat panel (`gui/window_character.gui`), including its label, tooltip, on/off state and the strength value it shows, and points it at the menu's target instead of the window's character. A change to the panel button shows up in the menu after re-running the generator. `("czrow", …)` does the same for small buttons side by side, such as the strength and tier selectors.

New scripted GUIs are in `common/scripted_guis/ucm_military_sguis.txt`.

## Quick Actions: Always-On Cheats

The panel's strength (1–7), tier (1–3) and frequency (week/month/quarter) selectors, all on / all off, and all 30 timed cheats: income, monthly gold, domain, vassals, prestige ×2, piety, renown ×2, influence, merit, legitimacy, health, stress, life, immortality, disease immunity, long reign, skills ×2, lifestyle XP, innovation, building slots, travel safety, legend spread, the gold and prestige floors, no prison, auto-ascension, forever young. Levies is in Military. These apply to **you**. Since spec 1.3 they stop in multiplayer (Phase 1 gate).

## Military & Warfare

| Section | Contents |
| --- | --- |
| Armies | Army spawner; spawn house guards (5,000 / 2,000); horde army; dream army; levies +100% toggle; teleport your armies to the target's capital |
| Target's Armies | Remove their commanders, destroy a share of their raised troops, empty their supplies |
| Knights | Knightly honour, accolade glory, Grand Marshal, force or remove the target as a knight |

## Artifacts & Equipment

| Section | New | Linked |
| --- | --- | --- |
| Editors | | Artifact workshop, artifact editor |
| Target's Artifacts | Repair all; make all illustrious | Bestow, take, claim, destroy, generate with history, summon, borrow; rob all their artifacts; claim all their artifacts |
| Your Artifacts | | Forge the Crown of the Sovereign; artifact decision |

## Not done

- **Spec items with no baseline or engine support found:** per-regiment editing (expand, reinforce) and per-artifact modifier editing beyond the workshop and editor.
- **Artifact presets** (Legendary Warrior and the like) aren't added. The workshop's own presets cover crafting.

## In-game test checklist

1. Quick Actions: set strength 3, switch on Income. The button turns to ON. Wait a month and check income.
2. Military: Dream Army on yourself raises men-at-arms. Empty Their Supplies on an enemy ruler at war works.
3. Artifacts: on a character with damaged artifacts, Repair All restores durability.
4. Check `error.log` for `ucm_` lines.
