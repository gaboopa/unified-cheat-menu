# Phase 2 — Character & Relationships tabs

Fills the main menu's **Character & Genetics** and **Relationships & Family** tabs (spec 4.1, 4.2). **Not yet tested in game.**

## How it's built

- **Existing Skonester tools are linked, not copied.** "Interaction" buttons open the baseline's own right-click interaction on the target (`Character.OpenPlayerInteraction`), so they behave exactly as from the right-click menu, including their own pickers and confirmations. They're only shown when the interaction itself would be.
- To make that work, opening the menu turns on Skonester's two right-click toggles ("Open Skonester Character Tools" and "Open Cheats") and closing it turns off whichever ones it turned on. While the menu is open, the right-click menu shows those tools too.
- **New actions** are scripted GUIs in `common/scripted_guis/ucm_character_sguis.txt`. Each has an `is_valid` check, so its button is disabled when it doesn't apply (for example, Twins when the target is male).
- The menu window is now generated: edit `TABS` in `tools/gen_ucm_main_menu.py` and run it. Don't hand-edit `gui/ucm_main_menu.gui`.
- **Step size** (1/5/10/25/100) for skill and weight buttons is stored on the player as `var:ucm_step`, and defaults to 1.

## Character & Genetics

| Section | New | Linked Skonester tools |
| --- | --- | --- |
| Editors | | Trait editor, cheat trait editor, lifestyle editor, Edit Character |
| Identity | Sexuality ×4 | Change age, join your dynasty, switch character |
| Attributes | Step selector; −/+ per skill with current value; all skills −/+; weight −/+ | Super Boost |
| Traits & Genetics | | Correct personality, remove vices, add congenital traits, boost education |
| Health | Clear stress | Medical Miracle, plague immunity, immortality on/off, celibate |
| Lifestyle | | Lifestyle skill boost |
| Presets | | Paragon, Steward's Mandate, Warlord, Exemplar (and their removals) |
| Resources | | Currency menu |

## Relationships & Family

These need a second character unless noted.

| Section | New | Linked Skonester tools |
| --- | --- | --- |
| Relationships | Friend, best friend, rival, nemesis, lover, soulmate; remove all six | Set Relationship |
| Marriage | Marry, marry matrilineal, betroth, betroth matrilineal, break betrothal, divorce | Force betrothal, divorce, add concubine |
| Family | Second is father / real father / mother; join second's house | Adopt ×2, disown, designate heir, set primary heir, disinherit, annihilate dynasty |
| Pregnancy | Pregnant by second with 1/2/3 children; end pregnancy (target only) | Trigger pregnancy |
| Hooks & secrets | Strong hook either way; learn / expose the target's secrets (target only) | Gain strong hook |

## Left out

- **Debug-only Skonester interactions** (weight, quick pregnancy, learn/expose secrets, add hook, force divorce, uncelibate, restore inheritance) only appear in CK3 debug mode, which the spec says ordinary use must not need. The new native buttons cover most of what they did.
- **Baby's sex:** wrongly recorded as unsupported at the time; `set_pregnancy_gender` exists. Added in `tools/gen_ucm_extra.py`.
- **Rename character:** removed after testing. Typed text fed to `change_first_name` failed twice: first "Name is too long" even for one letter (probably the 40-character `RENAME_MAX_LENGTH` check on the raw loc text), then "Couldn't find new first name" (the text is parsed with the target as `ROOT`). A third attempt reading through `GetPlayer` also didn't rename. Not needed, so dropped.
- **Parent-loop check** only looks five generations back (`any_ancestor`).
- **Fertility, perks, lifestyle trees, modifiers, presets beyond Skonester's:** not in this pass.

## Test results

- **Working in game:** skill −/+ with step sizes (after adding `force_character_skill_recalculation`, since skills otherwise update only on the daily tick), sexuality, age.
- **Not yet checked:** the rest of the Character tab's linked buttons, and the Relationships & Family tab.

## In-game test checklist

1. Open Cheat Menu on an NPC → Character & Genetics. Skill values show numbers. Set step to 5 and press + on Diplomacy: it goes up by 5.
2. Change sexuality and weight, and check the character window.
3. Click several linked buttons (Change Age, Medical Miracle, Paragon). Each opens the same dialog as from the right-click menu.
4. Close the menu. Skonester's extra right-click entries are hidden again, unless you had them open before.
5. Set a second character of the opposite sex, then open the menu on an adult NPC → Relationships & Family: Friend, Marry, Second Is Father, Twins. Each takes effect, and buttons that don't apply are greyed out.
6. Set as father someone who's the target's own child: the button is greyed out.
7. Check `error.log` for `ucm_` lines.
