#!/usr/bin/env python3
"""Steward's tool for the class vial-to-rack dataset.

Run it in the LeRobot virtual environment on the host (it only needs pandas/pyarrow,
which LeRobot installs). A "part" is one recording session's dataset folder,
e.g. datasets/t3_stB_sim_s02.

  python class_data.py check    PART [PART ...]           # does each part match the frozen spec?
  python class_data.py fix      PART_OR_MERGED [...]      # make sim parts mergeable; make merged sets editable
  python class_data.py manifest OUT.csv PART [PART ...]   # episode -> team/station/source/session, in merge order

Give `manifest` the parts in exactly the order you give them to the merge command.
"""
import csv
import glob
import json
import re
import shutil
import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ---- the frozen spec: edit here, nowhere else ---------------------------------------------
TASK = "Pick up the vial and place it in the rack"
CODEBASE = "v3.0"
ROBOT_TYPE = "so101_follower"  # what LeRobot 0.4.3 (the workshop container) writes
FPS = 30
CAMERAS = ("observation.images.ego", "observation.images.external_D455")
IMAGE_SHAPE = [480, 640, 3]
JOINTS = ["shoulder_pan.pos", "shoulder_lift.pos", "elbow_flex.pos",
          "wrist_flex.pos", "wrist_roll.pos", "gripper.pos"]
MAX_EPISODE_S = 45
MIN_EPISODE_S = 3
# Teams 1-5 exist; 6 and 7 are spare for the future. Team 0 is the instructor's and TA's
# test team: its parts pass `check` but are never merged (`manifest` refuses them).
NAME = re.compile(r"^t(?P<team>[0-7])_st(?P<station>[ABC])_(?P<source>sim|real)_s(?P<session>\d\d)$")
TEST_TEAM = "0"
# --------------------------------------------------------------------------------------------


def load(part: Path):
    info = json.loads((part / "meta" / "info.json").read_text())
    tasks = list(pd.read_parquet(part / "meta" / "tasks.parquet").index)
    eps = pd.concat(
        pd.read_parquet(f, columns=["episode_index", "length"])
        for f in sorted(glob.glob(str(part / "meta" / "episodes" / "*" / "*.parquet")))
    ).sort_values("episode_index")
    return info, tasks, eps


def check(part: Path) -> bool:
    problems, notes = [], []
    m = NAME.match(part.name)
    if not m:
        problems.append(f"folder name '{part.name}' is not t<team>_st<A|B|C>_<sim|real>_s<NN> (team 0-7)")
    elif m["team"] == TEST_TEAM:
        notes.append("team 0 is the instructor/TA test team - this part must not go into the merge")
    try:
        info, tasks, eps = load(part)
    except Exception as e:  # noqa: BLE001
        print(f"FAIL  {part.name}\n      cannot read dataset: {e}")
        return False
    feats = info["features"]

    if info.get("codebase_version") != CODEBASE:
        problems.append(f"codebase_version is {info.get('codebase_version')}, expected {CODEBASE}")
    if info.get("robot_type") != ROBOT_TYPE:
        problems.append(
            f"robot_type is '{info.get('robot_type')}', expected '{ROBOT_TYPE}'. "
            "'so_follower' means it was recorded with LeRobot 0.5+ on the host, where joints "
            "default to degrees instead of the -100..100 scale. Do not merge it."
        )
    if info.get("fps") != FPS:
        problems.append(f"fps is {info.get('fps')}, expected {FPS}")

    cams = sorted(k for k, v in feats.items() if v.get("dtype") in ("video", "image"))
    if cams != sorted(CAMERAS):
        problems.append(f"cameras are {cams}, expected {sorted(CAMERAS)}")
    for cam in cams:
        if feats[cam].get("dtype") != "video":
            problems.append(f"{cam} is stored as images, not video")
        if list(feats[cam].get("shape", [])) != IMAGE_SHAPE:
            problems.append(f"{cam} shape is {feats[cam].get('shape')}, expected {IMAGE_SHAPE}")
    for key in ("action", "observation.state"):
        if key not in feats:
            problems.append(f"missing feature {key}")
            continue
        if feats[key].get("names") != JOINTS:
            problems.append(f"{key} joint names are {feats[key].get('names')}")
        if "fps" in feats[key]:
            notes.append(f"{key} carries the sim recorder's extra 'fps' key - run `fix` before merging with real parts")

    if tasks != [TASK]:
        problems.append(f"task strings are {tasks}, expected exactly ['{TASK}']")

    secs = eps["length"] / FPS
    long_ = eps.loc[secs > MAX_EPISODE_S, "episode_index"].tolist()
    short = eps.loc[secs < MIN_EPISODE_S, "episode_index"].tolist()
    if long_:
        problems.append(f"episodes longer than {MAX_EPISODE_S}s: {long_}")
    if short:
        problems.append(f"episodes shorter than {MIN_EPISODE_S}s (false start?): {short}")
    if info.get("total_episodes") != len(eps):
        problems.append(f"info.json says {info.get('total_episodes')} episodes, metadata lists {len(eps)}")

    data = pd.concat(
        pd.read_parquet(f, columns=["action", "observation.state"])
        for f in sorted(glob.glob(str(part / "data" / "*" / "*.parquet")))
    )
    for key in ("action", "observation.state"):
        arr = pd.DataFrame(data[key].tolist())
        lo, hi = arr.min().min(), arr.max().max()
        if lo < -101 or hi > 101:
            problems.append(f"{key} values span {lo:.1f}..{hi:.1f}; the -100..100 scale was expected (degrees?)")
        if arr.std().max() < 1e-3:
            problems.append(f"{key} never changes - arm not connected?")

    n_vid = {cam: len(glob.glob(str(part / "videos" / cam / "*" / "*.mp4"))) for cam in cams}
    if any(n == 0 for n in n_vid.values()):
        problems.append(f"missing video files: {n_vid}")

    verdict = "FAIL" if problems else "PASS"
    print(f"{verdict}  {part.name}: {len(eps)} episodes, {int(eps['length'].sum())} frames, "
          f"median {secs.median():.1f}s, longest {secs.max():.1f}s")
    for p in problems:
        print(f"      x {p}")
    for n in notes:
        print(f"      - {n}")
    return not problems


def fix(part: Path) -> None:
    """Remove the non-standard 'fps' key the workshop's sim recorder puts inside the
    action / observation.state feature descriptions. lerobot-record does not write it,
    and LeRobot refuses to merge datasets whose feature descriptions differ."""
    path = part / "meta" / "info.json"
    info = json.loads(path.read_text())
    changed = [k for k in ("action", "observation.state") if info["features"].get(k, {}).pop("fps", None) is not None]
    if changed:
        shutil.copy2(path, path.with_suffix(".json.orig"))
        path.write_text(json.dumps(info, indent=4))
        print(f"fixed {part.name}: removed 'fps' from {changed} (original kept as info.json.orig)")

    # Second repair, for MERGED datasets. The sim recorder writes one episode-metadata file per
    # episode. LeRobot's merge packs them into one file but leaves each row pointing at its old
    # file number, so a later split / delete / re-merge fails with FileNotFoundError. Make every
    # row point at the file it actually lives in. On an untouched part this changes nothing.
    repointed = 0
    for f in sorted(glob.glob(str(part / "meta" / "episodes" / "*" / "*.parquet"))):
        chunk, file = int(Path(f).parent.name.split("-")[1]), int(Path(f).stem.split("-")[1])
        table = pq.read_table(f)
        wrong = sum(c != chunk for c in table["meta/episodes/chunk_index"].to_pylist()) + sum(
            x != file for x in table["meta/episodes/file_index"].to_pylist())
        if not wrong:
            continue
        for col, val in (("meta/episodes/chunk_index", chunk), ("meta/episodes/file_index", file)):
            i = table.schema.get_field_index(col)
            table = table.set_column(i, table.schema.field(i), pa.array([val] * len(table), type=table.schema.field(i).type))
        pq.write_table(table, f)
        repointed += 1
    if repointed:
        print(f"fixed {part.name}: re-pointed episode metadata in {repointed} file(s)")
    if not changed and not repointed:
        print(f"ok    {part.name}: nothing to fix")


def manifest(out: Path, parts: list[Path]) -> None:
    rows, offset = [], 0
    for part in parts:
        m = NAME.match(part.name)
        if not m:
            sys.exit(f"cannot build manifest: bad part name {part.name}")
        if m["team"] == TEST_TEAM:
            sys.exit(f"cannot build manifest: {part.name} is a team-0 test part and must not be merged")
        _, _, eps = load(part)
        for _, e in eps.iterrows():
            rows.append({
                "episode_index": offset + int(e["episode_index"]),
                "part": part.name,
                "episode_in_part": int(e["episode_index"]),
                **m.groupdict(),
                "frames": int(e["length"]),
                "seconds": round(int(e["length"]) / FPS, 2),
            })
        offset += len(eps)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    df = pd.DataFrame(rows)
    print(f"wrote {out}: {len(df)} episodes from {len(parts)} parts")
    print(df.groupby(["source", "team"]).size().unstack(fill_value=0).to_string())


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in ("check", "fix", "manifest"):
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "check":
        results = [check(Path(a.rstrip("/"))) for a in args]
        print(f"\n{sum(results)}/{len(results)} parts pass")
        sys.stdout.flush()
        sys.exit(0 if all(results) else 1)
    if cmd == "fix":
        for a in args:
            fix(Path(a.rstrip("/")))
    if cmd == "manifest":
        manifest(Path(args[0]), [Path(a.rstrip("/")) for a in args[1:]])


if __name__ == "__main__":
    main()
