# Source verification and outstanding runtime checks

Evidence: user-supplied FDDA Enhanced, Food and Drinks, FDDA Redone, Demonized FDDA New Time Events, Living Devices v1.6, Cigarette Ember Light 1.1, Smoke Longer; local October 11 engine snapshot at `xray-monolith-2026.10.11`.

- FDDA Redone `mod_system_enjoy_cigarettes.ltx` declares `item_ea_cigarettes_orig_hud` inheriting existing cigarette assets. Our HUD inherits this section and supplies three new animation aliases. Existing model references remain dependencies; native OGF files were not supplied or bundled. Their effective motion references must be confirmed by the runtime preflight.
- `liz_fdda_redone_consumables.script` calls native `game.play_hud_motion` with both hands and configured speed, and calls `db.actor:eat(item)` for normal consumption. Our controller does not invoke its action runner.
- October 11 `src/xrGame/level_script.cpp:1718-1750,2996-3000` exports HUD playback, motion length and safe motion-name queries. `player_hud.cpp:1612-1714` selects separate hand/item motions; `motion_length:1040-1052` returns zero for looping clips. We use the engine return value for state timing.
- `src/xrEngine/SkeletonMotions.cpp:82-255,354-376,471-484` supplies the OMF version-four definition, track, compression, CRC and mark layouts used by build_clips.py. Source hand/item tracks were sliced at identical frames. New clips have no inherited event marks. Original item motions and definitions are unchanged byte-for-byte.
- `src/Layers/xrRender/SkeletonAnimated.cpp:808-835` supports wildcard OMF references. A separate hand OMF is placed alongside the FDDA sequence. Effective hand-model wildcard loading remains an in-game check; missing/non-stopping motions are rejected by the controller's returned-duration check.
- `src/xrGame/script_game_object.cpp:1077-1104`, `Inventory.cpp:1106-1170`, `eatable_item.cpp:123-180`, and Lua exports in `script_game_object_script3.cpp` establish synchronous native Eat, ownership checks, item effects and remaining-use decrement. One use is charged at lighting completion, not per drag. The default FX wrapper is suppressed only during this one native consumption call.
- `script_light_script.cpp` exposes HUD-mode script lights. New light code is independent of optional addon scripts. Existing FDDA `ciga_effects.script` identifies the native particle resource; our controller schedules its own short emission, without invoking that script or its time events.
- Supplied `_g.script` defines hide_hud_inventory; `actor_menu.script` defines is_hud_free. Supplied axr_main declares the key press/hold/release, update, save/load, and actor-destroy events used here. Custom functor integration is optional and checked for file existence; F8 is the fallback.

## Prototype boundaries

This is a script-controlled smoking session, not a detector-class conversion. The three standard cigarette packs share a visual. Eight drags/120 seconds are prototype tuning values. There is no persistent partial cigarette and no staged shortening. Normal cigarette bonuses/penalties occur once when lighting completes. Interrupting a lit session wastes the remainder. Menus/save/load/death/map change terminate the session rather than serialize it. Isolated audio is deferred.

## Clip selection

The source long hand motion has 1,343 frames, and its item motion has 1,344. Lighting uses frames 0..420, idle repeats frame 420, and puff uses 420..630, at speed 2 (30 source frames/second). These cuts are preliminary and selected against source timing references, not rendered inspection. Their visual continuity and whether one extracted clip reads as exactly one drag require user testing. Native preflight checks each item motion before starting; hand timing failures abort and clear the session.

## Validation

`texlua development/controller_fixtures.lua <project-root>` exercises consumption, blocked/repeated input, cancellation, menus, save/load, map/death, burn timeout, failed consumption, foreign/empty packs, missing motions, busy HUD, F8, and effect cleanup using mocks. Lua runtime is the container's Lua 5.3/texlua, not GAMMA's LuaJIT. The production script uses Lua 5.1-compatible syntax. `check_assets.py` independently checks generated tracks against source slices and original item preservation, and checks aliases/XML/package paths. No in-game success is claimed.

## User test evidence and 0.1.1 rationale

Uploaded `xray_erik(20261015-171637).log` records two 0.1.0 sessions, one pack use each (3->2 and 2->1), successful puff/idle transitions, and clean stop reasons. The supplied 22.97-second video visibly shows pack extraction and a filter-forward frozen idle pose. Revision 0.1.1 shifts idle to the later upright pose and extends the initial preparation without guessing a new global hand offset. The new puff begins at that pose and ends on a similar rest pose. Visual alignment is still a user-test outcome, not certified by binary checks.

FDDA's `ciga_effects.ciga_start` schedules light flashes through `ea_light.light_on`; that helper only creates/moves a script light. The user reports a lighter-strike sound with no corresponding visible animation. The exact driver of that sound and presence of a lighter mesh in the effective native cigarette OGF have not been established. No invented lighter model path or unsupported animation alias was added. Ordinary FDDA smoking comparison is needed before claiming a lighter-animation fix.

## Revision 0.1.2 — preserve working motion, close endpoints

The newer log confirms use consumption down to 1->0 and repeated successful puff/idle transitions. The new video exposes the item reset on the return transition. Keep the 0.1.1 rest/drag trajectory, but correct each local hand/item bone toward its idle endpoint using a smooth quaternion/translation delta over source frames 510..570. Frames through 510 preserve the source outgoing motion; the final pose and 60-frame guard tail match idle. Check start/end pose equivalence after binary re-encoding, not only the construction input. NumPy/SciPy are development dependencies only.

October 11 `player_hud::script_anim_play` recreates the item model on each call. `CKinematicsAnimated::IBlendSetup` initializes mixing playback at EPS_S weight, whereas nonmixing begins at weight 1. Use nonmixing playback now that hand/item endpoints match. Append 60 matching rest frames to finite clips; transition using active-frame/total-frame ratio while the native motion remains alive. This avoids ordinary automatic StopScriptAnim before the script can enter idle. A render-thread stall longer than the roughly one-second guard remains a runtime edge case, not a zero-gap guarantee under every scheduler condition.

Charge at 281/481 of the returned 481-frame intro duration, restoring the approximate 4.7-second 0.1.0 event timing while preserving the 421 active-frame preparation. FX_SUPPRESS diagnostics confirm when the default actor_effects visual/audio wrapper is bypassed. Other installed native-use sound listeners are not rewritten. This restores earlier trigger timing; exact sound synchronization remains for user verification.

## Revision 0.1.3 — independent audio/exhale timing

The latest supplied video/log confirms 0.1.2 consumption and transitions. Keep its two OMF files byte-identical. User requests ignition roughly one second earlier and smoke/exhale during the lowered motion.

Found the native sound driver in October 11 ActorCondition.cpp:1010-1051: ApplyInfluence and ApplyBooster read `use_sound` directly and manage m_use_sound. Actor-effect Lua suppression cannot stop that native recording. Avoid runtime pSettings mutation or modifying unrelated sound volume. A DLTX patch routes the three supported packs to a short silent native cue and records their verified baseline ordinary-use path `interface\inv_smoke` in a separate field. That baseline is explicitly supplied in configs/items/items/items_drink.ltx for all three packs. An actor_on_item_use callback replays it for ordinary use, skipping only our synchronous interactive Eat. A later native item-use callback replaces that fallback sound as appropriate. No inventory class, normal item stats, consumption or other native-use listener is removed. Inherited pack variants carrying the route can also use the ordinary fallback. Profiles with a custom replacement of the baseline inv_smoke cue need separate evaluation.

Own ignition triggers at 3,686ms, one second before the former 4,686ms use-event trigger. Consumption timing remains as 0.1.2. Own smoke/exhale trigger together at 2,100ms of each drag. Ignition/exhale are 0.85/1.15-second excerpts of the user-supplied FDDA ciga1_long.ogg at 4.10/8.16 seconds, with short edge fades. No voice synthesis or unrelated audio is used. build_audio.py packages native v3 Ogg user-comment metadata; SoundRender_Source_loader.cpp:108-138 defines its binary layout. CRCs of rewritten Ogg pages are recalculated and independently checked. `script_sound_script.cpp` exports sound_object playback and stopping. The three original optional addons remain unnecessary.

Ordinary-use audio baseline, cancelled/failed interactive consumption, missing/overridden routing, exact event timing, shared smoke/audio event, single emission per drag and lifecycle sound cleanup are covered by mocked tests. Exact perceived audio alignment and timbre remain in-game test outcomes. This adds no lighter mesh or new lighter hand animation.

## Revision 0.1.4 — ignition flash and activation evidence

User log xray_erik(20261015-182337).log shows READY and two AUDIO regular events, no MOTION, CONSUME or start failure. This proves the controller loaded and ordinary-use callback ran, not that disabling Smoke Longer blocked an interactive request. Smoke Longer only replaces the FDDA animation mutator/menu script; no references to that script exist in this controller. Add request/rejection/expiry and ordinary-use diagnostics, preserving distinct activation behavior. F8 remains the independent entry point.

User clarifies normal lighting has a visible flash but no lighter mesh. Reimplement FDDA ciga_start's two camera-relative lights (0.15s strike, then 1.3s flame beginning 0.4s later) at our configured ignition cue. Parameters follow supplied ea_light call values; fade is time-based rather than original frame-dependent subtraction. Controller owns cleanup independently, with separate ignition_flash setting. Renderer appearance/position still needs user verification. OMF and audio bytes remain unchanged.

## v0.9 beta promotion

Promote accepted 0.1.4, excluding 0.1.5 diagnostic additions. Only controller version prefix, translated menu label and package metadata change. User log xray_erik(20261015-184847).log records three sessions with one pack use each, nine completed drag exhale events at 2100–2116ms, and clean extinguished/interrupted stops. The 25.7-second video shows the ignition flash, holding/lowering and no obvious reset. Low lighting limits subtle particle-placement assessment. No smoking-controller fault is recorded; unrelated profile startup errors remain outside scope. No raw user logs or video are published.
