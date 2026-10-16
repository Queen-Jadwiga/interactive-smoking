# Interactive Smoking — v0.9.3

Light a cigarette, hold it between drags, and choose when to take each puff. Includes an ignition flash, glowing ember, smoke and exhale cues.

## Changes in v0.9.3

- Holster held items and detectors before smoking to prevent weapon-model overlap.
- Move the cigarette closer and slightly higher.
- Add the initial lighting puff's delayed exhale; improve smoke placement and camera tracking, with two emitters lasting 1.6 seconds by default.
- Play the accepted lift-and-flick disposal on Reload, after the final drag's exhale, or when the cigarette burns out.
- Keep smoking active through saves and autosaves.
- Remove experimental MMB ashing and its animation clips; deferred to a later version.

The v0.9.2 inventory-start fix is retained.

## Requirements

- S.T.A.L.K.E.R. GAMMA with its existing FDDA Redone cigarette models, textures and HUD assets.
- Demonized modded executables: tested on **October 11, 2026**. Other builds have not been verified.

**Living Devices, Cigarette Ember Light and Smoke Longer are optional.** Interactive sessions provide their own effects. This beta supports **Cigarettes, Lucky cigarettes and Russian cigarettes**. Cigars and other tobacco items are planned for later.

## Install

Install `Interactive_Smoking_v0.9.3.zip` through Mod Organizer 2, or download the `end-user` branch with **Code → Download ZIP**. If MO2 does not detect the package automatically, select the folder containing `gamedata` as the data directory.

Put Interactive Smoking **below FDDA and cigarette patches** in MO2's left pane so its animation files and audio routing win conflicts. Replace any earlier Interactive Smoking installation completely. Enable only one version, then restart the game.

## Controls

1. Carry a supported nonempty pack. Right-click it and choose **Smoke interactively (beta)**. Alternatively close all menus, stand still, and press **F8**.
2. Any held weapon/item and detector are holstered first; they remain holstered afterward. Let the lighting sequence finish and the hand lower automatically (approximately nine seconds total).
3. **Hold RMB** to raise and hold the cigarette. Release without clicking to lower silently. A release during the raising animation queues lowering at its end.
4. **Click LMB while holding RMB** to smoke, then lower automatically. A click during raising queues one drag; releasing RMB before raising finishes cancels it. Once a drag starts, releasing RMB lets it finish. Release and press RMB again for the next raise.
5. **Reload**: toss the cigarette. During a drag, disposal waits for its exhale; while raised, the hand lowers first. **F8** or **Escape** cancels immediately.

Ordinary **Use** and FDDA's **Enjoy cigarettes** remain separate actions; select the interactive entry or F8 for this mod's controls.

After the eighth drag and its delayed exhale, the cigarette is tossed automatically.

## Behavior and settings

One pack use is consumed roughly 4.7 seconds into lighting. Normal cigarette bonuses and penalties apply once. The default session permits eight drags and burns out after two minutes. Cancelling before consumption keeps the pack use; extinguishing after lighting wastes the remainder.

Saving, including autosaves, does not end the current session. Opening menus, loading, dying, changing maps, sprinting or climbing ends the session. Saved games do not restore a half-smoked cigarette. There is no persistent half-smoked cigarette or shrinking model. All three packs currently share the same cigarette visual.

Settings are in `gamedata/configs/mod_system_is_smoking.ltx`: drag count, burn duration, ember light, ignition flash, smoke, sound and cue timing, plus smoke emitter count (1–4) and duration (1150–3000 ms). F8 is a fixed fallback key in this beta. Ordinary cigarette use retains its baseline use recording.

## Troubleshooting

If nothing happens, confirm you selected **Smoke interactively (beta)** or F8. If another action is playing, let it finish. Follow any missing-animation or audio-conflict message and check MO2 priority. For problems, report your executable version, enabled cigarette addons, what happened, and attach `appdata/logs/xray_<name>.log`. Relevant entries begin `[InteractiveSmoking 0.9.3]`.

## Uninstall

Extinguish, save, exit completely, and disable the mod in MO2. Consumed pack uses are not refunded.

## Credits

Interaction/controller code by Queen-Jadwiga. Animation and short sound clips derive from the supplied **FDDA Redone — lizzardman** assets; upstream asset credits remain with their creators. Existing GAMMA/FDDA models, textures and native particle resources are referenced. No scripts from the three optional addons are bundled.

