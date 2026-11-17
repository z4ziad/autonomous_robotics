# Training and Deploying a Policy on the Vial-to-Rack Dataset

Nov 6, 2026 

This guide gives instructions to train basic policies on the merged dataset from the class. It is already on the Hugging Face organization. These instructions cover training an ACT, Diffusion, or SmolVLA policy with LeRobot 0.6.1. You can then deploy the trained policy on one of the lab stations’ SO-101 follower arms. Every command is complete, so you don’t have to look stuff up!

## Before you start

**Which computer.** Training runs on any Linux computer that has the host LeRobot environment and an NVIDIA GPU with driver 580 or newer. On a station PC, run this once before the first training:&#32;

`sudo chown -R robotlab:robotlab ~/.cache/huggingface`` `

The Docker container created that folder as root, and without this line, every download into it fails with "Permission denied". Do deployment (Step 4) on one of the lab stations with the follower arm and cameras.

**Which dataset.** Three merged datasets exist on the organization `autorobo`. Pick one name and use that same name in every command below:

| Dataset name | Contents | When to use it |
| --- | --- | --- |
| `vials_sim_v1` | The sim episodes merged after the freeze | Sim only training |
| `vials_real_v1` | All real episodes after the freeze | Real-only training |
| `vials_all_v1` | All simulated and all real episodes after the freeze | The main training runs |

**Run these five lines in every new terminal before anything else.** A reboot or a new terminal window forgets the three \`export\` settings; forgetting them produces the errors listed at the end of this guide.

```bash
conda activate lerobot
export HF_ORG=autorobo
export DATASET=<pick_a_dataset>     # vials_real_v1, vilas_sim_v1, or vials_all_v1
export TEAM=<your team>             # your team: t1 to t5;
hf auth whoami                      # must print a username; if not, run: hf auth login
```

`hf auth login` asks for a Hugging Face token of an account that is a member of the organization. A **read** member can download datasets and train; a **write** member is needed only to push a trained policy to the organization (Step 3, option B).

**Sharing a station PC.** Several teams use the same `robotlab` account on a station, so three rules apply there. One training at a time per PC: before starting, run `nvidia-smi` and look for a `python` process in its lower table; if one is listed, a training is already running, so wait or use another computer. No training during a booked recording session, because training slows the recording loop and makes the follower arm stutter. Every team keeps its own run name: the `TEAM` line above goes into the run name, so two teams never write into the same folder (LeRobot refuses to start when the output folder already exists).

## Step 1: Train ACT

Run the four lines mentioned above (”Before you start”), then the command below. Replace nothing in the command: the two `export` lines in "Before you start" supply the dataset name and the organization name. The first line of the command block sets RUN, the name of this training run: the word act\_ followed by the dataset name and the team, for example act\_vials\_real\_all\_t3. RUN names the output folder and the job, and the same name is used again in Steps 3 and 4. The command downloads the dataset into `~/.cache/huggingface/lerobot/` on the first run and reuses that copy afterward.

```bash
export RUN=act_${DATASET}_${TEAM}      # sets RUN, the run name: act_ + dataset + team, e.g. act_vials_all_v1_t3
lerobot-train \
  --dataset.repo_id=${HF_ORG}/${DATASET} \
  --policy.type=act \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --output_dir=${HOME}/vials/outputs/${RUN} \
  --job_name=${RUN} \
  --steps=100000 \
  --batch_size=16 \
  --save_freq=20000 \
  --log_freq=200
```

| Option | What it does |
| --- | --- |
| `--policy.type=act` | Chooses ACT (Action Chunking Transformer). Its defaults fit this dataset: it predicts the next 100 actions (3.3 s at 30 fps) from the two camera images and the six joint values, and uses an ImageNet-pretrained ResNet-18 for each camera. |
| `--policy.push_to_hub=false` | Keeps the trained policy on this computer only. Without this line LeRobot refuses to start unless `--policy.repo_id` is also given (see Step 3, option B). |
| `--output_dir` | Where checkpoints go. The path is under your home folder on purpose: a relative `outputs/` path inside the workshop folder belongs to root and cannot be written. |
| `--steps=100000` | Training length. ACT on a few hundred episodes is usually good after 50,000 to 100,000 steps. For a smoke test use `--steps=2000`. |
| `--batch_size=16` | Episodes-worth of samples per step. On an RTX 5080 (16 GB) this needs about 7 GB of GPU memory; on a 32 GB card `--batch_size=32` is fine. Reduce to 8 if the run stops with "CUDA out of memory". |
| `--save_freq=20000` | A checkpoint every 20,000 steps and one at the end. |
| `--log_freq=200` | A progress line every 200 steps. |

**Note:** There are more options than the table above. Check LeRobot Documentation.   
**How long it takes.** On the RTX 5080 in the lab, the dry-run dataset trained at about 10 steps per second with batch 8, so 100,000 steps at batch 16 take roughly 4 to 5 hours. The progress line shows `loss` (should fall from above 1 to well below 0.5 over the run), `grdn` (gradient norm), and `smp/s` (samples per second).

**Resuming after an interruption.** If the run was stopped, continue it from its last checkpoint with:

```bash
lerobot-train --config_path=${HOME}/vials/outputs/${RUN}/checkpoints/last/pretrained_model/train_config.json --resume=true
```

**Optional: training curves in Weights & Biases.** Add `--wandb.enable=true --wandb.project=vials` after running `wandb login` once. Without it, the progress lines in the terminal are the only record, so keep the terminal open or run the command inside `tmux`.

## Step 2: Train Diffusion Policy instead

Use this command in place of the ACT command in Step 1. Everything else in this guide is the same for both policies.

```bash
export RUN=diffusion_${DATASET}_${TEAM}      # sets RUN, the run name: diffusion_ + dataset + team, e.g. diffusion_vials_all_v1_t3
lerobot-train \
  --dataset.repo_id=${HF_ORG}/${DATASET} \
  --policy.type=diffusion \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --policy.resize_shape="[240, 320]" \
  --policy.crop_ratio=0.9 \
  --policy.noise_scheduler_type=DDIM \
  --policy.num_inference_steps=10 \
  --output_dir=${HOME}/vials/outputs/${RUN} \
  --job_name=${RUN} \
  --steps=100000 \
  --batch_size=16 \
  --save_freq=20000 \
  --log_freq=200
```

| Option | What it does |
| --- | --- |
| `--policy.type=diffusion` | Chooses Diffusion Policy. Its defaults: it looks at the last 2 observations, predicts 64 future actions (2.1 s) and executes 32 of them (1.1 s) before predicting again. |
| `--policy.resize_shape="[240, 320]"` | Shrinks each 640×480 camera image to 240×320 before the image encoder, which is how Diffusion Policy was designed to be used and cuts GPU memory by about four times. |
| `--policy.crop_ratio=0.9` | Takes a 216×288 crop of the shrunk image: a random crop during training (a cheap form of data augmentation), the central crop when the policy runs. |
| `--policy.noise_scheduler_type=DDIM` and `--policy.num_inference_steps=10` | When the policy runs on the arm, it denoises in 10 steps instead of 100, so an action chunk is ready in a fraction of a second. These two options don’t change training. |
| `--batch_size=16` | Fits an RTX 5080 with the resize above. Reduce to 8 if the run stops with "CUDA out of memory". |

Training time is similar to ACT, 4 to 6 hours for 100,000 steps on the RTX 5080. The loss of Diffusion Policy is a noise-prediction error and is not comparable to ACT's loss; expect it to settle around 0.05 to 0.1.

## Step 2b: Fine-tune SmolVLA instead

SmolVLA is a 450-million-parameter vision-language-action model that Hugging Face pretrained on community SO-100 and SO-101 datasets. Fine-tuning starts from that pretrained model (`lerobot/smolvla_base`), so it already knows what a gripper, a table, and a pick-and-place look like before it sees the class episodes; on a few hundred episodes, it is usually the strongest of the three policies in this guide. The cost is a larger model: training takes more GPU memory, and the checkpoint is about 1 GB.

**Once per computer**, install the extra packages SmolVLA needs, in the same environment:

```bash
pip install 'lerobot[smolvla]==0.6.1'
```

**Train.** Run the five lines from "Before you start", then:

```bash
export RUN=smolvla_${DATASET}_${TEAM}      # sets RUN, the run name: smolvla_ + dataset + team, e.g. smolvla_vials_all_v1_t3
lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=${HF_ORG}/${DATASET} \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --output_dir=${HOME}/vials/outputs/${RUN} \
  --job_name=${RUN} \
  --steps=20000 \
  --batch_size=16 \
  --save_freq=5000 \
  --log_freq=200
```

| Option | What it does |
| --- | --- |
| `--policy.path=lerobot/smolvla_base` | Replaces `--policy.type`: the policy type, its settings, and its pretrained weights all come from the base model, which is downloaded from the Hub on the first run (about 1 GB, plus the vision-language backbone it is built on). |
| `--steps=20000` | Fine-tuning needs far fewer steps than training from scratch; 20,000 is the value Hugging Face recommends. The learning rate schedule built into the model decays over 30,000 steps, so do not go much beyond that. |
| `--batch_size=16` | Fits an RTX 5080 (16 GB) because the vision-language part of the model stays frozen and only the action expert is trained. Use 32 on a 32 GB card; reduce to 8 if the run stops with "CUDA out of memory". |
| `--save_freq=5000` | A checkpoint every 5,000 steps: with a short run, more frequent checkpoints give more candidates for Step 5. |

SmolVLA reads the task sentence stored in the dataset ("Pick up the vial and place it in the rack") during training, and in Step 4 the `--task` option must carry exactly the same sentence; the command in Step 4 already does.

**Time and output.** About 2 to 3 hours for 20,000 steps on the RTX 5080. The checkpoint folder layout is the same as for ACT (Step 3), so Steps 3 to 5 apply unchanged, with `smolvla_` in place of `act_` in the run name.

**If the arm pauses between action chunks when the policy runs.** SmolVLA predicts 50 actions (1.7 s) per inference and each inference takes a noticeable fraction of a second on the station GPU. If that shows as a short stop every 1.7 s, add `--inference.type=rtc --inference.rtc.execution_horizon=10` to the Step 4 command: the policy then computes the next chunk while the current one is still being executed.

## Step 3: Find the checkpoint and bring it to a station

Training writes checkpoints under the output folder, one subfolder per saved step and a link named `last` that always points to the newest:

```
~/vials/outputs/act_vials_all_v1_t3/
  checkpoints/
    020000/pretrained_model/     <- weights (model.safetensors) and config.json
    040000/pretrained_model/
    ...
    100000/pretrained_model/
    last -> 100000               <- link to the newest checkpoint
```

The folder to hand to a station is one `pretrained_model` folder, normally `checkpoints/last/pretrained_model`. That folder is about 200 MB for ACT, 1 GB for Diffusion Policy and 1 GB for SmolVLA. What happens next depends on where the training ran.

**Trained on the station where the policy will run: nothing to copy.** The checkpoint is already on that PC. In Step 4, set the policy path straight to the checkpoint folder of the run:

```bash
export POLICY=${HOME}/vials/outputs/${RUN}/checkpoints/last/pretrained_model
```

`${RUN}` is the run name from Step 1 or Step 2, so the five lines of "Before you start" and the `export RUN=...` line must have been run in the same terminal; otherwise, write the folder name in full, for example `${HOME}/vials/outputs/act_vials_all_v1_t3/checkpoints/last/pretrained_model`. To run the same policy on a *different* station, use option A or option B below.

**Trained elsewhere (another station, a personal computer): two ways to get the folder onto the station PC.**

**Option A: copy the folder.** From the training computer, with the station reachable over the network (replace `stationA` with the station's hostname or IP address):

```bash
scp -r ${HOME}/vials/outputs/${RUN}/checkpoints/last/pretrained_model robotlab@stationA:~/policies/${RUN}
```

A USB stick works just as well: copy the `pretrained_model` folder onto it, then on the station copy it to `~/policies/<run name>`. In Step 4, `--policy.path` is then `${HOME}/policies/<run name>`.

**Option B: push the policy to the organization.** This needs a write-role token. On the training computer:

```bash
python -c "from lerobot.policies.factory import get_policy_class; import json, pathlib
p = pathlib.Path('${HOME}/vials/outputs/${RUN}/checkpoints/last/pretrained_model')
cls = get_policy_class(json.load(open(p/'config.json'))['type'])
cls.from_pretrained(p).push_to_hub('${HF_ORG}/${RUN}', private=True)"
```

On the station, nothing needs copying: in Step 4, `--policy.path` is `${HF_ORG}/${RUN}` and LeRobot downloads the policy with the station's token. Keep policies private like the datasets.

## Step 4: Run the policy on a station's real arm

Do this on the station PC, logged in as `robotlab`, in a normal terminal on the host (not inside the container: the container's LeRobot cannot load policies trained with LeRobot 0.6.1). The follower arm must be powered and the two cameras connected, as for a real recording session. The leader arm is not used; move it out of the way.

**Set the scene exactly as for recording**: the vial rack and the vials in the positions the station card prescribes, nothing else on the mat, hands and objects clear of the arm's reach.

**Run these lines.** The `source` line loads the station's own values (`ROBOT_PORT`, `ROBOT_ID`, `CAMERA_GRIPPER`, `CAMERA_EXTERNAL`) from the file the setup checklist filled in, so nothing has to be typed from the card. Set `POLICY` to the folder from Step 3, option A, or to the organization name from option B.

```bash
conda activate lerobot
source ~/Sim-to-Real-SO-101-Workshop/docker/env
# POLICY = where the trained policy is. Its name is the run name from Step 1 or Step 2:
#   all dataset, team 3:   act_vials_all_v1_t3   (or diffusion_vials_all_v1_t3)
#   final dataset, team 3:     act_vials_all_v1_t3      (or diffusion_vials_all_v1_t3)
# Keep ONE of the three lines below and put your run name in it.
export POLICY=${HOME}/vials/outputs/act_vials_all_v1_t3/checkpoints/last/pretrained_model   # trained on this station
# export POLICY=${HOME}/policies/act_vials_rall_v1_t3        # copied to this station (Step 3, option A)
# export POLICY=autorobo/act_vials_all_v1_t3                # pushed to the organization (Step 3, option B)
lerobot-rollout --strategy.type=base \
  --policy.path=${POLICY} \
  --policy.device=cuda \
  --robot.type=so101_follower \
  --robot.port=${ROBOT_PORT} \
  --robot.id=${ROBOT_ID} \
  --robot.use_degrees=false \
  --robot.calibration_dir=${HOME}/.cache/huggingface/lerobot/calibration/robots/so101_follower \
  --robot.max_relative_target=10 \
  --robot.cameras="{ego: {type: opencv, index_or_path: ${CAMERA_GRIPPER}, width: 640, height: 480, fps: 30}, external_D455: {type: opencv, index_or_path: ${CAMERA_EXTERNAL}, width: 640, height: 480, fps: 30}}" \
  --task="Pick up the vial and place it in the rack" \
  --fps=30 \
  --duration=45 \
  --display_data=true
```

| Option | Why it is there |
| --- | --- |
| `--robot.use_degrees=false` | The dataset stores joint values on the −100 to 100 scale (the container's convention). Otherwise, LeRobot 0.6.1 would read the policy’s outputs as degrees and send the arm to the wrong positions. Never omit it. |
| `--robot.calibration_dir=...so101_follower` | The arm was calibrated inside the container, which saved the file under `so101_follower`; LeRobot 0.6.1 looks under `so_follower` unless told. |
| `--robot.cameras="{ego: ..., external_D455: ...}"` | The policy finds its two images by these names, which must be exactly the names used during recording: `ego` for the gripper camera, `external_D455` for the fixed camera. |
| `--robot.max_relative_target=10` | Caps how far any joint may move per 1/30 s tick (10 units on the −100..100 scale). It makes a badly behaved policy slow rather than violent. Raise to 20 once the policy is trusted; a cap that is too low makes the arm lag behind the policy's intent. |
| `--duration=45` | The run ends after 45 s, the same limit as a recorded episode, and the arm returns to its starting pose. |
| `--display_data=true` | Opens a window with both camera views and the joint values during the run. |

**During the run.** A window appears; the arm starts after a few seconds of warm-up. Watch the first seconds closely. Ctrl+C stops the arm at once at any moment. If the arm heads for a joint limit at speed, stop it, and check `--robot.use_degrees=false` and the calibration folder before trying again.

**What a good result looks like.** The arm moves towards a vial, closes the gripper on it, lifts it, carries it over the rack, and lowers it into a hole. A policy trained on the dry-run dataset will usually get only part of the way; a policy trained on the full class dataset should succeed on a good share of attempts (Step 5 measures it).

## Step 5: Measure success

Judge a policy by how often it completes the task, not by its training loss. Use the same protocol for every policy so you can compare the numbers.

1. Run Step 4 ten times in a row at one station. Before each run, put the vial back at its starting position and the rack where the station card prescribes; change nothing else between runs.
2. A run is a **success** when the vial stands in a rack hole, and the gripper has released it within 45 s. Everything else is a failure; note how far it got.
3. Write one row per policy in the table below. Ten runs give a resolution of 10 percentage points, which is enough to tell a working policy from a failing one; use twenty runs when two policies are close.

| Policy (run name) | Dataset | Checkpoint step | Station | Successes out of 10 | Typical failure | Date |
| --- | --- | --- | --- | --- | --- | --- |
| (example) act\_vials\_all\_v1\_t0 | vials\_all\_v1 | 2000 | A | 0 | (example) hovers above the vial, never closes the gripper | (example) |
|  |  |  |  |  |  |  |

To compare stations, repeat the ten runs at a second station with the same checkpoint: the difference between stations shows how much the policy depends on one station's camera placement and calibration.

**Optional: record the evaluation runs.** Replacing `--strategy.type=base` with `--strategy.type=episodic --strategy.num_episodes=10 --dataset.repo_id=${HF_ORG}/eval_${RUN} --dataset.single_task="Pick up the vial and place it in the rack" --dataset.push_to_hub=false` records every run as an episode of a new dataset named `eval_<run name>`, with reset pauses between runs, so failures can be replayed in the viewer later.

## Errors seen so far and their fixes

| The message | The cause | The fix |
| --- | --- | --- |
| `ValueError: 'repo_id' argument missing. Please specify it to push the model to the hub.` | `--policy.push_to_hub=false` was left out of the training command. | Add `--policy.push_to_hub=false`, or add `--policy.repo_id=${HF_ORG}/${RUN}` to push the result at the end of training. |
| `Repo id must use alphanumeric chars ... '/vials_aa_v1'` | `HF_ORG` is empty: a new terminal or a reboot forgot the `export` line. | Run the four lines from "Before you start" again. |
| `The NVIDIA driver on your system is too old (found version 12090)` followed by training on the CPU | The GPU driver is older than 580; the PyTorch that LeRobot installs needs 580 or newer. | Update the driver (Ubuntu: `sudo apt install nvidia-driver-580-open`, then reboot) and check that `nvidia-smi` reports CUDA 13.0. |
| `PermissionError: [Errno 13] Permission denied: 'outputs/train'` at the first checkpoint | The output folder belongs to root (it was created by the Docker container). | Use `--output_dir=${HOME}/vials/outputs/${RUN}` as in Step 1, or `sudo chown -R $USER:$USER outputs`. The training itself was fine; rerun it. |
| `401` or `Repository Not Found` when the dataset is downloaded | No Hugging Face token on this computer, or the account is not a member of the organization. | `hf auth login` with a token of a member account; `hf auth whoami` must list the organization. |
| `CUDA out of memory` during training | The batch is too large for the GPU. | Halve `--batch_size`; for Diffusion Policy keep the `--policy.resize_shape` option. |
| `KeyError: 'observation.images.ego'` or a similar missing-key error when the policy runs | The camera names in `--robot.cameras` differ from the names used during recording. | Use exactly `ego` and `external_D455`, as in Step 4. |
| The arm moves to wrong positions or towards a joint limit when the policy runs | `--robot.use_degrees=false` or `--robot.calibration_dir` was left out, so the policy's −100..100 outputs were read as degrees. | Stop with Ctrl+C; add both options as in Step 4. |
| `Failed to sync read 'Present_Position' ... There is no status packet!` when the policy runs | The follower arm's motors have no power, or the USB cable is loose. | Check the power LED and the cables, then run again. |
| `PermissionError: [Errno 13] Permission denied: '/home/robotlab/.cache/huggingface/lerobot/hub'` while the dataset is downloaded | On a station PC the folder `~/.cache/huggingface/lerobot` belongs to root: the Docker container created it when it mounted the calibration folder. | `sudo chown -R robotlab:robotlab ~/.cache/huggingface` once, then run the training command again. The container is unaffected. |
| `FileExistsError: Output directory ... already exists and resume is False` | A run with the same name was started before on this computer, by you or by another team. | Check the `TEAM` line in "Before you start". To continue your own interrupted run, use the resume command in Step 1; to start afresh, add a suffix to RUN, e.g. `export RUN=${RUN}_b`. |
