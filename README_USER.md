# Interactive Smoking — v0.9 beta

Light a cigarette, hold it between drags, and choose when to take each puff. Includes an ignition flash, glowing ember, smoke and exhale cues.

## Requirements

- S.T.A.L.K.E.R. GAMMA with its existing FDDA Redone cigarette models, textures and HUD assets.
- Demonized modded executables: tested on **October 11, 2026**. Other builds have not been verified.

**Living Devices, Cigarette Ember Light and Smoke Longer are optional.** Interactive sessions provide their own effects. This beta supports **Cigarettes, Lucky cigarettes and Russian cigarettes**. Cigars and other tobacco items are planned for later.

## Install

Download the `end-user` branch using **Code → Download ZIP**, or the source ZIP from the v0.9 beta release, and install through Mod Organizer 2. If MO2 does not detect the package automatically, select the folder containing `gamedata` as the data directory.

Put Interactive Smoking **below FDDA and cigarette patches** in MO2's left pane so its animation files and audio routing win conflicts. Replace any earlier Interactive Smoking installation completely. Enable only one version, then restart the game.

## Controls

1. Carry a supported nonempty pack. Right-click it and choose **Smoke interactively (beta)**. Alternatively close all menus, stand still, and press **F8**.
2. Let the lighting sequence finish, approximately seven seconds.
3. Tap your bound **Fire** key for a drag. Holding Fire does not repeat drags.
4. Press **Reload**, **F8**, or **Escape** to extinguish.

Ordinary **Use** and FDDA's **Enjoy cigarettes** remain separate actions; select the interactive entry or F8 for this mod's controls.

## Behavior and settings

One pack use is consumed roughly 4.7 seconds into lighting. Normal cigarette bonuses and penalties apply once. The default session permits eight drags and burns out after two minutes. Cancelling before consumption keeps the pack use; extinguishing after lighting wastes the remainder.

Opening menus, saving, loading, dying, changing maps, sprinting or climbing ends the session. There is no persistent half-smoked cigarette or shrinking model. All three packs currently share the same cigarette visual.

Settings are in `gamedata/configs/mod_system_is_smoking.ltx`: drag count, burn duration, ember light, ignition flash, smoke, sound and cue timing. F8 is a fixed fallback key in this beta. Ordinary cigarette use retains its baseline use recording.

## Troubleshooting

If nothing happens, confirm you selected **Smoke interactively (beta)** or F8. If another action is playing, let it finish. Follow any missing-animation or audio-conflict message and check MO2 priority. For problems, report your executable version, enabled cigarette addons, what happened, and attach `appdata/logs/xray_<name>.log`. Relevant entries begin `[InteractiveSmoking 0.9]`.

## Uninstall

Extinguish, save, exit completely, and disable the mod in MO2. Consumed pack uses are not refunded.

## Credits

Interaction/controller code by Queen-Jadwiga. Animation and short sound clips derive from the supplied **FDDA Redone — lizzardman** assets; upstream asset credits remain with their creators. Existing GAMMA/FDDA models, textures and native particle resources are referenced. No scripts from the three optional addons are bundled.

This beta preserves the accepted 0.1.4 behavior. The author tested ignition, manual drags, lowering and stopping in game; this is not a claim of compatibility with every GAMMA profile.
