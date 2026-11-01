# Phase 12: Features recreated from the gap review

A comparison against the baseline mod (`bfcb175`) and Divine Intervention v0.4.0 found features UCM lacked or couldn't reach. They are rebuilt here as native menu actions. DI was used as a behaviour reference only. Static checks pass. **Not tested in game.**

`tools/gen_ucm_extra.py` generates the actions, and `gen_ucm_main_menu.py` merges them into the tabs. Run them in that order. The modifier list comes from `modifiers.log` (`script_docs`), so regenerate it after a game update with `CK3_LOG_DIR` set if the logs aren't in the default place.

| Tab | Added |
| --- | --- |
| Character | Modifier editor window (536 modifiers in 8 categories, stacking + and −, clear all); stress, dread, tyranny, legitimacy and fulfillment steps; visual age presets; five locks; resource editor |
| Relationships | Baby's sex, remove hooks, make house head, plant secrets |
| Titles | Remove claims, de jure tools, destroy primary title (confirm), Ecclesiastical and Wanua, permanent truce, win/lose/peace outcomes, declare war by tier |
| Faith & Culture | Personal tenet picker window, copy/remove/clear tenets, learn or join a rite, make cardinal, divergent culture, acceptance steps, innovations by era or all |
| Realm | Capital county control, development and modifiers; move realm or county capital; remove holdings (confirm); building slot; AI build; +/− for each standard building chain |
| Court | Group actions for lovers, friends, rivals, extended family, house bloc, faith and culture, plus prestige and piety; spawner with age, count, sex, traits, skills, genes and immortality; child, sibling, parent, spouse, courtier, lowborn, commander, knight, councillors, every court position |
| DLC | Skip, finish or cancel an activity; estate presets; 45 legends; clear legends |

## Known limits

- **No county or barony picker.** Capital moves choose at random. County and building actions apply to the target's capital.
- **"Treaties"** are 9,999-year truces. The engine docs list no treaty effect.
- **Finish activity** skips up to 8 phases. There is no complete-activity effect.
- **Declare war** uses the mod's own `sol_expansion_war*` casus belli, not a picker over every CB.
- **Elder Kings 2:** `compat/ek2/` greys out the building, innovation-era, legend and court-position buttons, because they use vanilla keys. Its tenet picker uses the EK2 list.
- **Turkish** text stays English: CK3 1.20 has no Turkish language.

## In-game test checklist

1. Load with this mod alone, then check `error.log` for `ucm_` lines. Watch for unknown modifier keys: some tags in `modifiers.log` may reject the values used.
2. Open the menu and both side windows. Check that they sit beside the menu and that the Realm tab scrolls smoothly.
3. Modifier editor: click + twice on one modifier and confirm it stacks, then − and Clear All.
4. Baby's sex on a pregnancy already under way: check the child's sex at birth.
5. Buildings: + twice on one chain, then −. Check whether the level drops or the building disappears.
6. Locks: check that legitimacy and fulfillment really stop changing.
7. Spawner: child, sibling, parent and spouse with Count 2, then a councillor and a court position.
8. Group actions: house bloc and culture counts look right, and the culture group doesn't stall the game.
9. Tenet picker: add a tenet, click again to remove it.
10. With EK2: greyed buttons cause no errors.
