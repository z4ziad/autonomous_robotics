# Student Session Guide: Collecting Vial-to-Rack Episodes

Oct 19, 2026 · @Ziad

One session is one team, at one station, recording either simulated or real episodes, from logging in to logging out. Every team uses the same account on a station; what tells your team's episodes apart from everyone else's is the part name you type in step 4 and the row you write in the session log in step 19. Follow the steps in order; each step is one thing to do. Steps 1 to 5 and 16 to 20 are the same for every session. In between, do steps **6 to 10 for a simulated session** or steps **11 to 15 for a real session**.

## Before you sit down

Have these ready before your reserved time starts, so the whole slot goes to recording.

- **Your team's reservation**, and whether this slot is a simulated session or a real session. A station can do only one of the two at a time.
- **The station card** for this station, open in a browser. It is the shared file with the pre-flight list, the scene layout and the end-of-session list.
- **The session log**, open in a browser. Look up your team's last session number of this kind (simulated or real). This session's number is the next one.
- **Roles.** One person drives the leader arm. One person sits at the keyboard and types the commands. For a real session, a third person keeps a hand near the follower arm's power switch and never reaches into the workspace while the arm moves.
- **The station account's password**. Each station PC has one account, shared by all five teams.

Two things you never have to do: calibrate an arm, or type the task sentence. The arms are already calibrated, and the task sentence is built into the commands below.

## Steps 1 to 5: the start of every session

1. **Log in** to the station PC with the station's shared account. It is the same account for every team; do not create or use any other.
2. **Start the container.** Open a terminal and type:

   ```bash
   bash ~/run_teleop.sh
   ```

   If it asks for a password, type the station account's password. After a few seconds the prompt changes; you are now inside the container, and everything you type in this terminal runs there. Call this **Terminal 1**. Keep it open for the whole session.
3. **Check the station's settings.** In Terminal 1, type:

   ```bash
   echo $TELEOP_PORT $ROBOT_PORT $CAMERA_GRIPPER $CAMERA_EXTERNAL $HF_ORG
   ```

   Five values should appear, for example `/dev/ttyACM1 /dev/ttyACM0 0 2 your-course-org`. If any of the five is missing, stop and message the TA. Do not guess a value.
4. **Name this session's part.** In Terminal 1, type one line of this form, with your own team number, station letter, kind of session, and session number:

   ```bash
   export PART=t3_stB_sim_s02
   ```

   This example means team 3, station B, simulated episodes, the team's second simulated session. For a real session write `real` instead of `sim`. The session number always has two digits. Type it carefully; the part keeps this name forever. Then check that the name is new by typing \`ls datasets/$PART\`. The answer should be \`No such file or directory\`. If a folder is listed instead, another session already used this name, because all teams share this account and this disk. Check the session log and correct the name before going on. The recording commands do not refuse an existing name: they append your new episodes to whatever that folder already holds, so a wrong name mixes two sessions' episodes with no way to tell them apart later. The only exception is when you are deliberately continuing your own session from earlier.
5. **Do the pre-flight list on the station card.** For a real session that is the whole list: clamps, cables, light, rack on the left, vials on the right, both cameras showing the mat. For a simulated session only the leader arm matters: check that it is plugged in, then fold it into its packed position, close to the base, so that the simulated arm does not start inside the rack.

Now continue with step 6 for a simulated session, or step 11 for a real session.

## Steps 6 to 10: a simulated session

You move the leader arm, and a simulated follower arm on the screen copies you. The real follower arm and the real cameras stay switched off.

6. **Start the simulator and the recorder.** In Terminal 1, type the whole block below. Change only the number after `--seed`: it is your team number times 100, plus the session number. Team 3, session 2 gives 302.

   ```bash
   lerobot_agent --task Lerobot-So101-Teleop-Vials-To-Rack-DR \
       --repo_id ${HF_ORG}/${PART} \
       --repo_root $(pwd)/datasets/${PART} \
       --task_name "Pick up the vial and place it in the rack" \
       --seed 302
   ```

   The simulator window opens. The first start of the day takes about two minutes. Leave the task sentence exactly as it is.
7. **Set up the two camera views.** In the simulator window, open the menu **Window**, then **Viewports**, and switch on **Viewport 1** and **Viewport 2**. In one viewport, open its camera menu and choose `gripper_cam`. In the other, choose `Camera_OmniVision_9782_Color`. In each viewport's settings, change the aspect ratio from 16:9 to **4:3**. From now on, drive the arm by looking at these two views only, not at the 3D scene.
8. **Warm up without recording.** Click inside a viewport so the simulator receives your keys. Press **R** to reset the scene and move the arm around for a minute. Pick up a vial and put it down without pressing any other key. Nothing is saved yet. When the motion feels natural, start recording.
9. **Record the episodes.** For each episode:
   - Press **R**. The scene resets with new lighting and new vial positions.
   - Press **S**. Recording starts.
   - Pick up one vial and place it into one empty slot of the rack. Move smoothly; do not rush.
   - Press **S** again. Recording stops and the episode is saved in the background.

   If an attempt cannot be completed, press **C** instead of the second S; the attempt is thrown away. A fumble that you recover from is good data, so keep going and finish the task. The terminal prints `[RACK]` when the simulator sees the vial in the rack. Record the number of episodes your team planned for this slot; ten to twenty is a normal session.
10. **Stop cleanly.** After the last episode, look at Terminal 1 and wait until it prints `No more episodes in queue`. That line means every episode is written to disk. Then press **Ctrl+C** to close the simulator. If the simulator crashes or closes early, run the block from step 6 again with the same part name; the recorder reopens the folder and adds to it.

Now continue with step 16.

## Steps 11 to 15: a real session

You move the leader arm, and the real follower arm copies you. Both cameras record.

11. **Check the calibration.** In Terminal 1, type:

    ```bash
    python docker/real/scripts/so101_check_calibration.py
    ```

    The last line it prints must begin with `Overall: ✓ PASS`. If it does not, stop, message the TA, and do not record in this slot. If any command ever asks whether to use the existing calibration or run a new one, press **Enter** to keep the existing one. Never type `c`.
12. **Only if a USB cable was moved since the last session**, run `lerobot-find-port` and then `lerobot-find-cameras opencv`, and save any changed value with `setenv`, for example `setenv ROBOT_PORT=/dev/ttyACM0`. If nothing was unplugged, skip this step.
13. **Set the scene, then start recording.** Put one to three vials on the right side of the mat in varied positions, the rack on the left, and the follower arm in its start pose. The driver takes the leader arm. Recording of the first episode begins the moment the command below starts, so be ready. In Terminal 1, type the whole block:

    ```bash
    lerobot-record \
      --robot.type=so101_follower --robot.port=$ROBOT_PORT --robot.id=$ROBOT_ID \
      --robot.cameras='{
        "ego":           {"type": "opencv", "index_or_path": '"$CAMERA_GRIPPER"',  "width": 640, "height": 480, "fps": 30},
        "external_D455": {"type": "opencv", "index_or_path": '"$CAMERA_EXTERNAL"', "width": 640, "height": 480, "fps": 30}
      }' \
      --teleop.type=so101_leader --teleop.port=$TELEOP_PORT --teleop.id=$TELEOP_ID \
      --display_data=true \
      --dataset.repo_id=${HF_ORG}/${PART} \
      --dataset.root=$(pwd)/datasets/${PART} \
      --dataset.single_task="Pick up the vial and place it in the rack" \
      --dataset.num_episodes=10 \
      --dataset.episode_time_s=45 \
      --dataset.reset_time_s=20 \
      --dataset.push_to_hub=false \
      --play_sounds=false
    ```

    A preview window opens with both camera views. Confirm that the view labelled `ego` shows the gripper camera and `external_D455` shows the fixed camera. If they are swapped, see "If something goes wrong". The command records 10 episodes and then stops by itself. Change the `10` if your team planned a different number for this slot. Leave everything else as it is.
14. **Record the episodes.** For each episode:
    - Pick up one vial and place it in the rack. Move smoothly.
    - Press the **right arrow** key. The episode ends.
    - A 20-second reset period starts. Put the vials back in new positions and return the arm to its start pose. Press the right arrow again when ready, or wait for the time to run out. The next episode begins.

    If an attempt cannot be completed, press the **left arrow** key; the attempt is thrown away and recorded again. Keep going through a fumble you can recover from. An episode ends by itself after 45 seconds. To record more episodes into the same part after the command stops, run the same block again with one extra line, `--resume=true \`, and set `--dataset.num_episodes` to how many more you want.
15. **Finish.** The command stops after the last episode and spends a short while writing video files. Wait until the prompt returns in Terminal 1. To stop before the last episode, finish the episode you are in, then press **Esc** instead of the right arrow. Do not press Esc in the middle of an attempt; if you do, that unfinished attempt is saved as an episode, so write its number down for step 19.

Now continue with step 16.

## Steps 16 to 20: the end of every session

Do these in order before you leave. They take about ten minutes, so stop recording ten minutes before your slot ends.

16. **Look at a few episodes.** In Terminal 1, type:

    ```bash
    lerobot-dataset-viz --repo-id ${HF_ORG}/${PART} --root $(pwd)/datasets/${PART} --episode-index 0
    ```

    A viewer opens and plays episode 0 with both camera views and the joint positions. Change the number at the end to see other episodes; look at two or three. You are looking for a black or blocked camera view, swapped views, or an episode where the vial did not end up in the rack. Write down the numbers of any bad episodes. Close the viewer when done.
17. **Run the automatic check.** Open a **second terminal** on the station PC. Do not start the container in it. Type the two lines below, with your part's full name typed out in place of `t3_stB_sim_s02`:

    ```bash
    conda activate lerobot
    python ~/class_data.py check ~/Sim-to-Real-SO-101-Workshop/datasets/t3_stB_sim_s02
    ```

    The result is one line starting with `PASS` or `FAIL`, for example `PASS  t3_stB_sim_s02: 12 episodes, 3140 frames, median 8.6s, longest 14.2s`. For a simulated part, two notes about an `fps` key also appear; they are expected and are not a failure. If the line says `FAIL`, do not upload. Copy the whole output into a message to the TA and go on to step 19.
18. **Upload the part.** Back in Terminal 1, the container terminal, type:

    ```bash
    python -m sim_to_real_so101.scripts.lerobot_push_dataset \
        --repo-id ${HF_ORG}/${PART} --root $(pwd)/datasets/${PART} --private
    ```

    Wait until it finishes without an error. Keep `--private`; without it the part is visible to the whole internet.
19. **Write the session in the log.** Add one row to the session log: the part name, today's date, who drove and who typed, how many episodes were recorded, the numbers of any episodes to remove and why, and anything unusual, such as a camera that was bumped or a check that failed. The steward builds the class dataset from this log, so an unlogged part may be left out.
20. **Leave the station.** Type `exit` in Terminal 1 to stop the container, and close both terminals. Do the end-of-session list on the station card: light off, vials back on the right, rack on the left, any collision noted. Log out of the account, so the next team starts from the login screen.

Never upload the same part twice, and never change a part after uploading it. If you notice a problem later, write it in the log and tell the steward; the steward fixes parts on downloaded copies.

## When to stop collecting

The class dataset is built in three stages after the teams finish: the freeze, the dry run, and the big merge. Here is what each one means for your team.

### Your team's quota

Each team records **40 simulated and 40 real episodes**; 30 and 30 is the minimum. Check the instructor's course page in case these numbers have changed. Count only episodes that are uploaded and not marked for removal in the log. Spread the work over several sessions of ten to twenty episodes each; several short sessions give more variety and fewer tired mistakes than one long one.

### Stop when either of these happens

- **Your team has reached its quota.** Finish the session you are in, do steps 16 to 20, and record no more. Extra episodes beyond the quota are welcome only if the instructor asks for them.
- **The freeze time has passed.** The instructor announces a date and time on the course page. After it, record nothing, even if you still have a reserved slot and are below quota. A part uploaded after the freeze does not go into the first version of the class dataset.

Finishing early is fine. Finishing late is not, because the steward starts on the freeze time and cannot wait for stragglers.

### The dry run

Before merging everything, the steward takes one simulated part and one real part through the complete merge procedure, to catch problems while they are still cheap to fix. During the dry run:

- Your team does nothing at the stations. Leave your parts as they are.
- Watch the course page and your messages. If the dry run finds a problem with one of your parts, the steward tells you what it was. Record a replacement session only if the steward asks for one.
- You can use the time to review your own episodes in the viewer (step 16) and add any missed notes to the session log. Do not re-record.

### The big merge

After the dry run, the steward downloads every logged part, checks and repairs them, merges them into three datasets, `vials_sim_v1`, `vials_real_v1` and `vials_all_v1`, and publishes them to the course organization with a manifest that says which episode came from which team. The instructor announces when they are ready. From then on:

- Training uses the merged datasets, never your individual parts.
- Your parts stay on the Hub as a record; do not delete them.
- The stations are free again, but they are now for evaluation, not collection. Do not start new parts unless the instructor opens a second collection round.

### Am I done? A short check

- Every part my team recorded has a `PASS` from the checker, is uploaded, and has a row in the session log.
- The log shows my team at or above quota, or the freeze time has passed.
- Nothing is left in the `datasets` folder on a station that is not in the log.

## If something goes wrong

| What you see | What to do |
| --- | --- |
| Step 3 prints fewer than five values | Stop. Message the TA. Do not type values from memory. |
| The recording command stops at once with an error, such as a port or power problem | Fix the cause: check the power LED on the arm, check the USB cables, or redo step 12. Then delete the empty part folder with `rm -r datasets/$PART` in Terminal 1 and run the command again. Without the delete, the next try stops with `FileExistsError`. Only delete a part folder that holds no episodes you want to keep. |
| `FileExistsError` when starting a recording | The part folder already exists. If it is an empty leftover from a failed start, delete it as above. If it holds episodes from earlier in this session, add `--resume=true` to the real-robot command; the simulator command resumes on its own. |
| The simulator prints `[ERROR]: Failed to initialize dataset. folder already exists` and closes | The part folder is a leftover from a start that crashed before any episode was saved, so it is not a dataset the simulator can continue. Check with `ls datasets/$PART/data` in Terminal 1: if it prints nothing or says no such file, delete the folder with `rm -r datasets/$PART` and run step 6 again. If it lists files, episodes exist; keep the folder, write the problem in the session log, and tell the TA. |
| You press S, Terminal 1 shows `torch.OutOfMemoryError: CUDA out of memory`, and the simulator freezes | Not something you did: the station is missing a setup fix for its 16 GB graphics card. Press Ctrl+C in Terminal 1 (close the simulator window if it stays open), tell the TA, who has the fix in setup checklist step 5, and delete the empty part folder before the next try, as above. |
| Terminal 1 prints `Svt[warn]: Failed to set thread priority: Invalid argument` while an episode is being saved | Harmless; ignore it. The video encoder asks for a higher thread priority than the container allows and carries on at normal priority. The episode is saved. |
| The two camera views are swapped in the preview | Press **Esc**, delete the part folder as above (it holds one useless episode), swap the two values with `setenv CAMERA_GRIPPER=...` and `setenv CAMERA_EXTERNAL=...`, and start step 13 again. |
| Keys do nothing in the simulator | Click inside a viewport first, then press the key. |
| The simulator does not finish loading | The leader arm is probably not fully connected. Unplug and replug its power, then run step 6 again. |
| The simulator prints `Segmentation fault (core dumped)` within seconds of starting | Not something you can fix at the station: the PC's NVIDIA driver is not one the simulator accepts. Tell the TA, who has the fix in the setup checklist, and use the slot for a real session if the arms are free. |
| The simulator crashes while starting, with `Segmentation fault` and a stack trace naming `libomni.hydra.rtx.plugin.so` or `librtx` | Not something you did. The simulator's renderer is failing on the station's NVIDIA driver, which only the TA can change. Stop, note the time in the session log, and tell the TA. Do not retry more than once; each attempt leaves crash files behind. |
| The simulator stops with `FileNotFoundError: Unable to open the usd file at path: .../SO-ARM101-USD.usd` | Not something you did. The robot model was never fully downloaded onto the station (the file is a Git LFS placeholder). Tell the TA; the fix is one command on the host and takes a minute, and you can then start the simulator again. |
| A command asks whether to use the existing calibration or type `c` to recalibrate | Press **Enter**. Then tell the TA, because this message means the arm's ID or port may be wrong. |
| The calibration check does not say `PASS` | Do not record. Message the TA with the output. |
| The checker in step 17 says `FAIL` | Do not upload. Copy the whole output into a message to the TA, and write the part in the log with a note. |
| You pressed Esc in the middle of an attempt | The unfinished attempt was saved as an episode. Write its number in the log for removal. |
| One joint of the follower arm does not move | A motor cable may be loose. Stop recording, power the arm off, and tell the TA. |
| In step 4, `ls datasets/$PART` lists a folder you did not create | You have typed a part name that another session already used. All teams share this account and this disk, so recording now would mix your episodes into someone else's part. Look up your team's next session number in the session log and set the name again. |

## One-page reference

| Item | Value |
| --- | --- |
| Part name | `t<team>_st<station>_<sim or real>_s<session>`, for example `t3_stB_sim_s02`. Team 1 to 5, station A, B or C, two-digit session number. |
| Task sentence | `Pick up the vial and place it in the rack`. Already in the commands; never retype it. |
| Camera names | `ego` is the gripper camera, `external_D455` is the fixed camera. |
| Simulator seed | Team number × 100 + session number. |
| Simulator keys | **R** reset the scene, **S** start or stop recording, **C** cancel the attempt. Click a viewport first. |
| Real-robot keys | **right arrow** end the episode or the reset period, **left arrow** redo the attempt, **Esc** stop after this episode. |
| One episode | One vial into one empty slot, 3 to 45 seconds. |
| Terminal 1 | Inside the container. Steps 2 to 16 and 18. |
| Terminal 2 | On the station PC, outside the container. Step 17 only. |
| Where parts are saved | `~/Sim-to-Real-SO-101-Workshop/datasets/<part name>` on the station PC, then uploaded to the course organization on the Hub. |
| Quota | 40 simulated + 40 real episodes per team; minimum 30 + 30. |
| Who to ask | The TA for anything at the station; the steward for anything about an uploaded part. |
| Login | One account per station, shared by all teams. Your team is identified by the part name and the session log, not by the login. |
