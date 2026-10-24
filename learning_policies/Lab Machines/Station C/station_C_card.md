# Station Card: Vial-to-Rack Recording

Oct 21, 2026 · Ziad Youssfi

One copy per station. The TA fills in the table at the top once; everything below it is the same at every station. Keep this open during every session. The step-by-step commands are in the student guide; this card is the checklist.

## This station

| Item | Value |
| --- | --- |
| Station letter | C |
| PC account | `robotlab` (same on every station; password from the TA) |
| Leader arm ID | `stC_teleop` |
| Follower arm ID | `stC_robot` |
| Leader port, follower port | `/dev/ttyACM0` , `/dev/ttyACM1` |
| Gripper camera number, fixed camera number | `2` , `0` |
| Session log | [link](https://docs.google.com/spreadsheets/d/1Yh-T71ASylh94ZUB-DemJ7aDxTGWTZ57rfiZK28g5YE/edit?usp=sharing) |

The ports and camera numbers are already saved on the PC; they are here so you can tell when something has changed.

## Before you start, every session

- [ ] Logged in as `robotlab`. Session log and this card open in the browser.
- [ ] Part name decided: `t<team>_st<station>_<sim or real>_s<NN>`, with the next session number from the log.
- [ ] Roles agreed: one person drives the leader arm, one types. For a real session, a third person stays by the follower's power switch.
- [ ] Leader arm plugged in. For a simulated session, fold it into its packed position before starting the simulator.

For a real session, also:

- [ ] Clamp tight. Move every follower joint by hand through its full range; nothing binds.
- [ ] Cables routed so they cannot snag or stop a joint.
- [ ] Follower power LED on. Light on, at the marked brightness.
- [ ] Rack on the LEFT. Black mat flat. Vials on the RIGHT.
- [ ] Both camera views show the rack, the mat and the gripper. No glare, nothing blocking.
- [ ] Calibration check prints `Overall: ✓ PASS`. If not: stop, tell the TA, do not record.

Never recalibrate. If a command offers to keep the existing calibration or type `c` for a new one, press **Enter** and tell the TA.

## Recording an episode

1. Arm in its start pose. Place 1 to 3 vials on the right side of the mat in new positions, **before** recording starts. In the simulator, **R** does this for you.
2. Drive from the two camera views only, not by looking at the arm or the 3D scene. The policy will see only what the cameras see.
3. One vial, into one empty slot of the rack, upright. Smooth, deliberate motion; no rushing.
4. Stop as soon as the vial is in and the gripper has opened. Between 3 and 45 seconds.
5. A fumble you recover from is good data: keep going and finish. Discard only an attempt that cannot be completed.

Failed attempts never go into the dataset: discard them during recording (**C** in the simulator, **left arrow** on the real arm), or write their episode numbers in the log for the steward to remove.

**What makes an episode unusable:** a blocked or black camera view, the two views swapped, the vial not in the rack, a jerk or a stall, or anything in the workspace that is not the rack, the mat and the vials.

## Names and keys

|  | Exactly this |
| --- | --- |
| Camera names | `ego` is the gripper camera, `external_D455` is the fixed camera. Same names in the simulator and on the real arm. |
| Task sentence | `Pick up the vial and place it in the rack`. It is already in the commands; never retype it. |
| Part name | `t<team>_st<station>_<sim or real>_s<NN>`, for example `t3_stB_sim_s02`. |
| Simulator seed | Team number × 100 + session number. |
| Simulator keys | **R** new random scene · **S** start or stop recording · **C** discard this attempt. Click a viewport first. |
| Real-arm keys | **right arrow** end the episode or the reset period · **left arrow** discard and redo · **Esc** stop after this episode (never mid-attempt). |
| Resolution and rate | 640 × 480 at 30 frames per second. Already set; do not change. |

## Running a policy on the arm

This applies later, when a trained policy drives the follower instead of a person.

- One person at the keyboard, one person with a hand on the follower's power switch, nobody else within reach of the arm.
- Nobody reaches into the workspace while the policy runs. Cut the power first, every time.
- Cut the power if the arm moves toward anything other than a vial or the rack, or faster than a person would drive it.
- Use the printed layout template: ten layouts, two trials each. Record the station letter with every trial.
- A trial succeeds if the vial is upright in the rack with the gripper open within 45 seconds and no vial left the mat.
- Note every collision or dropped vial in the session log.

## End of session

- [ ] Looked at two or three episodes in the viewer; bad episode numbers written down.
- [ ] Checker printed `PASS`. (A `FAIL` means no upload: send the output to the TA.)
- [ ] Part uploaded with `--private`.
- [ ] One row in the session log: part name, date, who drove and who typed, episode count, episodes to remove and why, anything unusual.
- [ ] Typed `exit` in the container; both terminals closed.
- [ ] Light off. It runs warm.
- [ ] Vials back on the right, rack on the left, mat flat.
- [ ] Any collision or dropped vial noted in the log.
- [ ] Logged out of `robotlab`.

Never record into another team's part. Never change a part after uploading it; tell the steward instead.

## Quotas

**40 simulated + 40 real episodes per team**; 30 + 30 is the minimum. Stop when your team reaches its quota or when the freeze time posted on the course page passes, whichever comes first. After the freeze, record nothing until the instructor announces the merged dataset.

**The steward rejects any part that fails the checker or has no row in the log. No appeals.**
