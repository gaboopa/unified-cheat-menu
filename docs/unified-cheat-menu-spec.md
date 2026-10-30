# Unified CK3 Cheat Menu

**Proposed Functional and Interface Specification — Version 1.3**

**Target:** Crusader Kings III 1.20.x "Crozier" (verified against 1.20.1.2 game files)\
**Baseline:** started from Skonester Cheat Menu Gold at upstream commit `bfcb175` (CC BY 4.0), since heavily rewritten\
**Feature reference:** Daddy Pika's Cheat Menu / Divine Intervention (behavior only; no code or assets)\
**Status:** Phases 0–7 implemented, followed by review, upstream-cleanup and simplification passes (Phases 8–11) and an Elder Kings 2 compatch (`compat/ek2/`, [ek2-compatch-plan.md](ek2-compatch-plan.md)). See the phase notes in docs/. Most features still need in-game testing; Phases 9–11 and the compatch haven't been load-tested yet.

This document is the original design. Where later phases changed or dropped something, the text says so; the phase notes record what was actually built.

### Changes from 1.2

- **No pins.** Removed pin lists, pinned titles, the Character A/B/C slots, the Selection Manager, and the Bulk Editor window. Every action applies to what you right-clicked, plus at most **one saved second character** for two-character actions.
- **Group actions instead of bulk selection.** Actions can apply to built-in groups taken from the clicked target, such as your vassals or your realm's counties (Section 5).
- **Single-player only.** The menu is disabled when another player is connected (`has_multiple_players`). The multiplayer-safety requirement and the plan to move per-player global variables onto the player's character are dropped.

### Changes from 1.1

Corrections from the game's own `script_docs` output (1.20.1.2), which replaces the earlier file-search evidence:

- **Rename character was back in scope** because `change_first_name = <dynamic_description>` exists. It was later dropped after failing in game (Appendix A).
- **Script can loop over many database types:** traits, innovations, traditions, tenets, doctrines, government types, holding types, court position types, and more. Pickers for these build their lists at game start, so modded content appears automatically. Buildings, men-at-arms types, and artifact templates still have no loop and keep generated lists.
- Added rename for cultures, faiths, and rites (`set_culture_name`, `set_faith_name`, `set_rite_name`).
- Clarified that `set_immortal_age` only works on characters who are already immortal, and that `personal_tenet_slot_add` is a modifier, not an effect.

### Changes from 1.0

- Removed **Rename character** (no character-rename effect exists) and **Set offspring sex** (no supported parameter).
- Pickers now use **generated lists** instead of reading the game's definitions at runtime.
- Rewrote the Faith Editor for the 1.20 Faith → **Rite** model and limited tenet-slot claims to what's been verified.
- Added **multiplayer-safe targeting**: per-player state lives on the player's character, not in global variables.
- Added a **vanilla override inventory**, a **global defines** review, and an **error.log baseline** to Phase 0.
- Settled licensing: Skonester is CC BY 4.0.
- Added Appendix A (engine verification evidence) and Appendix B (baseline audit).

---

## Design direction

Take Skonester's character-interaction workflow, organized submenus, and convenient one-click cheats as the starting point, and add Divine Intervention's more advanced editing capabilities.

Use a hybrid interface rather than merging both mods' menus wholesale. Most actions stay accessible by right-clicking a character, as in Skonester. More complicated operations, such as artifact construction and detailed diplomacy, open dedicated editors without requiring a separate permanent HUD.

This specification is a proposed design. It doesn't claim these features already work together.

---

## 1. Project objectives

Create a comprehensive CK3 cheat menu that keeps Skonester's convenient character interactions and organized menus and adds the advanced controls associated with Divine Intervention.

The resulting mod must work standalone. Players shouldn't need to install either original mod.

### 1.1 Governing requirements

1. **Preserve existing functionality.** All working Skonester features stay accessible and keep their existing behavior unless deliberately improved.
2. **Interaction-first design.** Right-clicking characters remains the primary entry point. Dedicated GUI windows are used only where they substantially improve complex editing.
3. **Context-aware actions.** The menu identifies the relevant character, realm, title, culture, faith, or other target automatically.
4. **Minimal clutter.** Don't flood the normal character interaction menu with hundreds of cheats.
5. **Comprehensive coverage.** Support all ten feature categories, including advanced DLC systems.
6. **Click to target, groups for scale.** Every action applies to the thing you right-clicked. Actions on many targets use built-in groups derived from it, never a manual selection list.
7. **Explicit targeting.** Every operation clearly identifies who or what will be modified.
8. **No silent destructive actions.** Dangerous operations require confirmation and disclose their scope.
9. **Modular implementation.** Organize functionality into independently maintainable modules.
10. **Compatibility awareness.** Account for game version, installed DLC, government types, and content supplied by other mods.
11. **Single-player only.** It's a cheat mod. All entry points (interactions, decisions, windows) are hidden while `has_multiple_players = yes`, and persistent cheats stop applying.

### 1.2 Preservation policy

Inventory existing Skonester functionality against the forked baseline before development begins.

Reuse working features where appropriate rather than reimplementing them unnecessarily.

Features to preserve include:

- Six-attribute editing, age modification, trait editing, lifestyle editing, and existing cheat traits.
- Character and family generation, marriage manipulation, and existing character interactions.
- Resource cheats, realm authority, succession editing, and title management.
- Culture and faith editors, including expanded tenet functionality.
- Army spawning, unlimited levies, infinite supplies, and military god mode.
- Existing artifact crafting, editing, repair, and modifier-stack functionality.
- Court management, automated appointments, and realm construction tools.
- Estate editing, legends, activities, and existing DLC functionality.
- Existing localization (English, German, Russian, Simplified Chinese, Turkish) and compatibility mechanisms.

A feature isn't preserved just because its menu entry is still visible. Its behavior must also pass regression testing.

---

## 2. Overall menu architecture

The interface uses three layers.

### Layer 1 — Character interactions

When you right-click a character, you see a compact set of cheat entries.

**Default visible interactions:**

- **Open Cheat Menu** opens the main categorized menu for the selected character.
- **Quick Cheats** opens commonly used immediate actions.
- **Set as Second Character** saves the character for two-character actions (Section 3.1).

Players who prefer more direct shortcuts can enable additional entries in Settings.

Ordinary cheat operations must not require debug mode.

### Layer 2 — Main categorized menu

The main cheat menu shows:

**Target:** Clicked character\
**Player:** Current playable character\
**Second character:** None

**Main Menu**

1. Quick Actions
2. Character & Genetics
3. Relationships & Family
4. Titles, Government & Diplomacy
5. Faith & Culture
6. Realm, Holdings & Construction
7. Military & Warfare
8. Artifacts & Equipment
9. Court & Character Generation
10. DLC & Advanced Systems
11. Settings & Utilities

Group actions (Section 5) live inside the category they belong to. For example, "Max development in every realm county" is under Realm, Holdings & Construction, not in a separate menu.

Each category opens a focused submenu. Complex categories may open a dedicated GUI editor.

Layer 2 is a single custom window with tabs, opened from the Layer 1 interaction. Skonester already uses this pattern (`common/character_interactions/01_ucm_gui_launcher_interactions.txt`). Skonester's existing decision-based menus stay available during migration.

### Layer 3 — Specialized editors

Use dedicated editing windows for operations that involve large lists, many values, or several interacting targets.

| Editor               | Intended functionality                                             | Skonester starting point                       |
| -------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| Character Editor     | Skills, traits, genetics, health, sexuality, age, perks, modifiers | `ucm_trait_editor.gui`, `ucm_lifestyle.gui`, `ucm_cheat_trait_editor.gui` |
| Relationship Editor  | Clicked and second character: relationship status, family relationships | None                                      |
| Title Manager        | Clicked title: de jure editing, claims, transfers                  | None                                           |
| Culture Editor       | Traditions, pillars, innovations, conversions                      | `ucm_acm_culture_picker.gui`, `ucm_culture_tradition_picker.gui` |
| Faith Editor         | Rites, tenets, doctrines, sins, virtues, conversions               | `ucm_acm_faith_editor.gui` and related pickers |
| Construction Manager | Holdings, building chains, building slots                          | None                                           |
| Army Manager         | Unit types, quantities, regiments, combat modifiers                | `ucm_sand_soldiers.gui`                  |
| Artifact Workshop    | Artifact creation and editing                                      | `ucm_artifact_craft.gui`, `ucm_artifact_repair.gui` |
| Character Generator  | Family, council, court, and custom character generation            | Existing generation interactions               |

Editors must not become a competing navigation system. Each editor keeps its parent menu context and has an obvious way back.

---

## 3. Shared interface behavior

### 3.1 Targeting system

All actions use one simple targeting model: **you click the thing you want to change.**

**Targets:**

- **Clicked target:** the character you right-clicked, or the title, county, culture, or faith you opened the menu from.
- **Self:** the current player character, only when an action explicitly says so.
- **Second character:** one saved character for actions that need two (marriage, relationships, transfers, wars between two NPCs). Right-click a character and choose **Set as Second Character**. It stays saved until replaced or cleared, and is cleared automatically if the character dies.
- **Group:** a built-in group derived from the clicked target, such as your vassals or your realm's counties (Section 5).

There are no pins, saved selection lists, or extra target slots.

The current player character and the clicked target must never be silently swapped for each other. Every two-character action shows both names before it runs.

**Storage:** Because the mod is single-player only (Section 1.1, requirement 11), menu state can stay in global variables, as the baseline does (`ucm_crozier_cheats_other` already holds the second character). No migration is needed.

### 3.2 Navigation consistency

Every submenu provides:

- Back to Previous Menu
- Back to Main Menu
- Close Menu
- Current Target (and second character, if set)
- Action-specific tooltips

Where a group version of an action exists, it sits next to the single-target version (for example, "Max development" and "Max development in every realm county").

### 3.3 Adjustable values

Numeric operations use consistent controls.

Common increments: **±1, ±5, ±10, ±25, ±100**

Some operations need their own increments or presets.

Use buttons and increment selectors. **Typed numeric input isn't available:** CK3's text-entry widget stores a string for display in localization, and script can't read that string as a number (Appendix A).

### 3.4 Confirmation policy

| Action type              | Behavior                                                        |
| ------------------------ | --------------------------------------------------------------- |
| Low-risk                 | Execute immediately and display a short result                  |
| Significant              | Display target, old value, new value, and confirmation          |
| High-risk                | Require explicit confirmation and provide a consequence warning |
| Group                    | Show the group, affected count, skipped count, and a confirmation |
| Potentially irreversible | Clearly state that restoring a save may be necessary            |

An in-game history may record completed actions, but it must not imply that all CK3 effects can be undone.

---

# 4. Detailed feature specifications

## 4.1 Character & Genetics

**Purpose:** Comprehensive editing of individual character properties.

**Menu hierarchy**

- Identity & Personal Details
- Attributes
- Traits & Genetics
- Health & Longevity
- Lifestyle & Education
- Character Modifiers
- Resource Editor
- Character Presets

### Identity & Personal Details

| Action                    | Functional requirement                                 | Engine support |
| ------------------------- | ------------------------------------------------------ | -------------- |
| Change age                | Increase/decrease age or use age presets               | Baseline has it (`ucm_change_age_interaction.txt`) |
| Change sexuality          | Heterosexual, homosexual, bisexual, asexual            | `set_sexuality` |
| Change weight             | Adjustable weight modification                         | `change_current_weight` |
| Change nickname           | Choose from predefined nicknames                       | `give_nickname` / nickname effects |
| Switch playable character | Transfer player control to an eligible selected character | Verify |
| Change culture            | Open culture picker                                    | Baseline has it |
| Change faith              | Open faith picker                                      | Baseline has it |
| Change house/dynasty      | Assign valid house or dynasty membership               | Verify |

### Attributes

Individually edit:

- Diplomacy
- Martial
- Stewardship
- Intrigue
- Learning
- Prowess

Required functions:

- Increase or decrease by the selected increment.
- Apply one increment to all six attributes.
- Apply predefined skill presets.
- Reset attributes to an explicitly defined baseline, where technically supported.
- Preserve Skonester's powerful attribute-enhancement options.

The editor shows current values and expected results before significant changes.

### Traits & Genetics

Organize traits into:

- Personality
- Congenital / Genetic
- Education
- Commander
- Lifestyle
- Fame and Status
- Health
- Special / DLC
- Custom Cheat Traits

Required functions:

- Add/remove individual traits.
- Filter traits by category. The list is built at game start with `every_trait` (Section 7.3), so traits added by other mods appear automatically.
- Modify congenital trait tiers.
- Remove negative congenital traits.
- Grant all selected positive congenital traits.
- Randomize personality.
- Remove negative personality traits.
- Modify trait experience when applicable.
- Increase/decrease commander trait experience when supported.
- Manage custom cheat traits separately from standard game traits.

Flag unsupported combinations before applying them.

### Health & Longevity

Provide:

- Heal injuries.
- Remove illnesses.
- Remove negative health modifiers.
- Adjust fertility.
- Enable/disable fertility.
- Grant/remove immortality. `set_immortal_age` only changes the age of a character who is already immortal (check with `is_immortal`), so granting immortality needs a separate effect.
- Toggle age-related protection.
- Lock/unlock stress.
- Lock/unlock dread.
- Lock/unlock tyranny.
- Apply persistent health regeneration.
- Apply health penalties and physical conditions.

**Important distinction:** Immortality, agelessness, and permanent health protection are separate effects. Don't present them as interchangeable.

### Lifestyle & Education

Provide:

- Add/remove lifestyle experience.
- Add/remove lifestyle perk points.
- Add/remove individual perks.
- Complete individual lifestyle trees.
- Reset individual lifestyle trees.
- Complete/reset all supported lifestyle trees.
- Change education traits.
- Improve education level.
- Support DLC lifestyles when present.

### Character Modifiers

Provide a categorized modifier editor covering:

- Health and longevity
- Resources and income
- Opinion and diplomacy
- Military strength
- Domain and administration
- Scheme performance
- Fertility and inheritance
- Lifestyle advancement
- Travel and activity bonuses

Each modifier offers Add, Remove, and, where appropriate, Adjust Magnitude or Duration.

### Resources

Support applicable character currencies, including:

Gold, prestige, piety, dynasty renown, influence, legitimacy, provisions, treasury, herd resources, merit, and other DLC-specific resources.

Only show resources that apply to the current character and game configuration.

---

## 4.2 Relationships & Family

**Purpose:** Edit personal, family, romantic, political, and secret relationships between characters.

**Menu hierarchy**

- Personal Relationships
- Marriage & Betrothal
- Family & Parentage
- Pregnancy & Fertility
- Hooks & Secrets
- Character Opinions
- Advanced Relationship Editor

### Personal Relationships

Supported relationship states include:

- Friend / Best Friend
- Rival / Nemesis
- Lover / Soulmate
- Potential Friend / Rival / Lover
- Crush
- Bully / Victim

Required functions:

- Create relationship.
- Remove relationship.
- Replace conflicting relationship.
- Establish relationship between the clicked character and the second character.
- Apply eligible relationships between the clicked character and a built-in group (for example, make every courtier a friend).

Directional relationships must keep the correct actor/recipient orientation.

### Marriage & Betrothal

Provide:

- Force marriage.
- Force matrilineal marriage.
- Arrange betrothal.
- Arrange matrilineal betrothal.
- Break betrothal.
- Force divorce.
- Remove marriage restrictions when explicitly selected.
- Add/remove concubines where supported.
- Marry the clicked character to the second character, so two NPCs can be married, not only the player and the clicked character.

Warn about incompatible characters, existing marriages, invalid succession states, and restrictions that can't safely be bypassed.

### Family & Parentage

Provide:

- Adopt character.
- Disown character.
- Assign or remove parent relationships (`set_father`, `set_mother`).
- Set or reset biological father (`set_real_father`).
- Make characters siblings.
- Change dynasty membership.
- Change house membership.
- Create cadet branch.
- Designate primary heir.
- Restore inheritance.
- Exterminate selected dynasty, preserving Skonester's existing functionality.

Validate parentage changes to prevent ancestry cycles, contradictory parent assignments, and invalid family structures.

### Pregnancy & Fertility

Provide:

- Start pregnancy (`make_pregnant`, baseline: `ucm_cheat_menu_force_pregnancy_effects.txt`).
- End pregnancy.
- Select father (`make_pregnant = { father = … }`).
- Request single-child, twin, or triplet outcomes (`number_of_children`).
- Enable/disable fertility.
- Remove pregnancy-related modifiers.

**Baby's sex:** set on an existing pregnancy with `set_pregnancy_gender` (engine docs; earlier versions of this spec wrongly said it couldn't be done).

Enable pregnancy options only when they apply, and distinguish guaranteed actions from outcomes the game engine decides.

### Hooks & Secrets

Provide:

- Add weak hook.
- Add strong hook.
- Remove hook.
- Reveal secrets.
- Remove secrets.
- Create selected secrets where supported.
- Preserve Skonester's fabricated-secret functionality.
- View the intended holder and target of each hook.

### Advanced Relationship Editor

Uses the clicked character and the second character as the pair.

The editor shows relationship status, marriage status, family relationships, opinions, hooks, alliances, and existing changes.

Group relationship actions always pair one character with each group member. They never create all-to-all relationships within a group.

---

## 4.3 Titles, Government & Diplomacy

**Purpose:** Manage political structures, titles, vassalage, succession, treaties, and wars.

**Menu hierarchy**

- Titles & Claims
- De Jure Structure
- Vassals & Contracts
- Government & Succession
- Authority & Stability
- Alliances & Treaties
- Wars & Peace
- Advanced Title Manager

### Titles & Claims

Provide:

- Claim selected title.
- Remove claims.
- Take selected title.
- Take all eligible titles.
- Transfer title to the second character.
- Create title (baseline: `ucm_create_titular_interactions.txt`).
- Rename title (`set_title_name` with the text-entry widget; see Section 7.3).
- Destroy title.
- Revoke title.
- Grant title.
- Merge titles using Skonester's existing behavior (`ucm_merge_titles.txt`).
- Select titles by rank.
- Select all titles held by a specified character.
- Select realm and sub-realm titles.

Before transferring a title, check holder eligibility, landholding requirements, title rank, and government restrictions.

### De Jure Structure

Provide:

- Change de jure liege.
- Reassign de jure vassals.
- Create missing superior titles.
- Create eligible subordinate titles.
- Construct an eligible de jure hierarchy.
- Reorganize selected de jure structures.
- Apply to multiple titles.

Large de jure changes must show how many titles are affected and flag invalid changes.

### Vassals & Contracts

Provide:

- Force vassalization.
- Make independent.
- Transfer vassal.
- Modify vassal contract.
- Remove applicable contract restrictions.
- Create/remove tributary relationships.
- Modify loyalty.
- Deter rebellions.
- Dissolve selected factions.

### Government & Succession

Provide government conversion for every applicable vanilla and installed-DLC government type.

Provide succession controls for:

- Primogeniture
- Ultimogeniture
- Confederate Partition
- Partition
- High Partition
- House Seniority
- Applicable elective systems (baseline overrides `common/succession_election/_succession_election.info`)

Preserve Skonester's existing succession controls and government-specific choices.

### Authority & Stability

Provide:

- Set realm authority level.
- Lock/unlock absolute authority.
- Increase vassal loyalty.
- Modify tyranny/dread.
- Suppress or dissolve factions.
- Stabilize selected realms.

### Alliances & Treaties

Provide:

- Form alliance.
- Break alliance.
- Establish treaty.
- End treaty.
- Create permanent treaty where supported.
- Assign alliances/treaties between selected NPCs.
- Apply treaties to selected groups.

### Wars & Peace

Provide:

- Declare war using a selected valid casus belli.
- Select war target.
- Force realm conquest where supported.
- Create tributary wars.
- Force victory.
- Force defeat.
- Force white peace.
- End one war.
- End all wars involving a selected character.
- Start eligible wars between the clicked character and the second character.

War operations must check existing wars, war objectives, character status, and participating sides.

---

## 4.4 Faith & Culture

**Purpose:** Comprehensive editing and conversion of culture and religion.

**Menu hierarchy**

- Culture Editor
- Cultural Traditions
- Cultural Pillars
- Innovations
- Culture Conversion
- Faith & Rite Editor
- Tenets & Doctrines
- Sins & Virtues
- Faith Conversion
- Mass Conversion Tools

### Culture Editor

Required controls:

- Select culture.
- Rename culture (`set_culture_name`).
- Change ethos.
- Change heritage.
- Change language.
- Change martial customs.
- Add/remove traditions. Baseline uses generated lists (`ucm_cw_tradition_picker_lists_generated.txt`); `every_culture_tradition` can replace them.
- Replace traditions.
- Change cultural acceptance.
- Trigger supported hybridization/divergence workflows.
- Learn selected languages.

Editing a culture changes the shared culture definition, not just the character who opened the editor. The interface must say so clearly.

### Innovations

Provide:

- Add individual innovation. Baseline uses one generated scripted GUI per innovation (`ucm_cw_innovation_unlock_generated.txt`). `add_innovation` accepts a `culture_innovation` target, so one scripted GUI taking the innovation as a scope could replace all of them, if the GUI can pass the innovation as a scope the way the tradition picker does (verify).
- Remove individual innovation (same; `ucm_cw_innovation_remove_generated.txt`).
- Add all eligible innovations.
- Complete innovations by era.
- Change cultural fascination/head where supported.

Support applicable DLC-era innovations.

### Culture Conversion

Available scopes:

- Clicked character.
- Clicked character's county.
- Clicked character's court.
- Clicked character's vassals.
- Clicked character's sub-realm.
- Clicked character's entire realm.

### Faith & Rite Editor

CK3 1.20 restructured religion. Faiths now work through **Rites**, tenets moved to their own database, and doctrines are organized in doctrine groups. The baseline is already ported (`agent.md`, "Status"). The editor targets this 1.20 model, not the pre-1.20 faith layout.

Provide:

- View the existing faith and rite definition.
- Rename faith or rite (`set_faith_name`, `set_rite_name`).
- Edit core tenets (`add_rite_tenet`, `remove_rite_tenet`).
- Replace/remove tenets.
- Add **personal** tenet slots (the `personal_tenet_slot_add` modifier; `free_personal_tenet_slots`).
- Edit doctrines by doctrine group.
- Edit marriage/family doctrines.
- Edit crime doctrines.
- Edit clergy doctrines.
- Edit religious-head settings.
- Select sins and virtues (the game keeps at most `MAX_VIRTUES_SINS = 7`, chosen from core and approved tenets).
- ~~Preserve Skonester's empty-tenet-slot fill and cleanup tools~~ Dropped in Phase 11: nothing in Skonester or this mod ever called them.

**Unverified: extra core tenets.** There's no slot-adding effect or define, but `add_rite_tenet` documents no limit. Whether a rite can hold more core tenets than usual has to be tested in game. Treat it as experimental until then.

### Faith Conversion

Apply conversion to characters, counties, courts, vassals, sub-realms, or entire realms.

**Validation:** Faith and culture changes must check the target scope and game-version compatibility. Expanded tenet tools must not assume other mods use vanilla slot limits.

---

## 4.5 Realm, Holdings & Construction

**Purpose:** Manage economic development, buildings, holding structures, and estates.

**Menu hierarchy**

- County Editor
- Development & Control
- Holding Manager
- Building Manager
- Construction Automation
- County Modifiers
- Estates & Domicile Buildings

### County Editor

Provide:

- Maximize development.
- Increase/decrease development.
- Maximize control.
- Adjust control.
- Maximize popular opinion.
- Change county culture.
- Change county faith.
- Add/remove county modifiers.

### Holding Manager

Provide:

- Change valid holding type.
- Select county capital.
- Add building slots.
- Remove buildings.
- Remove holding where valid.
- Create eligible new holdings where the engine supports it.

### Building Manager

Provide:

- Construct selected building.
- Upgrade selected building.
- Maximize building chain.
- Remove selected building.
- Upgrade every eligible building.
- Upgrade selected counties.
- Upgrade entire realm or sub-realm.
- Add building slots to selected holdings.
- Automate eligible AI building choices.

Building pickers use a **generated building catalog** built from the game's `common/buildings` files (Section 7.3). Script can't loop over all building types at runtime. Buildings added by other mods appear only after the catalog is regenerated against that mod.

### Estates & Domicile Buildings

Preserve Skonester's:

- Family estate upgrades.
- Worldwide estate upgrades.
- Economic estate preset.
- Military estate preset.
- Balanced estate preset.
- Exterior building removal.
- 1.20 domicile cheat (rewritten on 1.20 effects, `agent.md` milestone M2).

Add more granular building selection where possible.

**High-risk controls:** Removing holdings, changing county capitals, and adding potentially irreversible building slots require confirmation.

> **Baseline note:** Skonester overrides `NProvince.MAX_BUILDINGS = 1453` in `common/defines`. That changes the building limit for every province in the game, not just for cheat users. Review it in Phase 0 (Section 7.4).

---

## 4.6 Military & Warfare

**Purpose:** Create and modify armies, units, combat capabilities, and wars.

**Menu hierarchy**

- Army Spawner
- Men-at-Arms Editor
- Levies & Reinforcement
- Military Bonuses
- Knights & Accolades
- Special Units
- Wars & Military Operations

### Army Spawner

Provide:

- Select unit type.
- Select quantity.
- Generate men-at-arms.
- Generate eligible special units.
- Spawn armies for selected characters when supported.
- Spawn predefined military presets.
- Reinforce generated units.

Unit pickers use a generated men-at-arms catalog (baseline: `ucm_sand_maa_catalog_effects.txt`). Units added by other mods need a regenerated catalog or a compatibility patch.

### Men-at-Arms Editor

Provide:

- Add regiment.
- Expand regiment.
- Reinforce regiment.
- Maximize regiment strength.
- Apply available regimental bonuses.
- Adjust stack size within engine limits.

### Levies & Reinforcement

Preserve:

- Unlimited levies.
- Infinite supplies.
- Effectively zero upkeep.
- Reduced attrition.
- Instant or accelerated reinforcement.

Provide individual toggles and a way to restore normal behavior.

### Military Bonuses

Provide:

- Army god mode.
- Increased movement speed.
- Increased combat strength.
- Siege effectiveness bonuses.
- Reinforcement bonuses.
- Military maintenance modifiers.

### Knights & Accolades

Provide:

- Increase knight capacity.
- Increase knight effectiveness.
- Create/manage eligible accolades.
- Name accolades with the text-entry widget (vanilla does this in `accolade_events.txt`).
- Preserve Skonester's virtual accolade functionality.
- Boost accolade glory.

### Wars & Military Operations

Connect to the diplomacy/war system without duplicating it.

All war-changing actions call shared war operations, so targeting and validation stay consistent.

---

## 4.7 Artifacts & Equipment

**Purpose:** Full creation, customization, repair, transfer, and management of artifacts.

**Menu hierarchy**

- Create Artifact
- Edit Existing Artifact
- Artifact Modifiers
- Artifact Quality & Durability
- Transfer / Steal Artifacts
- Destroy Artifacts
- Saved Artifact Presets

### Artifact Creator

Support applicable artifact types, including:

- Weapons
- Armor
- Crowns
- Regalia
- Books
- Trinkets
- Court furnishings
- Thrones
- Tapestries
- Other eligible artifact categories

Creation workflow:

1. Select recipient.
2. Select category.
3. Select subtype.
4. Select rarity/quality.
5. Enter a name (text-entry widget, applied with `set_artifact_name`). Descriptions use predefined options.
6. Select modifiers.
7. Configure modifier values/stacks.
8. Preview.
9. Create and grant the artifact.

### Artifact Modifiers

Preserve Skonester's five-slot artifact modifier system, including custom modifier amounts.

Modifier categories include:

- Character attributes
- Health and lifespan
- Fertility
- Income and tax
- Vassal opinion
- Military strength
- Knight strength
- Schemes
- Prestige and piety
- Other game-supported artifact modifiers

### Existing Artifact Editor

Provide:

- Select owned artifact.
- Rename artifact (`set_artifact_name`).
- Change rarity/quality.
- Change compatible modifiers.
- Adjust modifier magnitude/stack.
- Repair durability.
- Change decay settings where supported.
- Transfer ownership.
- Steal artifact.
- Destroy artifact.

### Artifact Presets

Let players pick predefined configurations instead of setting everything up by hand.

Examples:

- Legendary Warrior
- Master Administrator
- Immortal Scholar
- Dynasty Founder
- Supreme Intriguer

Presets must produce their listed effects consistently. Modifier compatibility still depends on the artifact type and the available game definitions.

---

## 4.8 Court & Character Generation

**Purpose:** Generate customized characters and manage courts, councils, and court appointments.

**Menu hierarchy**

- Character Generator
- Family Generator
- Courtier Generator
- Council Generator
- Knight & Commander Generator
- Court Positions
- Court Automation
- Court Cleanup

### Character Generator

Configurable fields:

- Sex
- Age
- Culture
- Faith
- House/dynasty
- Attribute preset
- Congenital trait preset
- Personality preset
- Education
- Character count
- Destination court/camp

Generated characters get their names from the game's culture name lists.

### Family Generator

Provide:

- Create child.
- Create sibling.
- Create parent.
- Create spouse.
- Generate twins/multiple siblings where supported.
- Create members of the selected character's dynasty.

Generating parents or changing existing family structures requires explicit confirmation.

### Courtier & Council Generator

Generate suitable candidates for:

- Chancellor
- Steward
- Marshal
- Spymaster
- Chaplain
- Commander
- Knight
- Generic courtier
- Specialized court official

### Court Positions

Support every court position available under the current game's DLC and government.

Provide:

- Generate a qualified character.
- Assign office.
- Replace officeholder.
- Remove officeholder.
- Fill eligible empty positions.
- Reassign all selected positions.

### Automated Court Management

Preserve Skonester's automatic appointment system.

Provide:

- Enable/disable automatic appointments.
- Configure appointment frequency.
- Select role groups to manage.
- Prefer existing courtiers or allow generated replacements.
- Remove unneeded courtiers with confirmation.

Automated character generation needs limits so court population can't grow without bound.

---

## 4.9 DLC & Advanced Systems

**Purpose:** Provide specialized cheat functionality without cluttering the main menus.

**Menu hierarchy**

- Legends
- Activities
- Regencies & Diarchies
- Domiciles & Adventurers
- Inspirations
- Schemes & Intrigue
- Special Government Systems
- Events & Debugging

### Legends

Provide:

- Spawn eligible legends.
- Select legend category.
- Accelerate spread.
- Set spread-speed presets.
- Remove selected legends where supported.
- Remove legend-spread modifiers.
- Restore normal spread.

Preserve Skonester's specialized legend controls.

### Activities

Provide:

- Reduce/remove activity cost.
- Start eligible activities.
- Advance activity phases.
- Finish eligible activities.
- Cancel an activity where supported.

These controls must not leave activities half-finished.

### Regencies & Diarchies

Provide:

- Start regency.
- End regency.
- Assign regent.
- Replace regent.
- Adjust power-sharing scale.
- Select applicable government-specific power arrangements.

### Domiciles & Adventurers

Provide:

- Move domicile.
- Change eligible domicile properties.
- Upgrade domicile buildings.
- Convert to landless adventurer where supported.
- Rename adventurer company (text-entry widget plus `create_adventurer_title`, as vanilla does in `07_dlc_ep3_scripted_effects.txt`).
- Generate local contracts.
- Apply adventurer resource presets.

### Inspirations

Provide:

- Grant eligible inspiration.
- Select inspiration category.
- Sponsor inspiration.
- Complete or accelerate inspiration when supported.
- Remove invalid inspiration state.

### Schemes & Intrigue

Provide:

- Increase scheme success chance.
- Increase scheme growth.
- Increase secrecy.
- Add opportunities.
- Add eligible agent slots.
- Set progress presets.
- Complete eligible schemes.
- Reset scheme progress.
- Enable/disable increased active scheme limits.

Don't assume every scheme type supports every change.

### Special Government Systems

Provide government tools for systems introduced by supported DLC.

Keep these grouped under their government rather than in one long, unfiltered list.

### Events & Debugging

Provide:

- Toggle debug tools (the baseline's debug action group already requires CK3 debug mode).
- Open experimental event catalog.
- Trigger supported events on valid targets.
- Restore temporary cheat state where possible.
- Reset stuck menu selections.

Label experimental actions clearly.

**Achievements:** Enabling the mod doesn't block achievements. CK3 1.20 only blocks them for multiplayer, observer mode, switching character, debug mode or console commands, game rules flagged `blocks_achievements`, and over-budget Ruler Designer characters (vanilla `ACHIEVEMENTS_EXPLANATION`). The mod's game rules carry no such flag. Buttons that run console commands other than `debug_mode` (fog of war, quicksave/quickload hotkeys) only appear in debug mode, and the debug and character-switch buttons warn that they disable achievements.

---

# 5. Group Actions

There's no manual selection system: no pins and no saved selection lists. Instead, an action can apply to a **built-in group** taken from the thing you right-clicked. The group is worked out when the action runs, so there's nothing to set up beforehand or to clear afterwards.

## 5.1 Built-in groups

| Clicked target | Groups offered                                                               | Iterator used |
| -------------- | ---------------------------------------------------------------------------- | ------------- |
| Character      | Children, close family, extended family                                      | `every_child`, `every_close_family_member`, `every_extended_family_member` |
| Character      | House members, dynasty members                                               | `every_house_member`, `every_dynasty_member` |
| Ruler          | Direct vassals, all vassals and tributaries, courtiers, councillors, knights | `every_vassal`, `every_subject`, `every_courtier`, `every_councillor`, `every_knight` |
| Ruler          | Every county in the realm, every county in the sub-realm, held titles        | `every_realm_county`, `every_sub_realm_county`, `every_held_title` |
| Character      | Spouses, lovers, friends                                                     | `every_spouse`, relationship iterators |
| Title          | De jure counties, de jure vassal titles                                      | `every_de_jure_county`, `every_direct_de_jure_vassal_title` |
| Culture        | Counties of the culture                                                      | `every_culture_county` |
| Faith          | Counties of the faith                                                        | `every_faith_county` |

Each group action may add fixed filters where they matter, such as adults only, landed only, AI only, or "exclude myself". These are part of the action's definition, not something the player sets up.

World-wide groups (every living character, every county in the world) aren't offered by default. They're only available in Advanced/Experimental mode and always need confirmation.

## 5.2 Group-compatible operations

Group actions cover appropriate operations across:

- Skills
- Traits
- Trait experience
- Lifestyle experience
- Resources
- Modifiers
- Culture
- Faith
- Health
- Eligible title operations
- County development/control
- Building upgrades
- Eligible character relationships
- Court and military management

Not every single-target action has a group version.

For example, giving a trait to all your courtiers is simple. Making every vassal the same person's spouse or heir makes no sense and isn't offered.

## 5.3 Group execution workflow

**Right-click → Choose group action → Configure → Preview → Confirm → Execute → Review results**

Before execution, show:

- The group and how many members it has.
- Eligible targets.
- Ineligible targets.
- Changes to be applied.
- Whether the action may be irreversible.
- Roughly how many game entities will be affected.

After execution, show:

- Successfully changed.
- Skipped.
- Failed.
- Why each skipped or failed target was skipped, when that can be detected.

A group action must not stop at the first invalid target.

---

# 6. Functional UI requirements

## 6.1 Consistent visual conventions

Use CK3's existing visual language:

- Existing icons and panel styles where appropriate.
- Standard game tooltips.
- Consistent spacing and navigation.
- Clear grouping of actions.
- Existing Skonester terminology where it's familiar and accurate.

Avoid an elaborate standalone HUD.

## 6.2 Quick Actions

Quick Actions gives fast access to frequent operations.

Recommended defaults:

- Add Gold
- Add Prestige
- Add Piety
- Add Renown
- Heal Character
- Clear Stress
- Edit Skills
- Edit Traits
- Change Age
- Change Culture
- Change Faith
- Force Marriage
- Max Development
- Max Control
- Spawn Men-at-Arms
- Army God Mode
- Open Artifact Workshop

Add favorite and recent actions if the interface can support them reliably.

## 6.3 Visibility and filtering

Actions are:

- **Visible and enabled:** supported and valid.
- **Visible and disabled:** supported but currently invalid, with an explanation.
- **Hidden:** irrelevant to the game configuration, such as mechanics from DLC that isn't installed.

An Advanced/Experimental mode shows additional options.

## 6.4 Target context display

Every editor shows its target prominently.

For example:

**Character Editor — Duke Robert**\
Target: Duke Robert | Second character: Lady Matilda

**Culture Editor — Anglo-Saxon**\
Editing: Anglo-Saxon Culture | Scope: Global Culture Definition

**Max Development — Realm Counties**\
Group: Every county in Duke Robert's realm | Valid: 34 | Skipped: 2

These labels are illustrations, not interface requirements.

## 6.5 Interaction workflow examples

**Editing an NPC**

Right-click Character → Open Cheat Menu → Character & Genetics → Attributes → Increase Stewardship.

**Changing an NPC relationship**

Right-click Character B → Set as Second Character → Right-click Character A → Open Cheat Menu → Relationships & Family → Relationship Editor → Choose Relationship → Confirm.

**Changing every county in a realm**

Right-click Ruler → Open Cheat Menu → Realm, Holdings & Construction → Max Development in Every Realm County → Preview → Apply.

**Creating an artifact**

Right-click Recipient → Open Cheat Menu → Artifacts → Artifact Workshop → Configure Type, Quality, Modifiers → Create.

Every flow returns to the original target or parent menu without clearing the second character unnecessarily.

---

# 7. Technical architecture

## 7.1 Architectural principles

Build around shared operations rather than duplicating game effects across separate menus.

Recommended responsibilities:

| Component           | Responsibility                                                                  |
| ------------------- | ------------------------------------------------------------------------------- |
| Interaction Layer   | Right-click entries, context-sensitive access, target assignment                |
| Navigation Layer    | Category menus, back/close behavior, opening editors                            |
| Target Resolver     | Clicked target, second character, built-in groups, single-player check          |
| Action Registry     | Stable IDs, required targets, supported values, guards                          |
| Gameplay Modules    | Character, relationship, realm, military, artifact, culture, faith, DLC effects |
| Validation Layer    | Target eligibility, game/DLC conditions, legal scope checks                     |
| Execution Layer     | Apply validated effects once, consistently                                      |
| Confirmation Layer  | Preview and confirmation for significant changes                                |
| Feedback Layer      | Success, failure, and skip reporting                                            |
| Compatibility Layer | Version-specific and mod-dependent definitions                                  |

## 7.2 Action definition contract

Every action has a documented specification with:

- Stable internal action ID.
- Display name and description.
- Category and parent menu.
- Required target type.
- Supported target modes.
- Input parameters.
- Gameplay effect.
- Eligibility conditions.
- DLC/version dependency.
- Which built-in groups it supports, if any.
- Confirmation level.
- Reversal or cleanup capability.
- Test cases.

Example:

**Action ID:** `character.attribute.adjust`

- Context: Character
- Target: The clicked character, or a built-in group such as courtiers or vassals
- Parameters: Attribute, signed increment
- Behavior: Change the chosen attribute
- Validation: Character exists and the selected value is valid
- Feedback: Report the actual change
- Reversal: Opposite signed increment, subject to any changes made in between

Example:

**Action ID:** `realm.title.transfer`

- Context: Title and receiving character
- Parameters: Title, recipient, eligible transfer mode
- Validation: Title exists, recipient can hold the title, no invalid hierarchy
- Confirmation: Required
- Reversal: Not guaranteed; the affected game state may have changed
- Feedback: Show the transferred title and new holder

## 7.3 CK3-specific implementation strategy

Use CK3's existing modding mechanisms:

- Character interactions for access and target capture.
- Events/decision-based menus where appropriate.
- Custom GUI windows for complex editors.
- Scripted GUI and effects for UI-triggered operations.
- A global variable for the second character (Section 3.1).
- Localization for all visible text.
- Scripted triggers for eligibility and DLC checks.
- One shared single-player trigger (`has_multiple_players = no`) used by every interaction's `is_shown`, every decision's `is_shown`, every scripted GUI's `is_shown`, and every persistent-cheat tick.

**Runtime lists.** Script can loop over many database types: `every_trait`, `every_culture_innovation`, `every_culture_tradition`, `every_culture_pillar`, `every_tenet`, `every_doctrine`, `every_government_type`, `every_holding_type`, `every_court_position_type`, `every_casus_belli_type`, `every_accolade_type`, `every_legend_type`, `every_activity_type`, and others (see `logs/effects.log` from `script_docs`). Pickers for these types build their lists at game start (and on reload) into read-only global variable lists, so content from other mods appears automatically.

**Generated catalogs.** There's no loop over building types, men-at-arms types, or artifact templates (`every_maa_regiment` and `every_artifact` cover existing regiments and artifacts, not the definitions). Pickers for those are **generated offline** from the game files by scripts in `tools/`, as the baseline already does:

- `tools/gen_cw_tradition_picker_lists.py` produces `ucm_cw_tradition_picker_lists_generated.txt` (and, with `--agot-dir`, the AGOT variant in `tools/out/agot/`).
- `tools/gen_ek2_compatch.py` produces the religion virtue/sin data and the merged/derived files under `compat/ek2/`.
- `tools/gen_ucm_main_menu.py` produces `gui/ucm_main_menu.gui`; `tools/gen_ucm_translations.py` produces the German, Russian, Chinese and Turkish `ucm_l_*.yml`. `tools/ck3parse.py` is their shared parser.
- ~~`tools/gen_ucm_cw_innovation_sguis.py`~~ removed in Phase 10: no GUI ever called the innovation scripted GUIs it generated.

Generated files say "do not edit by hand" and are rebuilt whenever the target game version or a supported mod changes. Catalogs live in global variable lists.

The baseline's tradition and innovation generators can be retired once those pickers move to runtime lists.

**Text entry.** CK3's event text-entry widget (`event_window_widget_enter_text`) stores typed text, which localization can then display. Effects that take a localization key or dynamic description may be able to use it: `set_title_name_dynamic`, `set_artifact_name`, `set_house_name`, `set_dynasty_name`, `set_culture_name`, `set_faith_name`, `set_rite_name`, and `create_adventurer_title`. Typed text can't be read as a number. Only vanilla's own uses (artifacts, adventurer titles, houses) are proven. Feeding typed text to `change_first_name` failed in Phase 2 testing, so character renaming was dropped.

Ordinary menu use must not require debug mode.

Don't promise generic console-command execution, typed numeric input, or universal rollback.

## 7.4 Compatibility and module isolation

Isolate feature modules so that an error in one doesn't require restructuring the whole menu.

Avoid:

- Unnecessary vanilla GUI overrides.
- Duplicate implementations of the same gameplay effect.
- Hard-coded assumptions about modded traits, faiths, cultures, units, and buildings, beyond the regenerable catalogs above.
- Unbounded recurring character scans.
- Persistent global modifiers where a one-time change is enough.
- Global defines changes that affect players who aren't using cheats.
- Overwriting existing Skonester identifiers without a migration plan.

Where baseline components are kept, reuse them carefully, and use a new project-specific namespace for additions.

### 7.4.1 Vanilla override inventory

This is the Phase 0 inventory of the baseline. Since then: `gui/interaction_confirmation.gui` and the debug localization overrides were removed in Phase 7 (replaced by `localization/replace/`), `09_mpo_values.txt` in Phase 9; the two `.info` files are no longer in the repo. Still overridden: `gui/window_character.gui`, `gui/interaction_menu_window.gui`, `gui/frontend_ingame_menu.gui` and `tgp_china_minister_on_action.txt`.

The baseline replaced these vanilla files outright. Any other mod that changes the same file conflicts, and the last one in load order wins.

| File | Risk |
| --- | --- |
| `gui/window_character.gui` | High: the character window, shared by many UI mods |
| `gui/interaction_menu_window.gui` | High: the right-click menu |
| `gui/interaction_confirmation.gui` | High: every interaction confirmation |
| `gui/frontend_ingame_menu.gui` | Medium |
| `common/on_action/dlc/tgp/tgp_china_minister_on_action.txt` | Medium: DLC game logic |
| `common/script_values/09_mpo_values.txt` | Medium |
| `common/culture/traditions/_traditions.info` | Low: documentation file |
| `common/succession_election/_succession_election.info` | Low: documentation file |
| `localization/english/debug_l_english.yml` | Low |
| `localization/german/debug_l_german.yml` | Low |

Goal: replace the high-risk GUI overrides with additions such as scripted widgets, or with minimal targeted overrides. Each remaining override must be listed in the mod description.

### 7.4.2 Global defines

The baseline's `common/defines` overrides include at least `NProvince.MAX_BUILDINGS = 1453`, `NModifier.STANDARD_MINIMUM_VALUE = 0.0`, and `NCharacterOpinion.MAX_DUCHIES_BEFORE_PENALTY = 4`. These change rules for the whole game. In Phase 0, keep each one only if a cheat actually needs it, and document it. (Outcome: `MAX_DUCHIES_BEFORE_PENALTY` was removed in Phase 7; the other two remain in `common/defines/`.)

---

# 8. Save Safety and State Management

## 8.1 Destructive operations

These require explicit warnings:

- Destroying titles.
- Removing holdings.
- Rewriting de jure structures.
- Changing parentage or house membership.
- Exterminating dynasties.
- Mass religious/cultural conversion.
- Switching governments.
- Major succession changes.
- World-scale construction or population edits.

## 8.2 Undo policy

Distinguish three categories:

**Directly reversible:** A discrete change with a reliable inverse, such as a controlled attribute increment or adding/removing a dedicated modifier.

**Conditionally reversible:** A change that can be roughly restored if the previous state was saved and the game allows restoring it.

**Not reliably reversible:** Structural or simulated changes, including some title changes, family changes, wars, events, pregnancies, and government conversions.

Don't advertise a universal undo without proving it works.

Recommend saving the game before high-risk actions.

## 8.3 Temporary effects

Persistent cheats need clear toggle or removal controls.

These include:

- Immortality and longevity effects.
- Permanent health regeneration.
- Infinite supplies.
- Unlimited levies.
- Army god mode.
- Automatic court appointments.
- Scheme modifiers.
- Legend spread modifiers.
- Attribute and other cheat presets.

Removing a persistent cheat removes only the state the mod manages, not unrelated game modifiers.

---

# 9. Game and Mod Compatibility

## 9.1 Primary target

Target CK3 1.20.x "Crozier" and validate with the installed DLC. Engine facts in this spec were checked against 1.20.1.2 game files. The baseline README says it was tested in game on 1.20.1.1.

Don't assume a mod built for 1.19 works on 1.20. The baseline says 1.19 builds don't.

## 9.2 DLC support

Detect and gate DLC-specific features.

Relevant groups include:

- Royal Court and artifacts.
- Tours and Tournaments activities.
- Legends of the Dead.
- Roads to Power administration/estates.
- Landless adventurers.
- By God Alone (1.20 religion changes).
- Government-specific and regional systems from later DLC.

Decide feature availability from the installed game content and DLC requirements.

## 9.3 Total conversion mods

The architecture accommodates modded content, particularly:

- Custom traits.
- Custom cultures/faiths.
- Custom government types.
- Custom buildings.
- Custom men-at-arms.
- Custom title structures.

Traits, cultures, faiths, innovations, traditions, tenets, doctrines, and government types added by other mods appear automatically, because those pickers use runtime lists (Section 7.3). **Buildings, men-at-arms types, and artifact templates don't.** Supporting those from a content mod means running the generators against it and shipping the output as a compatibility patch.

Don't claim AGOT or other total-conversion compatibility without dedicated testing. As of the baseline, AGOT targets 1.19 and crashes 1.20 at startup even without this mod.

Compatibility patches may also be needed for replaced vanilla screens or gameplay systems (Section 7.4.1).

## 9.4 Standalone behavior and licensing

The finished menu must not depend on having either Skonester or Divine Intervention loaded. It started from Skonester's code but has been heavily rewritten, so it is better described as inspired by Skonester Cheat Menu Gold and Daddy Pika's Cheat Menu than as a patched copy.

The baseline is licensed under **Creative Commons Attribution 4.0 International**. Adapting and modifying it is permitted. Every release must credit Skonester, Daddy Pika (Daddy Pika's Cheat Menu), Zhuge, and the contributors named in the baseline README, link the license, and state that changes were made.

Divine Intervention's publicly documented behavior can serve as a feature reference. Don't copy its code or assets without permission.

---

# 10. Implementation Roadmap

All ten feature categories are in the final scope, but development proceeds in controlled phases.

| Phase                | Scope                                                                                | Exit requirement                              |
| -------------------- | ------------------------------------------------------------------------------------ | --------------------------------------------- |
| 0 — Baseline         | Audit Skonester, establish a clean test build, inventory working behavior, record the error.log baseline, review vanilla overrides and global defines | Existing-feature regression baseline and recorded error count |
| 1 — Foundation       | Navigation, clicked-target and second-character targeting, group-action framework, single-player gate, validation, execution, confirmations | Stable single-target and group workflows; menu hidden when a second player connects |
| 2 — Characters       | Attributes, traits, genetics, health, lifestyle, relationships, family               | Character and relationship tests pass         |
| 3 — Realm            | Titles, government, diplomacy, culture, faith/rite, construction                     | Realm-changing effects validated              |
| 4 — Military & Items | Armies, war operations, artifacts, modifiers                                         | Military and artifact tests pass              |
| 5 — Court & DLC      | Spawning, automated appointments, legends, activities, schemes, regencies, domiciles | DLC-dependent tests pass                      |
| 6 — Group Actions    | Group versions of actions across supported modules, large-group handling             | Group correctness and performance tests pass  |
| 7 — Hardening        | Localization, compatibility, accessibility, packaging, regressions, catalog regeneration | Release acceptance suite passes           |
| 8–11 (added)         | Whole-repo review fixes; upstream-code fixes ([upstream-review.md](upstream-review.md)); dead-code removal; simplification | Done, not yet load-tested; see below |
| EK2 compatch (added) | Detection, vanilla-data isolation, `compat/ek2/` mod | Done except the load test; see [ek2-compatch-plan.md](ek2-compatch-plan.md) |

### Phase 0 tasks

1. Load vanilla 1.20.1.2 plus the baseline only. Start a new game, reach the map, and record the number of `error.log` lines attributed to the mod's files. The baseline's own notes report about 11,600 errors after the 1.20 port (`agent.md`).
2. Run `script_docs` in the in-game console and keep the generated effect/trigger/data-type logs as the reference for verifying everything marked "verify" in this spec.
3. Review each vanilla override in Section 7.4.1 and each define in Section 7.4.2, and decide whether to keep, minimize, or remove it.
4. List every global variable that holds per-player state. (Done; migration no longer needed since v1.3 made the mod single-player only.)
5. Recover or rewrite the missing `gen_ucm_cw_innovation_sguis.py` generator. (Rewritten in Phase 0, then removed in Phase 10 as unused.)
6. Click through each existing feature and record whether it works, using the "Verify" notes in `agent.md`.

Phase 0 progress and findings are recorded in [phase0-baseline.md](phase0-baseline.md). Phase 1 is described in [phase1-foundation.md](phase1-foundation.md), Phase 2 in [phase2-characters.md](phase2-characters.md), Phase 3 in [phase3-realm.md](phase3-realm.md), Phase 4 in [phase4-military-artifacts.md](phase4-military-artifacts.md), Phase 5 in [phase5-court-dlc.md](phase5-court-dlc.md), Phase 6 in [phase6-group-actions.md](phase6-group-actions.md), Phase 7 in [phase7-hardening.md](phase7-hardening.md), Phase 8 in [phase8-review-fixes.md](phase8-review-fixes.md), Phase 9 in [phase9-upstream-fixes.md](phase9-upstream-fixes.md), Phase 10 in [phase10-dead-code.md](phase10-dead-code.md), Phase 11 in [phase11-simplification.md](phase11-simplification.md), Phase 12 (features recreated from the Skonester and Divine Intervention gap review) in [phase12-gap-features.md](phase12-gap-features.md).

Keep a usable build at the end of every phase.

Don't combine large structural changes with unrelated feature additions in the same validation cycle.

---

# 11. Validation and Acceptance Criteria

## 11.1 Preservation

- Existing Skonester interactions remain accessible.
- Existing behavior is unchanged unless deliberately replaced.
- Previously working military presets still work.
- Existing artifacts can still be created, edited, and repaired.
- Culture, faith, title, and succession editors still work.
- DLC-specific functionality remains gated.
- Menu state from one target doesn't leak into another.

## 11.2 Targeting

- A right-click action changes the clicked target, not the player, unless explicitly requested.
- The second character keeps the correct identity and is cleared when that character dies.
- Invalid, removed, or dead targets are handled gracefully.
- A group action affects exactly the group it names, worked out when it runs.
- No action runs on an unintended title or character.
- With a second player connected, no interaction, decision, or window from the mod is shown, and persistent cheats stop applying.

## 11.3 Game-state integrity

- No unintended titles or holdings are destroyed.
- Parentage edits can't create ancestry loops.
- Government changes handle invalid targets gracefully.
- Religion/culture edits apply at the specified level.
- Artifact edits don't silently delete unrelated modifiers.
- Turning off a cheat stops its persistent effects.
- Invalid war operations don't corrupt war state.

## 11.4 Performance and errors

- Opening menus doesn't cause lasting frame-rate drops.
- Large character or title lists aren't recalculated unnecessarily every game tick.
- Group actions produce deterministic counts and completed-action reports.
- Unrelated characters and realms stay unchanged.
- Automated features don't spawn unlimited courtiers or recurring event loops.
- No new `error.log` lines attributed to the mod's files compared to the Phase 0 baseline. Each phase should also reduce the baseline count.

## 11.5 Compatibility

Test at minimum:

- Current vanilla CK3 with no optional DLC enabled, where applicable.
- Vanilla CK3 with supported DLC enabled.
- A new save.
- An existing save made with the baseline mod.
- Alternate government and landless characters.
- A two-player multiplayer session, to confirm the mod is disabled.
- Representative modded traits, buildings, units, cultures, and faiths, using regenerated catalogs.
- Relevant total-conversion combinations, tested separately.
- At least one popular UI mod, to check conflicts with the overrides in Section 7.4.1.

## 11.6 Release completion

A feature is complete only when:

1. The action is reachable through its intended menu.
2. The correct target is identified.
3. Required inputs can be supplied.
4. Eligibility guards work correctly.
5. The gameplay effect happens as specified.
6. Feedback accurately reports the outcome.
7. Unrelated state is preserved.
8. The feature has passed both isolated and integrated tests.

A visible button or localization entry alone doesn't make a feature complete.

---

# 12. Final Product Definition

The finished Unified CK3 Cheat Menu offers the breadth of a full game editor while keeping the speed and convenience of Skonester's right-click interface.

Its defining characteristics:

**Accessible:** Most common cheats take only a right-click and a few selections.

**Comprehensive:** Character, family, realm, culture, faith, military, artifact, court, and DLC mechanics are covered in one consistent interface.

**Precise:** Complex operations let the player say exactly which characters, titles, counties, or other entities are affected.

**Flexible:** Simple single-target actions sit alongside advanced editors and batch operations.

**Maintainable:** Each feature has a stable internal definition, clear ownership, guarded effects, and tests.

**Reliable:** The menu flags unsupported operations rather than failing silently or acting on the wrong target.

The governing design principle:

**Skonester's presentation, expanded with Divine Intervention's depth, implemented as one coherent and maintainable mod.**

---

# Appendix A — Engine verification (CK3 1.20.1.2)

Checked against the game's own documentation (`script_docs` output: `logs/effects.log`, `triggers.log`, `modifiers.log`), plus the vanilla and baseline script that uses each effect. "Verified" means documented by the engine. It hasn't necessarily been tested in game.

| Claim | Result | Evidence |
| --- | --- | --- |
| Script can loop over traits, innovations, traditions, tenets, doctrines | ✅ Verified | `every_trait`, `every_culture_innovation`, `every_culture_tradition`, `every_tenet`, `every_doctrine` ("Iterate through every … in the database") |
| Script can loop over building types, MAA types, artifact templates | ❌ No | No database iterator for these; `every_maa_regiment` and `every_artifact` cover existing instances only |
| Typed text can rename titles, artifacts, houses, cultures, faiths, rites | ✅ Verified | `set_title_name_dynamic`, `set_artifact_name`, `set_house_name`, `set_culture_name`, `set_faith_name`, `set_rite_name`; text-entry pattern in `accolade_events.txt` and `07_dlc_ep3_scripted_effects.txt` |
| Typed text can rename characters | ❌ Failed in game | `change_first_name = <dynamic_description>` exists, but in Phase 2 testing it rejected typed text ("Name is too long", then "Couldn't find new first name"). Dropped at the user's request |
| Typed text can be read as a number | ❌ No | The text controller stores a string shown through localization |
| Pregnancy with chosen father and number of children | ✅ Verified | `make_pregnant` / `make_pregnant_no_checks`: `father`, `number_of_children`, `known_bastard` |
| Choosing the baby's sex | ✅ Verified | `set_pregnancy_gender = female/male/random` in `effects.log`. Not a `make_pregnant` parameter |
| Biological father | ✅ Verified | `set_real_father`, `set_father`, `set_mother` |
| Sexuality, weight | ✅ Verified | `set_sexuality`, `change_current_weight` |
| Immortality | ⚠️ Partial | `set_immortal_age` only works if already immortal; `is_immortal` trigger exists. Granting immortality needs another effect (verify) |
| Personal tenet slots | ✅ Verified | `personal_tenet_slot_add` is a modifier; `set_personal_tenet`, `force_set_personal_tenet` effects |
| Extra core tenets | ⚠️ Unverified | `add_rite_tenet` exists with no documented limit; test in game |
| Single scripted GUI for innovations | ⚠️ Likely (moot: the innovation scripted GUIs were removed in Phase 10) | `add_innovation` accepts a `culture_innovation` target; GUI scope passing needs verifying |
| Virtue/sin cap | ✅ Verified | `MAX_VIRTUES_SINS = 7` in `00_defines.txt` |
| Mod disables achievements | ❌ No | Vanilla `ACHIEVEMENTS_EXPLANATION` lists no mod or checksum condition; Divine Intervention (also changes `common/`) documents only debug mode as disabling them. Not yet confirmed in an Ironman game |

# Appendix B — Baseline audit summary

This records the original Skonester baseline at the start of the project, not the current repo.

- **Source:** `https://github.com/skonester/Skonester-Cheat-Menu`, commit `bfcb175` ("Portrait GUI Cheats"), cloned with full history. The local clone's remote is named `upstream`.
- **Version:** `descriptor.mod` version `10.22.26-BGA3`, `supported_version="1.20.*"`, tag "1.20 'Crozier'".
- **License:** CC BY 4.0.
- **Size:** about 159 scripted-effect files, 53 scripted-trigger files, 61 event files, 27 GUI files, 22 scripted-GUI files, 17 character-interaction files, and localization in five languages.
- **Entry points:** right-click → "Open Skonester Character Tools"; Decisions → Realm & Government Tools → Open Sub Menu Editor.
- **Known state:** ported to 1.20 and reaches the map with vanilla. Features still need clicking through (`agent.md`).
- **Risks:** 10 vanilla file overrides (Section 7.4.1), global defines changes (Section 7.4.2), global-variable targeting that isn't multiplayer-safe (moot since v1.3: single-player only), large starting error count (Section 10), missing innovation generator script (Section 7.3; later removed as unused).
