@Claude, what do you mean "One part session, on the station disk" in the diagram?

# Vial-to-Rack Data Collection: Station Runbook and Merge Protocol

Oct 8, 2026 · Ziad Youssfi

This document explains how students record episodes for the vial-to-rack task, and how those recordings are combined into one class dataset. The main rule is simple: every episode, simulated or real, is recorded inside the workshop's Docker container. The separate LeRobot installation on the same PC is used afterwards, to check the recordings, combine them, and train policies.

## At a glance

&#91;embedded content: data path · container records, host checks, merges and trains\]

Simulated and real episodes are written by the same LeRobot 0.4.3 inside the container, which is what makes them mergeable. The host's LeRobot 0.6.1 never records.

### Words used in this document

- **Station**: one of the three workspaces. Each has a leader arm, a follower arm, two cameras and a PC.
- **Container**: the workshop's Docker image, named `teleop-docker`. It holds the simulator (Isaac Sim) and an older LeRobot, version 0.4.3. You start it from a terminal and then type commands inside it.
- **Host**: the station PC itself, outside the container. The current LeRobot, version 0.6.1, is installed here.
- **Part**: the dataset folder produced by one recording session. In one session, one team at one station records either simulated or real episodes, and the result is one part. Every part is named t\<team>\_st\<station>\_\<sim or real>\_s\<session>, for example t3\_stB\_sim\_s02: team 3, station B, simulated episodes, the team's second simulated session. The team is 1 to 5 (6 and 7 are spare for future teams), the station is A, B or C, and the session number always has two digits. Team 0 is reserved for the instructor's and the TA's test recordings: a t0 part passes the same checks as any other but is never merged into the class dataset.
- **Hub**: the Hugging Face website, where datasets are stored. The course has an organization there, and every part is uploaded to it.
- **Steward**: the one person, a TA or the instructor, who downloads all the parts and combines them into the class dataset.
- **Merge**: to combine several parts into one larger dataset.

## Why there are two environments

The workshop's simulator, Isaac Sim 5.1, runs only on Python 3.11. The current LeRobot runs only on Python 3.12 or newer. One Python installation cannot be both, so each station PC has two separate sets of software:

- **Inside the container:** the simulator, plus LeRobot 0.4.3, which still works on Python 3.11.
- **On the host:** LeRobot 0.6.1, which has all the policies the teams will train.

This is less of a problem than it sounds. Both LeRobot versions save episodes in the same file format, called LeRobotDataset v3.0. An episode recorded by the old version inside the container can be opened, merged and trained on by the new version on the host.

The container cannot be brought up to Python 3.12 by changing a version number. That would mean moving the workshop to Isaac Sim 6 and [Isaac Lab 3.0](https://github.com/isaac-sim/IsaacLab/releases), which is still a pre-release and would require rewriting parts of the workshop's simulation code.

## Eight things that can go wrong, and the rule that prevents each

The two LeRobot versions agree on the file format but disagree on some details. The workshop's own commands are also not fully consistent between simulated and real recording. Testing turned up the eight problems below. Students follow the first five rules while recording. The steward or the instructor takes care of the last three.

### Rules for students

**1. Record real episodes inside the container, never with the host's LeRobot.** The two versions write joint positions in different units. LeRobot 0.4.3 in the container writes each joint as a number from −100 to 100, and the gripper from 0 to 100. LeRobot 0.6.1 on the host writes degrees unless told otherwise. If real episodes were recorded on the host, their numbers would mean something different from the numbers in the simulated episodes, and a policy trained on both would be learning from two incompatible scales. LeRobot does refuse to merge such parts, because the two versions also label the robot differently: `so101_follower` in the container and `so_follower` on the host. Students never type this label. The recording software writes it by itself, from its own version, and the \`--robot.type=so101\_follower\` option is the same in both versions. The arm's ID, such as \`orange\_robot\`, is not stored in the dataset and has no effect on merging. So the whole rule is: run the recording command inside the container, as the real-episode section shows. The checker rejects any part whose label is \`so\_follower\`.

**2. Name the real cameras `ego` and `external_D455`.** A dataset stores each camera's video under a name. The simulator always uses `ego` for the gripper camera and `external_D455` for the fixed camera. The workshop's real-robot command uses `wrist` and `front` for the same two views. LeRobot merges datasets only when their camera names match exactly, so the real recordings must use the simulator's names. `external_D455` refers to the camera model NVIDIA used. It is only a label, and your camera can be a different model.

**3. Copy and paste the task sentence; do not retype it.** Every episode stores a short instruction in words: "Pick up the vial and place it in the rack". Policies that read language use this sentence as an input. LeRobot treats two sentences as the same task only if they match character for character. The workshop's simulator command ends "in the rack" and its real-robot command ends "in the yellow rack", so following the workshop exactly produces a dataset with two tasks. A typing mistake or a missing capital letter has the same effect. The recording commands in this document already contain the sentence. Copy the whole command and leave the sentence unchanged.

**4. When recording real episodes, tell LeRobot where to save.** Unless told otherwise, the real-robot recording command saves into a folder that exists only inside the container. The container is deleted every time it exits, and the recording is deleted with it. The option `--dataset.root=$(pwd)/datasets/$PART` saves into the `datasets` folder instead. The container shares that folder with the station PC, so the files remain after the container exits. The real-robot recording command in this document already includes this option.

**5. Upload with the long form of the upload command.** The workshop provides a short command, `lerobot_push_dataset`, for uploading a part to the Hub. In the current workshop code that short command stops with an `ImportError` and uploads nothing. The same program works when it is started as `python -m sim_to_real_so101.scripts.lerobot_push_dataset`.

### Handled by the steward or the instructor

**6. Simulated parts need a small repair before they can be merged with real parts.** The simulator's recorder writes one extra line, `"fps": 30`, into the description of the joint data. The real-robot recorder does not write that line. LeRobot compares these descriptions before merging and refuses if they differ, with the message "Same features is expected". The command `python class_data.py fix` removes the extra line. The recorded data itself does not change.

**7. A merged dataset needs the same repair command once more.** The simulator's recorder saves a small index file for every episode. When LeRobot merges parts, it combines those files into one, but it leaves each episode's entry pointing to its old file. Training still works. Later operations, such as removing an episode, splitting the dataset or merging again, fail with `FileNotFoundError`. Running `python class_data.py fix` on the merged dataset corrects the entries.

**8. On the host, point LeRobot to the container's calibration files.** Each arm's calibration is saved in a file. The container keeps those files in folders named `so101_follower` and `so101_leader`. LeRobot 0.6.1 looks in folders named `so_follower` and `so_leader`, does not find the files, and offers to calibrate again. Never accept that offer. This matters only later, when a trained policy is run on the real arm from the host. The section "After the merge" gives the options to add.

## One-time setup at each station

The instructor or a TA does this once on each of the three station PCs, logged in as the station's one shared account; every team uses that same account, and teams are told apart by part names and the session log, not by logins. Everything below is installed in that account's home folder, so do it in that account and no other, and add the account to the \`docker\` group so that starting the container asks for no password. Students do not repeat any of it. There are six steps, and each step's commands are shown directly under it.

### Step 1: Build the workshop container

This is the workshop page *Get the Code and Models*. In a terminal on the station PC, type:

```bash
cd ~
git clone https://github.com/isaac-sim/Sim-to-Real-SO-101-Workshop.git
cd Sim-to-Real-SO-101-Workshop
docker build -t teleop-docker -f docker/sim/Dockerfile .
```

This builds the container image named `teleop-docker`. It is the only image needed for recording. The workshop's second image, `real-robot`, runs NVIDIA's GR00T model and is not needed to collect data.

### Step 2: Install the current LeRobot on the station PC

In a terminal on the station PC, not inside the container, type:

```bash
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
conda create -y -n lerobot python=3.12
conda activate lerobot
conda install -y ffmpeg -c conda-forge
pip install 'lerobot[core_scripts,training,feetech]==0.6.1'
python -c "import lerobot, torch; print(lerobot.__version__, torch.__version__, torch.cuda.get_device_name(0))"
```

The first two lines install conda, a tool that keeps separate Python installations apart. The next lines create an installation named `lerobot` and put LeRobot 0.6.1 into it. The last line is a test: it should print `0.6.1`, the PyTorch version, and the name of the graphics card. Install exactly version 0.6.1 on all three stations and on the computer used for training, so that everyone's tools behave the same way.

One thing to check on the RTX 5080. In a test install on 2026-10-08, the `pip` command chose a PyTorch build made for CUDA 13.0. LeRobot's installation page says that build needs NVIDIA driver version 580 or newer. Type `nvidia-smi` to see the station's driver version. If it is older than 580, the installation page's section *PyTorch CUDA variant* explains how to install the CUDA 12.8 build, which works with driver 570.86 or newer.

### Step 3: Allow the container to upload to the Hub

Uploading needs a Hugging Face access token, which works like a password. On the Hugging Face website, under Settings and then Access Tokens, create a token that is allowed to write to the course organization. Then do two things on the station PC.

First, add this line to the end of the file `~/.bashrc`, with the real token in place of the placeholder:

```bash
export HF_TOKEN=hf_xxxxxxxxxxxxxxxx
```

Second, create a file named `~/run_teleop.sh`. Copy into it the whole block from the workshop's *Quick Reference* page that starts with `cd ~/Sim-to-Real-SO-101-Workshop`, then `xhost +`, then the long `docker run --name teleop` command. Add one new line directly below the line `-e DISPLAY \`:

```bash
   -e HF_TOKEN \
```

The new line passes the token into the container each time it starts. Without it, someone would have to log in to Hugging Face inside the container at every session, because the container forgets the login when it exits. From now on, everyone starts the container the same way, by opening a new terminal and typing `bash ~/run_teleop.sh`.

### Step 4: Save the station's settings

Start the container with `bash ~/run_teleop.sh`. Inside it, find out which USB port each arm is on and which number each camera has. The workshop provides two helper commands for this, `lerobot-find-port` and `lerobot-find-cameras opencv`; its pages *Calibrating the SO-101* and *Operating the SO-101* walk through them. Then save the answers:

```bash
setenv TELEOP_PORT=/dev/ttyACM1     # the leader arm's port
setenv ROBOT_PORT=/dev/ttyACM0      # the follower arm's port
setenv CAMERA_GRIPPER=0             # the gripper camera's number
setenv CAMERA_EXTERNAL=2            # the fixed camera's number
setenv HF_ORG=your-course-org       # the course organization's name on the Hub
```

The values shown are examples; use the ones the helper commands report. `setenv` is a helper the workshop provides. It stores each value in a file on the station PC, so the values are still there the next time the container starts.

Two more settings, `TELEOP_ID` and `ROBOT_ID`, are the names under which each arm's calibration is saved. The workshop sets them during calibration. Leave them as they are.

### Step 5: Calibrate both arms once

Follow the workshop page *Calibrating the SO-101* for the leader arm and for the follower arm. When it asks you to move each joint through its range, move the joint until it physically stops, in both directions. Then run the workshop's check, inside the container:

```bash
python docker/real/scripts/so101_check_calibration.py
```

The last line it prints must read `Overall: ✓ PASS — calibration looks good.` If it does not, calibrate again. Finally, copy the folder `~/.cache/huggingface/lerobot/calibration` from the station PC into the course repository as a backup. The next section explains why this step matters so much when three stations share one dataset.

### Step 6: Copy the checker

Copy the file `class_data.py` into the home folder of the station PC. Students run it at the end of every session.

### Booking the stations

Recording simulated episodes and recording real episodes both use the station's leader arm and its PC. A station can therefore do only one of the two at a time. With five teams and three stations, give each team booked time slots, and label each slot as a simulated session or a real session.

## Calibration, and why it matters for a shared dataset

### What calibration does

Each joint of the arm has a motor with a sensor that reports the joint's position as a raw number. The unit is called an encoder count, and one count is about 0.09 degrees. Raw numbers cannot be compared between two arms, because each motor is mounted a little differently.

Calibration solves this. During calibration you move each joint from one physical end stop to the other, and LeRobot writes down the raw number at each end. From then on, LeRobot reports the joint's position as a place between those two ends: −100 means the joint is at one stop, +100 means it is at the other stop, and 0 means exactly halfway. These are the numbers saved in every episode, both for where the arm is and for where it is told to go.

The physical stops are in the same place on every SO-101, because the arms are built from the same parts. So if every arm is calibrated all the way to its stops, the number 0 means the same joint angle on every arm. This is what allows data from three stations to be mixed.

The wrist-roll joint is a partial exception. It can turn almost a full circle, so where its zero lands depends mostly on how carefully the wrist is centred at the start of calibration. Line up the two black dots on the gripper, as the workshop shows.

### What goes wrong when one station is calibrated short

Here is an example with made-up round numbers. Suppose the elbow can physically travel 2,200 counts between its two stops. At Station A, the person calibrating moved the elbow the whole way. At Station B, a cable snagged and the elbow stopped 200 counts early at one end, so LeRobot recorded a range of only 2,000 counts.

|  | Station A | Station B |
| --- | --- | --- |
| Range recorded at calibration | 2,200 counts, the full travel | 2,000 counts, 200 short at one end |
| The elbow is held exactly halfway between its stops. Number saved in the data: | 0 | +10 |
| The arm is told to go to 0. Where the elbow goes: | Halfway | About 9 degrees away from halfway |

The same physical pose is written into the data as two different numbers, and the same number moves the two arms to two different poses. That is what the earlier version of this document meant by "offset". Nine degrees at the elbow moves the gripper by a few centimetres, which is enough to miss a vial.

If the merged dataset contains episodes from both stations, the policy sees pictures of the same pose labelled with different numbers. It learns something in between, and it becomes less accurate at every station.

### Can a policy be trained on data from several SO-101 arms?

Yes. Every arm always has its own calibration file, and the raw numbers in those files are different for every arm. That is normal and is not a problem. What must be the same is the method: every arm is calibrated all the way to its physical stops. The saved numbers then mean the same angles on every arm, apart from small differences that come from assembly. Judging by the spread in NVIDIA's reference calibrations, those differences are a few degrees at most.

Policies that use camera images cope with small differences of that size, because they keep correcting from what they see. Pooling data from many arms is common practice. For example, the [SmolVLA](https://huggingface.co/blog/smolvla) model was first trained on 487 datasets that members of the community recorded on their own SO-100 arms.

What a policy cannot absorb is a large disagreement like the Station B example. The workshop's calibration check exists to catch exactly that. It compares the size of each joint's recorded range with 15 reference calibrations supplied by NVIDIA, and it warns when a joint is far from them. Station B's elbow in the example would be flagged.

### Can the trained policy run on any of the three stations?

Yes, under the same condition. This is what the workshop itself does: NVIDIA's ready-made policies were trained on data from NVIDIA's arms, and the workshop has you run them on your own arm. Three things make it work in your lab:

- Each station's calibration passes the workshop's check.
- The cameras are mounted in the same positions at every station. A camera that points somewhere slightly different changes what the policy sees, and that harms it as much as a calibration error does.
- The class dataset contains episodes from all three stations, which your plan already ensures. The policy has then seen each station's small differences during training.

Expect the success rate to differ somewhat from station to station. When you evaluate a policy, write down which station each trial was run on.

### A short test of whether two stations agree

You can test this directly before the teams collect data. Record one real episode at Station A. Copy its part folder into the `datasets` folder at Station B. Then, at Station B, inside the container, replay it:

```bash
lerobot-replay \
  --robot.type=so101_follower --robot.port=$ROBOT_PORT --robot.id=$ROBOT_ID \
  --dataset.repo_id=${HF_ORG}/t1_stA_real_s01 \
  --dataset.root=$(pwd)/datasets/t1_stA_real_s01 \
  --dataset.episode=0
```

Station B's arm repeats the movements that were recorded at Station A. Keep hands clear while it moves. If the gripper travels to the same places, for example if it ends above the same rack slot, the two calibrations agree. If it is consistently off to one side, recalibrate the station whose check does not pass. Repeat with Station C. This command was checked for correct spelling of its options, but it has not been run on a real arm.

### The rules that follow from this

- Calibrate each station once, with care. Do not calibrate again unless the arm was taken apart or the check fails.
- Sometimes a command asks whether to use the existing calibration or to run a new one. Press Enter to keep the existing one. A student who is unsure stops and asks the TA.
- If a station is recalibrated while the teams are still collecting, write the date in the session log, so that parts recorded before and after can be compared.

## Every session: recording simulated episodes

A simulated session uses the leader arm and the PC. The follower arm and the real cameras are not used. The student moves the leader arm, and a simulated follower arm on the screen copies it. These steps follow the workshop page *Sim-to-Real Strategy 1: Domain Randomization*, with three small additions that are explained under Step 2.

### Step 1: Start the container

Open a terminal on the station PC and type `bash ~/run_teleop.sh`. You are now inside the container, and everything you type in this terminal runs there. Check that the station's settings are loaded:

```bash
echo $TELEOP_PORT $TELEOP_ID $HF_ORG
```

This should print three values, for example `/dev/ttyACM1 orange_teleop your-course-org`. If one is missing, ask the TA.

### Step 2: Name the session and start the simulator

```bash
export PART=t3_stB_sim_s02
lerobot_agent --task Lerobot-So101-Teleop-Vials-To-Rack-DR \
    --repo_id ${HF_ORG}/${PART} \
    --repo_root $(pwd)/datasets/${PART} \
    --task_name "Pick up the vial and place it in the rack" \
    --seed 302
```

The first line gives this session's part its name. The name has four pieces: `t3` is team 3, `stB` is station B, `sim` means simulated, and `s02` means this is your team's second simulated session. Change them to match your own session.

The second command starts the simulator and the recorder. It differs from the workshop's version in three ways:

- `--repo_id` and `--repo_root` use the part name, so the recording is saved in the folder `datasets/t3_stB_sim_s02`.
- `--task_name` holds the class's task sentence. Leave it exactly as written.
- `--seed` is a number that controls the random changes to the scene, such as the lighting, the vial positions and the camera position. Use your team number times 100, plus your session number: team 3, session 2 gives 302. If every team used the same seed, every session would begin with the same sequence of scenes, and the class dataset would have less variety.

The simulator takes about two minutes to open the first time.

### Step 3: Arrange the two camera views

In the simulator window, open the menu Window, then Viewports, and switch on Viewport 1 and Viewport 2. In one viewport choose the camera `gripper_cam`. In the other choose `Camera_OmniVision_9782_Color`. In each viewport's settings, change the aspect ratio from 16:9 to 4:3.

These are the two views the policy will see. While recording, look only at these two views and not at the arm itself or the general 3D view. You then solve the task with the same information the policy will have.

### Step 4: Record the episodes

Click inside a viewport first, so that the simulator receives your key presses. Then, for each episode:

1. Press **R**. The scene resets with new random lighting and positions.
2. Press **S** to start recording.
3. Pick up one vial and place it into one empty slot of the rack.
4. Press **S** again to stop. The episode is saved in the background while you carry on.

If an attempt goes wrong, press **C** instead of S. The attempt is thrown away.

### Step 5: Stop cleanly

When you have recorded enough episodes, look at the terminal and wait for the message `No more episodes in queue`. It means every episode has been written to disk. Then press Ctrl+C in the terminal to close the simulator.

If the simulator closes or crashes before you are finished, run the two commands of Step 2 again with the same part name. The recorder opens the existing folder and adds the new episodes to it.

## Every session: recording real episodes

A real session uses both arms and both cameras. The student moves the leader arm, and the follower arm copies it. The recording command is the workshop's `lerobot-record` command from its page *Sim-to-Real Strategy 2: Co-Training With Real Data*, with four changes that are explained under Step 3.

### Step 1: Start the container and check the station

Open a terminal on the station PC and type `bash ~/run_teleop.sh`. Go through the pre-flight list on the station card. Then run the calibration check:

```bash
python docker/real/scripts/so101_check_calibration.py
```

The last line it prints must begin with `Overall: ✓ PASS`. If it does not, stop and tell the TA. Do not record.

### Step 2: Check the ports and cameras, but only if a cable was moved

USB port names and camera numbers can change when a cable is unplugged and plugged back in. If anyone has moved a USB cable since the last session, run `lerobot-find-port` and `lerobot-find-cameras opencv`, and update the settings with `setenv`, as in Step 4 of the one-time setup. If nothing was moved, skip this step.

### Step 3: Name the session and start recording

Recording of the first episode begins as soon as the command has started. Place the vials and put the arm in its start pose before you run it.

```bash
export PART=t3_stB_real_s02
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

The first line names the part in the same way as for a simulated session, but with `real` in the name. The recording command differs from the workshop's version in four ways:

- The cameras are named `ego` for the gripper camera and `external_D455` for the fixed camera, to match the simulator.
- `--dataset.single_task` holds the class's task sentence. Leave it exactly as written.
- `--dataset.root` saves the recording in the shared `datasets` folder, so it is still on the station PC after the container exits.
- `--dataset.push_to_hub=false` stops LeRobot from uploading automatically, so that you can check the part before it is uploaded.

You may change three of the options. `--dataset.num_episodes=10` is how many episodes this run records. `--dataset.episode_time_s=45` ends an episode after 45 seconds if you have not ended it yourself. `--dataset.reset_time_s=20` gives you 20 seconds between episodes to put the vials back.

A preview window opens and shows both camera views. Confirm that the view labelled `ego` comes from the gripper camera and the view labelled `external_D455` comes from the fixed camera.

### Step 4: Record the episodes

For each episode:

1. Pick up one vial and place it in the rack.
2. Press the **right arrow** key when you are done. This ends the episode.
3. A reset period follows. Put the vials back and return the arm to its start pose. Press the right arrow again when you are ready, or wait for the reset time to run out. The next episode then begins.

If an attempt goes wrong, press the **left arrow** key. The attempt is thrown away and you record it again.

To end the session before all the episodes are recorded, finish the current episode and press **Esc** instead of the right arrow. Esc saves whatever has been recorded of the current episode and then stops. If you press Esc in the middle of an attempt, the unfinished attempt is saved as an episode, so note its number in the session log for removal.

### If something goes wrong

**The command stops straight away with an error,** for example because the arm has no power or the port name is wrong. By then it has already created the folder `datasets/$PART`, with only a folder named `meta` inside. Fix the problem, then delete that part folder by typing `rm -r datasets/$PART`, and run the command again. If you do not delete it, the next attempt stops with `FileExistsError`. Only ever delete a part folder that holds no episodes you want to keep.

**The two camera views are swapped.** Press Esc. The part now holds one useless episode and nothing else, so delete the part folder as above. Exchange the values of `CAMERA_GRIPPER` and `CAMERA_EXTERNAL` with `setenv`, and start again.

**You want to add more episodes to the same part later in the session.** Run the same command again with one more option, `--resume=true`. The option `--dataset.num_episodes` then means how many more episodes to record.

## End of every session: look, check, upload, log

Before leaving the station, do four things in this order: look at what you recorded, run the automatic check, upload the part, and write the session in the log. Each step has one command, shown directly under it.

Pay attention to where each command is typed. Steps 1 and 3 are typed inside the container, in the terminal you recorded in. Step 2 is typed in a second terminal on the station PC, outside the container.

### Step 1: Look at a few episodes (inside the container)

```bash
lerobot-dataset-viz --repo-id ${HF_ORG}/${PART} --root $(pwd)/datasets/${PART} --episode-index 0
```

A viewer opens and plays episode 0, with both camera views and the joint positions. Change the number at the end to look at other episodes. You are looking for obvious problems: a black or blocked camera view, the two views swapped, or an episode in which the vial did not end up in the rack. Write down the numbers of any bad episodes for Step 4.

### Step 2: Run the automatic check (second terminal, outside the container)

Open a new terminal on the station PC. Do not start the container in it. Type the two lines below, with your own part name in place of `t3_stB_sim_s02`:

```bash
conda activate lerobot
python ~/class_data.py check ~/Sim-to-Real-SO-101-Workshop/datasets/t3_stB_sim_s02
```

The first line switches this terminal to the LeRobot 0.6.1 installation. The second line runs the checker on your part. The checker reads the part and compares it with the class's agreed settings: the camera names, the task sentence, the recording rate, the joint units, the episode lengths and the folder name. It prints one line that begins with `PASS` or `FAIL`, like this:

```
PASS  t3_stB_sim_s02: 12 episodes, 3140 frames, median 8.6s, longest 14.2s
```

Under a `FAIL` it lists what is wrong in plain words. Do not upload a part that fails; show the message to the TA.

For a simulated part, two extra notes appear that mention an `fps` key. They are expected and do not mean the part failed. The steward removes that key later.

### Step 3: Upload the part (inside the container)

Go back to the first terminal, the one inside the container, and type:

```bash
python -m sim_to_real_so101.scripts.lerobot_push_dataset \
    --repo-id ${HF_ORG}/${PART} --root $(pwd)/datasets/${PART} --private
```

This uploads the part to the course organization on the Hub, under the same name. The word `--private` makes the upload visible only to members of the course organization. Keep it. Without it, anyone on the internet can see the part.

### Step 4: Write the session in the log

Add one row to the class's shared session log; a shared spreadsheet is enough. Write down the part name, the date, who operated the arm, how many episodes were recorded, the numbers of any episodes that should be removed and why, and anything unusual, such as a camera that was bumped. The steward uses this log to know which parts exist and which episodes to remove.

There is one log for the whole class, not one per station: teams move between stations, the steward builds `parts.txt` from it, and a team finds its next session number by filtering one sheet. Use these columns, one row per session:

| Column | What to write |
| --- | --- |
| Part | The part name, exactly as typed in step 4, e.g. `t3_stB_sim_s02` |
| Date | YYYY-MM-DD |
| Team | 1 to 5; 0 for setup tests |
| Station | A, B or C |
| Type | `sim` or `real` |
| Session | The two-digit session number from the part name |
| Driver | Who moved the leader arm |
| Typist | Who ran the commands |
| Episodes | How many episodes the checker reported |
| Remove | Episode numbers to drop, counted from 0 as the viewer shows them, e.g. `4, 7`; blank if none |
| Why | One short reason per removed episode |
| Checker | `PASS` or `FAIL` |
| Uploaded | `yes` or `no` |
| Notes | Anything unusual: a bumped camera, a crash, a recalibration, a station problem |
| Steward | Left blank by teams; the steward writes `downloaded`, `cleaned`, `merged` or `rejected` |

Team, Station, Type and Session repeat what the part name says; they are there so the sheet can be sorted and filtered without reading names.

### Two rules about parts

- Each part belongs to one team's one session. Never record into a part that another team started.
- Once a part is uploaded, do not change it. If something needs fixing, tell the steward. The steward makes all repairs on downloaded copies.

## The agreed settings for every episode

Every part must have the settings in this table. If two parts differ in any of them, they either cannot be merged or they merge into a dataset that misleads the policy. The checker tests all of these automatically except three: the simulator seed, whether an episode holds exactly one vial placement, and where the part was uploaded.

| Setting | Value |
| --- | --- |
| Recording software | The workshop container, `teleop-docker`, for simulated and real episodes alike |
| File format | LeRobotDataset version 3.0 |
| Recording rate | 30 frames per second |
| Robot label stored in the data | `so101_follower` |
| Camera names | `ego` for the gripper camera, `external_D455` for the fixed camera |
| Image size | 640 × 480 pixels |
| Joint values | Six numbers per frame, in this order: shoulder pan, shoulder lift, elbow flex, wrist flex, wrist roll, gripper. Each runs from −100 to 100, except the gripper, which runs from 0 to 100. |
| Task sentence | `Pick up the vial and place it in the rack` |
| Simulator scene | `Lerobot-So101-Teleop-Vials-To-Rack-DR`, the version with random variation |
| Simulator seed | Team number × 100 + session number |
| One episode | One vial placed into one slot, lasting between 3 and 45 seconds |
| Part name | Team, station, `sim` or `real`, and session number, in the form t\<team>\_st\<station>\_\<sim or real>\_s\<session>, for example `t3_stB_sim_s02` |
| Where parts are uploaded | The course organization on the Hub, as private datasets |

These values are also written at the top of the file `class_data.py`. If the class has already agreed on a different task sentence, change it in three places: the line that starts with `TASK` in `class_data.py`, the simulated recording command, and the real recording command.

The scene layout, the arm's start and end poses, and each team's quota are on the station card and are not repeated here.

## Steward: building the class dataset

One person combines all the parts. This person needs a computer with LeRobot 0.6.1 installed, as in Step 2 of the one-time setup, plus the file `class_data.py` and the session log. The work produces three datasets and one table:

- `vials_sim_v1` holds all the simulated episodes.
- `vials_real_v1` holds all the real episodes.
- `vials_all_v1` holds both.
- The manifest is a table with one row per episode. It says which team, station and session each episode came from, and whether it is simulated or real. LeRobot does not store this information inside the dataset, so the manifest is the only record of it. You need it later to study how much the simulated data helps.

### Step 1: Prepare a working folder

```bash
conda activate lerobot
export HF_ORG=your-course-org
mkdir -p ~/vials && cd ~/vials
```

Copy `class_data.py` into the new folder `~/vials`. Create a text file there named `parts.txt` that lists the names of all the parts in the session log, one name per line.

### Step 2: Download all the parts

```bash
for p in $(cat parts.txt); do
  hf download $HF_ORG/$p --repo-type dataset --local-dir parts/$p
done
```

Each part is downloaded into its own folder inside a folder named `parts`.

### Step 3: Check every part

```bash
python class_data.py check parts/*
```

This is the same check the students ran, now on all parts at once. Every part should print `PASS`. Step 5 explains what to do about a `FAIL`.

### Step 4: Repair the simulated parts

```bash
python class_data.py fix parts/*_sim_*
```

This removes the extra `fps` line from every simulated part, which is problem 6 in the list of eight. It prints one line per part saying what it changed.

### Step 5: Make any other repairs

Most sessions need nothing here. There are two repairs you may need.

If a part was recorded with the wrong task sentence, this command rewrites the sentence in that part. Put the part's name in both places where `t2_stB_real_s01` appears:

```bash
lerobot-edit-dataset --operation.type modify_tasks \
    --repo_id $HF_ORG/t2_stB_real_s01 --root parts/t2_stB_real_s01 \
    --operation.new_task "Pick up the vial and place it in the rack"
```

If the session log lists episodes to remove from a part, use the next block. The numbers in `[4, 7]` are the episode numbers to remove, counted from 0 as the viewer shows them.

```bash
mkdir -p rejected
lerobot-edit-dataset --operation.type delete_episodes --operation.episode_indices "[4, 7]" \
    --repo_id $HF_ORG/t3_stB_real_s02 --root parts/t3_stB_real_s02 \
    --new_repo_id $HF_ORG/t3_stB_real_s02 --new_root clean/t3_stB_real_s02
mv parts/t3_stB_real_s02 rejected/ && mv clean/t3_stB_real_s02 parts/
```

LeRobot writes a cleaned copy of the part into a folder named `clean`. The last line moves the original into a folder named `rejected` and puts the cleaned copy in its place.

After any repair, run the check from Step 3 again.

Three kinds of failure cannot be repaired with these commands. A part whose robot label is `so_follower` was recorded on the host, in degrees, and must be recorded again. A part from a station that fails the calibration check must also be recorded again, after the station is recalibrated. A part with different camera names could be rescued, but only with a custom script that does not exist yet.

### Step 6: Merge

The block below first defines a small helper named `merge`, so that you do not have to type every part name by hand. Paste the whole block into the terminal.

```bash
merge () {
  local out=$1; shift
  local ids=$(printf "'$HF_ORG/%s'," $(basename -a "$@")) roots=$(printf "'%s'," "$@")
  lerobot-edit-dataset --operation.type merge \
    --new_repo_id $HF_ORG/$out --new_root merged/$out \
    --operation.repo_ids "[${ids%,}]" --operation.roots "[${roots%,}]"
  python class_data.py fix merged/$out
}
merge vials_sim_v1  $(ls -d parts/t[1-7]_*_sim_*  | sort)
merge vials_real_v1 $(ls -d parts/t[1-7]_*_real_* | sort)
merge vials_all_v1  merged/vials_sim_v1 merged/vials_real_v1
```

The `t[1-7]` in the two `ls` lines leaves out team 0, the instructor's and TA's test parts, in case any were downloaded. `class_data.py manifest` refuses a t0 part as well, so a test part cannot slip into the class dataset unnoticed.

The helper takes a name for the new dataset and a list of folders. It asks LeRobot to merge those folders into one dataset inside a folder named `merged`, and then runs the repair command on the result, which is problem 7 in the list of eight.

The last three lines use the helper three times. The first merges all the simulated parts, the second merges all the real parts, and the third merges those two results into the complete dataset. Parts are merged in alphabetical order of their names.

### Step 7: Write the manifest

```bash
python class_data.py manifest merged/vials_all_v1_manifest.csv \
    $(ls -d parts/t[1-7]_*_sim_* | sort) $(ls -d parts/t[1-7]_*_real_* | sort)
```

This writes the table described at the start of this section. The file `merged/vials_all_v1_manifest.csv` opens in any spreadsheet program. The episode numbers in it match the episode numbers in `vials_all_v1`, because this command lists the parts in the same order as the merge did. The command also prints how many simulated and real episodes each team contributed.

### Step 8: Upload the class datasets

```bash
for d in vials_sim_v1 vials_real_v1 vials_all_v1; do
  python -c "from lerobot.datasets import LeRobotDataset; LeRobotDataset('$HF_ORG/$d', root='merged/$d').push_to_hub(private=True)"
done
```

This uploads the three datasets to the course organization as private datasets. This step was not tested, because the test computer had no access to the Hub.

### Later: smaller datasets for the co-training study

LeRobot can cut a smaller dataset out of `vials_all_v1`, for example all the simulated episodes plus ten real ones. Use the manifest to choose the episode numbers. The command is `lerobot-edit-dataset --operation.type split`, and LeRobot's page *Using the Dataset Tools* shows its options.

## After the merge

### Training

From here on, the class dataset is an ordinary LeRobot dataset, and the workshop container is no longer involved. On the training computer, with LeRobot 0.6.1 installed:

```bash
lerobot-train \
  --dataset.repo_id=$HF_ORG/vials_all_v1 \
  --policy.type=act \
  --output_dir=outputs/train/act_vials_all_v1 \
  --job_name=act_vials_all_v1 \
  --policy.device=cuda \
  --policy.repo_id=$HF_ORG/act_vials_all_v1
```

This trains an ACT policy on the complete dataset, downloading it from the Hub. To train from the copy on the steward's computer instead, add the option `--dataset.root=merged/vials_all_v1`.

### Running a trained policy on the real arm

The policy learned joint values on the −100 to 100 scale, because that is what the container recorded. LeRobot 0.6.1 on the host assumes degrees unless told otherwise. Every LeRobot 0.6.1 command that moves a real arm therefore needs these two extra options:

```bash
  --robot.use_degrees=false \
  --robot.calibration_dir=$HOME/.cache/huggingface/lerobot/calibration/robots/so101_follower \
```

The first option makes LeRobot 0.6.1 use the −100 to 100 scale. Without it, the policy's numbers would be read as degrees and the arm would move to the wrong positions. The second option tells LeRobot 0.6.1 where the container saved the arm's calibration, which is problem 8 in the list of eight. The cameras must also be named `ego` and `external_D455` in the command, as they were during recording.

Neither option has been tried on a real arm. Try them first with plain teleoperation, where a person is in control, before letting a policy drive. The command `lerobot-teleoperate` accepts the same two options, and for the leader arm it needs `--teleop.use_degrees=false` and `--teleop.calibration_dir=$HOME/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader`.

### Evaluating a trained policy in the simulator

This part is not solved yet. There are two obstacles. The workshop's evaluation command, `lerobot_eval`, can only talk to NVIDIA's GR00T policy server. And the container's LeRobot 0.4.3 cannot open a policy trained by LeRobot 0.6.1 as it is: in a test, an ACT policy loaded only after one setting, `pretrained_revision`, was removed from its configuration file.

The likely solution is to run the policy on the host and let the simulator in the container send it camera images and receive actions over a network connection. The workshop already runs GR00T this way. That connection would have to be written and tested.

## What was tested, and what was not

The path from recording to training was tested on 2026-10-08, in software only. The test computer had no robot, no camera, no graphics card, no Isaac Sim and no access to the Hub.

**What was tested.** Small test parts were made with LeRobot 0.4.3, at the exact version the container uses, by running the same sequence of operations as the workshop's simulator recorder and as its real-robot recording command. The real-robot recording command in this document was started and ran correctly up to the point where it tries to open the arm's USB port. With LeRobot 0.6.1, each of the eight problems was reproduced, the steward's commands were run as printed here, and the merged dataset was opened, its video was read, it was split, and an ACT policy was trained on it for two steps.

**What was not tested.** The simulator itself, the arms and cameras, the installation on an RTX 5080, uploading and downloading, and running a policy.

Before the whole class depends on this document, take one simulated part and one real part from one station through all of the steward's steps.

## Sources

- NVIDIA workshop: [Get the Code and Models](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/06-get-the-code.html), [Calibrating the SO-101](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/07-calibrating-so101.html), [Strategy 1: Domain Randomization](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/09-strategy1-dr-teleop.html), [Strategy 2: Co-Training With Real Data](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/13-strategy2-cotraining.html), [Sim Evaluation](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/11-sim-evaluation.html), [Quick Reference](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/quick_reference.html), [Troubleshooting Guide](https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/troubleshooting.html)
- [Workshop code](https://github.com/isaac-sim/Sim-to-Real-SO-101-Workshop): `docker/sim/Dockerfile`, `utils/lerobot_recorder.py`, `utils/lerobot_interface.py`, `scripts/lerobot_agent.py`, `scripts/lerobot_push_dataset.py`, `scripts/lerobot_eval.py`
- LeRobot documentation: [Installation](https://huggingface.co/docs/lerobot/installation), [Imitation Learning for Robots](https://huggingface.co/docs/lerobot/il_robots), [Using the Dataset Tools](https://huggingface.co/docs/lerobot/using_dataset_tools), [Backward compatibility](https://huggingface.co/docs/lerobot/backwardcomp)
- [LeRobot source](https://github.com/huggingface/lerobot), tag `v0.6.1` and commit `e670ac5`: SO-101 configuration, `datasets/aggregate.py`, `scripts/lerobot_record.py`
- Workshop datasets on the Hub: [simulated](https://huggingface.co/datasets/sreetz-nv/so101_teleop_vials_rack_left), [real](https://huggingface.co/datasets/sreetz-nv/so101_teleop_vials_rack_left_real_50), [simulated plus real](https://huggingface.co/datasets/sreetz-nv/so101_teleop_vials_rack_left_sim_and_real)
