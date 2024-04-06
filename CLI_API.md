# SkyTemple Randomizer CLI API

Documentation for version: `2.0.0`

The Randomizer can be controlled via CLI API. It supports randomizing the game but also
provides access to all the information from a ROM which is also available via 
GUI (monster names, item names, abilities, etc.).

To access it run `skytemple_randomizer cli <subcommand>` or `python -m skytemple.randomizer.main cli <subcommand>`.

The API is designed to be consumed by other applications as such optimized to be machine-readable and
the output is stable. Errors are also printed on stdout. Additional diagnostic info may be printed on stderr.

## Table of Contents
* [Data Structures](#data-structures)
  + [Config JSON](#config-json)
    - [`.chapters.randomize`](#-chaptersrandomize-)
    - [`.chapters.text`](#-chapterstext-)
    - [`.dungeons.fixed_rooms`](#-dungeonsfixed-rooms-)
    - [`.dungeons.items`](#-dungeonsitems-)
    - [`.dungeons.items_enabled`](#-dungeonsitems-enabled-)
    - [`.dungeons.layouts`](#-dungeonslayouts-)
    - [`.dungeons.max_floor_change_percent`](#-dungeonsmax-floor-change-percent-)
    - [`.dungeons.max_hs_chance`](#-dungeonsmax-hs-chance-)
    - [`.dungeons.max_ks_chance`](#-dungeonsmax-ks-chance-)
    - [`.dungeons.max_mh_chance`](#-dungeonsmax-mh-chance-)
    - [`.dungeons.max_sticky_chance`](#-dungeonsmax-sticky-chance-)
    - [`.dungeons.min_floor_change_percent`](#-dungeonsmin-floor-change-percent-)
    - [`.dungeons.mode`](#-dungeonsmode-)
    - [`.dungeons.pokemon`](#-dungeonspokemon-)
    - [`.dungeons.random_weather_chance`](#-dungeonsrandom-weather-chance-)
    - [`.dungeons.settings`](#-dungeonssettings-)
      * [`.dungeons.settings.[].randomize`](#-dungeonssettings--randomize-)
      * [`.dungeons.settings.[].unlock`](#-dungeonssettings--unlock-)
      * [`.dungeons.settings.[].randomize_weather`](#-dungeonssettings--randomize-weather-)
      * [`.dungeons.settings.[].monster_houses`](#-dungeonssettings--monster-houses-)
      * [`.dungeons.settings.[].enemy_iq`](#-dungeonssettings--enemy-iq-)
    - [`.dungeons.traps`](#-dungeonstraps-)
    - [`.dungeons.weather`](#-dungeonsweather-)
    - [`.improvements.download_portraits`](#-improvementsdownload-portraits-)
    - [`.improvements.patch_moveshortcuts`](#-improvementspatch-moveshortcuts-)
    - [`.improvements.patch_unuseddungeonchance`](#-improvementspatch-unuseddungeonchance-)
    - [`.improvements.patch_totalteamcontrol`](#-improvementspatch-totalteamcontrol-)
    - [`.improvements.patch_disarm_monster_houses`](#-improvementspatch-disarm-monster-houses-)
    - [`.improvements.patch_fixmemorysoftlock`](#-improvementspatch-fixmemorysoftlock-)
    - [`.iq.randomize_tactics`](#-iqrandomize-tactics-)
    - [`.iq.randomize_iq_gain`](#-iqrandomize-iq-gain-)
    - [`.iq.randomize_iq_skills`](#-iqrandomize-iq-skills-)
    - [`.iq.randomize_iq_groups`](#-iqrandomize-iq-groups-)
    - [`.iq.keep_universal_skills`](#-iqkeep-universal-skills-)
    - [`.item.algorithm`](#-itemalgorithm-)
    - [`.item.global_items`](#-itemglobal-items-)
    - [`.item.weights`](#-itemweights-)
    - [`.locations.randomize`](#-locationsrandomize-)
    - [`.locations.first`](#-locationsfirst-)
    - [`.locations.second`](#-locationssecond-)
    - [`.pokemon.abilities`](#-pokemonabilities-)
    - [`.pokemon.abilities_enabled`](#-pokemonabilities-enabled-)
    - [`.pokemon.iq_groups`](#-pokemoniq-groups-)
    - [`.pokemon.monsters_enabled`](#-pokemonmonsters-enabled-)
    - [`.pokemon.moves_enabled`](#-pokemonmoves-enabled-)
    - [`.pokemon.movesets`](#-pokemonmovesets-)
    - [`.pokemon.starters_enabled`](#-pokemonstarters-enabled-)
    - [`.pokemon.tm_hm_movesets`](#-pokemontm-hm-movesets-)
    - [`.pokemon.tms_hms`](#-pokemontms-hms-)
    - [`.pokemon.typings`](#-pokemontypings-)
    - [`.quiz.include_vanilla_questions`](#-quizinclude-vanilla-questions-)
    - [`.quiz.mode`](#-quizmode-)
    - [`.quiz.questions`](#-quizquestions-)
      * [`.quiz.questions.[].question`](#-quizquestions--question-)
      * [`.quiz.questions.[].answers`](#-quizquestions--answers-)
    - [`.quiz.randomize`](#-quizrandomize-)
    - [`.seed`](#-seed-)
    - [`.starters_npcs.explorer_rank_rewards`](#-starters-npcsexplorer-rank-rewards-)
    - [`.starters_npcs.explorer_rank_unlocks`](#-starters-npcsexplorer-rank-unlocks-)
    - [`.starters_npcs.native_file_handlers`](#-starters-npcsnative-file-handlers-)
    - [`.starters_npcs.npcs`](#-starters-npcsnpcs-)
    - [`.starters_npcs.overworld_music`](#-starters-npcsoverworld-music-)
    - [`.starters_npcs.starters`](#-starters-npcsstarters-)
    - [`.starters_npcs.topmenu_music`](#-starters-npcstopmenu-music-)
    - [`.text.instant`](#-textinstant-)
    - [`.text.main`](#-textmain-)
    - [`.text.story`](#-textstory-)
  + [Error JSON](#error-json)
    - [`.error_msg`](#-error-msg-)
    - [`.error_type`](#-error-type-)
    - [`.internal_error`](#-internal-error-)
    - [`.traceback`](#-traceback-)
  + [ROM-Info JSON](#rom-info-json)
    - [`.edition`](#-edition-)
  + [Progress JSON](#progress-json)
    - [`.current_step`](#-current-step-)
    - [`.total_steps`](#-total-steps-)
    - [`.current_step_description`](#-current-step-description-)
  + [Done JSON](#done-json)
    - [`.done`](#-done-)
* [Commands](#commands)
  + [`randomize`](#-randomize-)
  + [`default-config`](#-default-config-)
  + [`info-rom`](#-info-rom-)
  + [`ppmdu-config`](#-ppmdu-config-)
  + [`info-monsters`](#-info-monsters-)
  + [`info-items`](#-info-items-)
  + [`info-item-categories`](#-info-item-categories-)
  + [`info-moves`](#-info-moves-)
  + [`info-abilities`](#-info-abilities-)
  + [`info-dungeons`](#-info-dungeons-)

## Data Structures

### Config JSON
This part of the API is stable for each MINOR release of the randomizer. It may change with each PATCH update, however,
the Randomizer WILL then accept Config JSONs from previous versions for compatibility reasons (same MINOR version).

The Config JSON is the configuration for the Randomizer. It is also used by the CLI (can be ex- and imported) from
the settings. It has the following structure (`jq` style):

#### `.chapters.randomize`
Type: Boolean

Whether to randomize chapter titles or not. Possible titles are taken from `.chapters.text`.

#### `.chapters.text`
Type: String; Newline seperated list of Strings

List of possible chapter titles. The list is newline seperated (`\n`), however the strings themselves may also contain
escaped newlines (`\\n`).

#### `.dungeons.fixed_rooms`
Type: Boolean

If true, some fixed rooms (notably boss fights) are replaced with a random layout.

#### `.dungeons.items`
Type: Boolean

If true, items in dungeons are randomized.

#### `.dungeons.items_enabled`
Type: Array of Integers

A list of Item IDs that can be used for random items. This will also affect item randomization outside of dungeons.

#### `.dungeons.layouts`
Type: Boolean

If true, dungeon layouts, tilesets, music and other properties are randomized.

#### `.dungeons.max_floor_change_percent`
Type: Integer

The maximum amount of floors to add to a dungeon during randomization (in %).

#### `.dungeons.max_hs_chance`
Type: Number

The maximum chance that can be set for a dungeon floor to spawn hidden stairs.

#### `.dungeons.max_ks_chance`
Type: Number

The maximum chance that can be set for a dungeon floor to spawn Kecleon shops.

#### `.dungeons.max_mh_chance`
Type: Number

The maximum chance that can be set for a dungeon floor to spawn monster houses.

#### `.dungeons.max_sticky_chance`
Type: Number

The maximum chance that can be set for a dungeon floor to spawn sticky items.

#### `.dungeons.min_floor_change_percent`
Type: Integer

The maximum amount of floors to remove from a dungeon during randomization (in %).

#### `.dungeons.mode`
Type: Integer; Enum

- 0: Fully random: Each floor gets randomized with random settings. 
- 1: Consistent per dungeon: Each floor in the same dungeon gets randomized with (some) of the same settings.

#### `.dungeons.pokemon`
Type: Boolean

If true, monster spawns on dungeon floors are randomized.

#### `.dungeons.random_weather_chance`
Type: Number

The maximum chance for random non-clear weather on a dungeon floor. Only relevant if `.dungeons.weather` is true.

#### `.dungeons.settings`
Type: Object

A list of settings for each individual dungeon. Keys are the dungeon IDs.

##### `.dungeons.settings.[].randomize`
Type: Boolean

If false, this dungeon floor will not be affected by any randomization settings.

##### `.dungeons.settings.[].unlock`
Type: Boolean

If true, this dungeon will be unlocked from the beginning of the game.

##### `.dungeons.settings.[].randomize_weather`
Type: Boolean

If false, random weather randomization does not apply to floors of this dungeon.

##### `.dungeons.settings.[].monster_houses`
Type: Boolean

If false, monster houses will not spawn in this dungeon.

##### `.dungeons.settings.[].enemy_iq`
Type: Boolean

If false, enemy IQ is not randomized in this dungeon, regardless of other settings.


#### `.dungeons.traps`
Type: Boolean

If true, trap spawns on dungeon floors are randomized.

#### `.dungeons.weather`
Type: Boolean

If true, weather for dungeon floors will be randomized.

#### `.improvements.download_portraits`
Type: Boolean

If true, portraits and sprites from https://sprites.pmdcollab.org (or rather [SpriteServer](https://spriteserver.pmdcollab.org))
are downloaded and applied to the game for all NPCs and starter options.

#### `.improvements.patch_moveshortcuts`
Type: Boolean

If true, the patch MoveShortcuts is applied: [Documentation](https://github.com/SkyTemple/skytemple-files/blob/1.6.6/skytemple_files/patch/handler/move_shortcuts.py#L42-L54).

#### `.improvements.patch_unuseddungeonchance`
Type: Boolean

If true, the patch UnusedDungeonChance is applied: [Documentation](https://github.com/SkyTemple/skytemple-files/blob/1.6.6/skytemple_files/patch/handler/unused_dungeon_chance.py#L42-L54).

#### `.improvements.patch_totalteamcontrol`
Type: Boolean

If true, the patch CompleteTeamControl is applied: [Documentation](https://github.com/SkyTemple/skytemple-files/blob/1.6.6/skytemple_files/patch/handler/complete_team_control.py#L114-L126).

#### `.improvements.patch_disarm_monster_houses`
Type: Boolean

If true, the patch DisarmOneRoomMonsterHouses is applied: [Documentation](https://github.com/SkyTemple/skytemple-files/blob/1.6.6/skytemple_files/patch/handler/disarm_one_room_mh.py#L37-L49).

#### `.improvements.patch_fixmemorysoftlock`
Type: Boolean

If true, the patch FixMemorySoftlock is applied: [Documentation](https://github.com/SkyTemple/skytemple-files/blob/1.6.6/skytemple_files/patch/handler/fix_memory_softlock.py#L40-L52).

#### `.iq.randomize_tactics`
Type: Boolean

If true, tactics are fully unlocked at random levels. One random tactic is available from the beginning. 

#### `.iq.randomize_iq_gain`
Type: Boolean

If true, the amount of belly the gummies fill and the amount of IQ they give are fully random for each type.

#### `.iq.randomize_iq_skills`
Type: Boolean

If true, IQ skills are unlocked at random IQ amounts. Item Master is always unlocked.

#### `.iq.randomize_iq_groups`
Type: Boolean

If true, IQ skills are assigned to random IQ groups (but at least one). Item Master is always in all groups.

#### `.iq.keep_universal_skills`
Type: Boolean

If true, all skills that are included in all groups in the base game will also be added to all groups when randomizing.
On top of that, even if "randomize IQ skill unlocks" is enabled, Course Checker, Item Catcher, Item Master, and 
Exclusive Move-User will always be unlocked from the start.
However, Status Checker, Nontraitor, and Lava Evader will still have randomized IQ values.

#### `.item.algorithm`
Type: Integer; Enum

- 0: Balanced: Tries to make it equally likely to find any item in the game, the only exception being Poké which is boosted.
- 1: Classic: Algorithm that was used in the Randomizer prior to version 1.4. 
     It doesn't attempt to balance out the different item categories, making items from categories with fewer total 
     items easier to find.

#### `.item.global_items`
Type: Boolean

If true, items in global item lists (rewards, Treasure Town shops, etc.) are randomized.

#### `.item.weights`
Type: Object

A mapping of weights for each item category, controlling how likely items from each category are to spawn.
The keys are IDs of item categories, the values are numbers representing the weight. Higher weights are
more likely to spawn. 

Only relevant if `.item.algorithm` is 0.

#### `.locations.randomize`
Type: Boolean

If true, location names are randomized. All locations in the game get assigned a new name consisting of two words,
where the first word is taken from `.locations.first` and the second from `.locations.second`.

#### `.locations.first`
Type: Strings; List of newline seperated strings

See `.locations.randomize` for more info.

#### `.locations.second`
Type: Strings; List of newline seperated strings

See `.locations.randomize` for more info.

#### `.pokemon.abilities`
Type: Boolean

If true, monsters in the game are assigned random abilities from the list `.pokemon.abilities_enabled` 

#### `.pokemon.abilities_enabled`
Type: Array of Integers

A list of Ability IDs that can be used for random abilities.

#### `.pokemon.iq_groups`
Type: Boolean

If true, all monsters in the game a assigned a random IQ group.

#### `.pokemon.monsters_enabled`
Type: Array of Integers

A list of monster group IDs that can be used by ANY other randomization options (eg. for NPCs or monsters in dungeons).

#### `.pokemon.moves_enabled`
Type: Array of Integers

A list of moves that can be used by ANY other randomization options (eg. for random movesets or TM/HM moves). 

#### `.pokemon.movesets`
Type: Boolean

If true, what moves monsters can learn by level-up is randomized.

#### `.pokemon.starters_enabled`
Type: Array of Integers

A list of monster group IDs that can be used for starter options if `.starters_npcs.starters` is true.

#### `.pokemon.tm_hm_movesets`
Type: Boolean

If true, what monster can learn which TMs/HMs is randomized.

#### `.pokemon.tms_hms`
Type: Boolean

If true, the moves TMs and HMs contain are randomized.

#### `.pokemon.typings`
Type: Boolean

If true, the typings of monsters are randomized.

#### `.quiz.include_vanilla_questions`
Type: Boolean

If true, the personality test may also contain the questions already stored in ROM, in addition to the questions in
`.quiz.questions`.

Only relevant if `.quiz.randomize` is true.

#### `.quiz.mode`
Type: Integer; Enum

- 0: TEST: Perform the personality test as in the original game 
- 1: TEST_AND_ASK: Perform the personality test as in the original game, but afterwards give the player the option
     to select another starter from a list.
- 2: ASK: Do not perform a personality test, just ask the player from a list, what starter they want to pick. 

#### `.quiz.questions`
Type: Array

List of questions that may appear in the personality test.

Only relevant if `.quiz.randomize` is true.

##### `.quiz.questions.[].question`
Type: String

The question the player will be presented with.

##### `.quiz.questions.[].answers`
Type: Array of Strings

List of possible answers the player can pick for this question. All questions must have at least two answers. 
2-4 answers will be randomly picked for each question used.

#### `.quiz.randomize`
Type: Boolean

If true, the questions in the personality test are randomized.

#### `.seed`
Type: String

The starting seed number to use for the random number generator. If given an empty string the current system time
is used instead.

#### `.starters_npcs.explorer_rank_rewards`
Type: Boolean

If true, Explorer Ranks give random items as rewards upon unlocking a new level.

#### `.starters_npcs.explorer_rank_unlocks`
Type: Boolean

If true, Explorer Rank Levels are randomly unlocked. The cap for Master Rank unlock is max. 200000 points.

#### `.starters_npcs.native_file_handlers`
Type: Boolean

If true, the randomizer uses faster implementations to manipulate the files in the ROM.
This can affect the random values rolled during the randomization.

This should only be disabled if you run into issues.

#### `.starters_npcs.npcs`
Type: Boolean

If true, NPCs are randomized. Other places were NPCs appear are also changed if technically possible 
(boss fights, special episode player characters, etc.).

#### `.starters_npcs.overworld_music`
Type: Boolean

If true, the music that plays in overworld scenes is randomized (for the most part).

#### `.starters_npcs.starters`
Type: Boolean

If true, the player and partner starter options are randomized.

#### `.starters_npcs.topmenu_music`
Type: Boolean

If true, the music that plays on the title screen is randomized.

#### `.text.instant`
Type: Boolean

If true, the text in the game will appear instantly.

#### `.text.main`
Type: Boolean

If true, randomize the game's main text file. This contains everything except for most of the overworld dialogue. 
The randomization is done in a way that (in most cases) similar categories of texts are shuffled.

Potentially unstable! Not supported for the JP ROM (setting ignored).

#### `.text.story`
Type: Boolean

If true, randomize the game's overworld scene text. ALL overworld text is shuffled.

Potentially unstable! Not supported for the JP ROM (setting ignored).

### Error JSON
The Error JSON is returned when unrecoverable errors occur. It has the following structure (`jq` style):

#### `.error_msg`
Type: String

The error message.

#### `.error_type`
Type: String or Null

Python exception type of the error.

#### `.internal_error`
Type: Boolean

If false, this error is almost certainly due to wrong input. If true it is almost certainly an application error.

#### `.traceback`
Type: String or Null

Python exception traceback of the error.

### ROM-Info JSON
General metadata about a ROM. More info may be added in any new version.

#### `.edition`
Type: String

The game edition as [ppmdu edition string](https://github.com/SkyTemple/skytemple-files/blob/1.6.6/skytemple_files/_resources/ppmdu_config/pmd2data.xml#L37-L51).

### Progress JSON
Current Randomization progress. The total number of steps and the descriptions can vary between settings and may change
with any new version.

#### `.current_step`
Type: Integer

Number that usually increases with each new progress. Represents the number of the current step that is being processed.

#### `.total_steps`
Type: Integer

Total number of steps before the randomization is done. `.current_step` should always be lower or equal to this number,
but this doesn't have to be the case. Use "Done JSON" to detect the end of Randomization instead!

#### `.current_step_description`
Type: String

Human-readable description of the current step.

### Done JSON
Marker to signal the end of randomization.

#### `.done`
Always true.

## Commands

### `randomize`
Usage: `randomize INPUT_ROM CONFIG OUTPUT_ROM`
Return format: A stream of JSON lines, where each line is "Progress JSON", "Error JSON" or "Done JSON". The
     latter two are only returned as the last lines.

Runs the randomization. Each progress update is printed as JSON in a new line. The last line are either "Error JSON" or
"Done JSON". If the last line is "Error JSON", randomization failed. If the last line is "Done JSON" is succeeded.

The last line before the process exists may or may not be newline terminated. In rare cases additional "Progress JSON"
lines may be printed after "Error JSON" or "Done JSON", these must be ignored. Do not kill the process after "Done JSON"
is printed. After "Done JSON" is printed the Randomizer will save the ROM file. Only after the process has finished
with a non-zero exit code is the output ROM readable.

- `INPUT_ROM` is the path to the input ROM file.
- `CONFIG` is the path to a "Config JSON". 
- `OUTPUT_ROM` is the path where the randomized ROM will be saved to on success.

Tip: You can run the randomization with default settings with Bash by using process substitution:

```bash
skytemple_randomizer cli randomize rom.nds <(skytemple_randomizer cli default-config rom.nds) output.nds
```

### `default-config`
Usage: `default-config ROM`
Return format on success: Config JSON
Return format on error: Error JSON

Prints the default config for the given ROM as JSON.

### `info-rom`
Usage: `info-rom ROM`
Return format on success: ROM-Info JSON
Return format on error: Error JSON

Prints general metadata information about the ROM.

### `ppmdu-config`
Usage: `ppmdu-config`
Return format on success: Merged [PPMDU Config XML](https://github.com/SkyTemple/skytemple-files/tree/1.6.6/skytemple_files/_resources/ppmdu_config)
Return format on error: Error JSON

Prints the PPMDU config. Exact XML format is not documented. This can be considered reasonably stable but should be 
relied upon with caution.

### `info-monsters`
Usage: `info-monsters ROM`
Return format on success: JSON object where keys are monster group IDs and values are their name. 
Return format on error: Error JSON

Prints a mapping of monster IDs and their names.

### `info-items`
Usage: `info-items ROM`
Return format on success: JSON object where keys are item IDs and values are their name. 
Return format on error: Error JSON

Prints a mapping of item IDs and their names.

### `info-item-categories`
Usage: `info-item-categories ROM`
Return format on success: JSON object where keys are item category IDs and values are their name. 
Return format on error: Error JSON

Prints a mapping of item category IDs and their names. Only relevant category IDs are returned.

### `info-moves`
Usage: `info-moves ROM`
Return format on success: JSON object where keys are move IDs and values are their name. 
Return format on error: Error JSON

Prints a mapping of move IDs and their names.

### `info-abilities`
Usage: `info-abilities ROM`
Return format on success: JSON object where keys are ability IDs and values are their name. 
Return format on error: Error JSON

Prints a mapping of ability IDs and their names.

### `info-dungeons`
Usage: `info-dungeons ROM`
Return format on success: JSON object where keys are dungeons IDs and values a list of names (see below). 
Return format on error: Error JSON

Prints a mapping of dungeon IDs and their names. The names are an array with two strings. The first string
is the main dungeon name, the second is the selection dungeon name.
