# Hugging Face GPU Jobs: Setup for Autonomous Robotics Teams

**Audience:** CMU Autonomous Robotics instructor and five student teams  
**Purpose:** Train one robot-learning policy per team (ACT, Diffusion Policy, SmolVLA, or NVIDIA GR00T) on prerecorded demonstration datasets using NVIDIA GPUs, billed to the course's existing Hugging Face organization.

> **Before starting:** Replace `YOUR_ORG` and `YOUR_DATASET` with the actual Hugging Face organization and dataset names. A Hugging Face organization with a positive compute-credit balance can run Jobs. Jobs are billed by the minute while starting or running; you don’t need an organization subscription upgrade just to use Jobs.

## Step 1 — Fund the existing Hugging Face organization

**Instructor** (already done)

1. Sign in at [huggingface.co](https://huggingface.co).
2. Open the existing organization that hosts the demonstration datasets.
3. Go to **Organization Settings → Billing**.
4. Add a payment method and purchase an initial amount of compute credits (for example, **$200**).
5. Review the credit balance, expiry date, compute usage, and any automatic-recharge setting. Consider keeping automatic recharge off initially for tighter control.

**Important:** The credits are not necessarily a hard spending cap. Monitor usage and establish course limits on hardware and GPU-hours. Jobs are charged to the account specified by `--namespace`; omitting it normally bills the student's personal account.

## Step 2 — Invite the five student teams

**Instructor** (already done)

1. Open **Organization Settings → Members**.
2. Invite the student accounts using their Hugging Face usernames or email addresses.
3. Assign a role that lets students create model repositories and submit Jobs on behalf of the organization. **Write** is a straightforward option; verify access with the test in Step 4.
4. Keep instructor billing and administrative permissions separate from student accounts.

**Note:** Standard organization permissions do not provide automatic per-team Jobs spending caps. More granular Jobs restrictions are available on Enterprise plans. Establish a per-team GPU-hour budget and review usage regularly.

## Step 3 — Install the Hugging Face CLI and authenticate

**Each student**, on their own laptop/workstation:

```bash
python3 -m pip install --upgrade huggingface_hub
hf auth login
```

Authenticate with your **own** Hugging Face account and an access token with permissions to run Jobs and access the relevant course dataset/model repositories. Never share the instructor's token or commit tokens to GitHub.

See available GPU hardware and prices:

```bash
hf jobs hardware
```

## Step 4 — Confirm organization-billed NVIDIA GPU access

**One student** should first run this small GPU test:

```bash
hf jobs uv run \
  --namespace YOUR_ORG \
  --name gpu-test \
  --flavor l4x1 \
  --timeout 10m \
  --with torch \
  python -c 'import torch; print("CUDA available:", torch.cuda.is_available()); print("GPU:", torch.cuda.get_device_name(0))'
```

Expected outcome: CUDA is available and the device is an **NVIDIA L4**. A 10-minute L4 Job costs at most about **$0.13** in nominal GPU-time charges at $0.80/hour (depending on actual billable minutes).

If the Job fails, check organization membership and permissions, token authentication, available credits, and whether the `--namespace` value matches the organization's exact name.

## Step 5 — Submit each team's training Job

A student with a **standalone `train.py` script compatible with `uv`** can use the following pattern:

```bash
hf jobs uv run \
  --namespace YOUR_ORG \
  --name team1-act \
  --flavor l4x1 \
  --timeout 8h \
  --secrets HF_TOKEN \
  -v hf://datasets/YOUR_ORG/YOUR_DATASET:/data \
  train.py
```

Customize the command for each team's policy and training script. In particular:

- **ACT, Diffusion Policy, SmolVLA:** Start by testing `l4x1` (NVIDIA L4, 24 GB VRAM). Actual memory requirements depend on the model and training configuration.
- **GR00T:** Consider `l40sx1` (NVIDIA L40S, 48 GB VRAM) for memory-efficient fine-tuning, or a larger configuration if needed. Verify the selected GR00T version's official minimum VRAM requirements before the full run.
- The mounted dataset (`/data`) is **read-only**. Adapt the script to load from that path, or use the Hugging Face Datasets library directly.
- `--secrets HF_TOKEN` forwards the student's own token to the Job when training code needs to read private content or push outputs to the Hub. Their token needs appropriate repository permissions.
- `--timeout 8h` is a **maximum duration**, not a reservation. Shorten it for initial tests.
- If the training program depends on a full code repository, specialized CUDA libraries, or system packages (particularly for GR00T), use a compatible **Docker image/Jobs workflow** rather than assuming the single-file `uv` example will work unchanged.

**Important: Persist outputs before the Job ends.** A Job's local filesystem is ephemeral. Push the trained weights to an organization model repository (e.g., `YOUR_ORG/team1-act`) or write checkpoints to a mounted Hugging Face Storage Bucket. Verify the trained model or checkpoints were successfully saved.

For bucket-based checkpoint storage, see [Jobs configuration: Volumes](https://huggingface.co/docs/hub/jobs-configuration#volumes).

## Step 6 — Monitor and manage Jobs

**Instructor or authorized students** can inspect organization Jobs:

```bash
# Running/scheduled Jobs
hf jobs ps --namespace YOUR_ORG

# All Jobs, including completed and failed runs
hf jobs ps -a --namespace YOUR_ORG

# Logs for a specific Job
hf jobs logs --namespace YOUR_ORG JOB_ID

# Cancel a specific Job
hf jobs cancel --namespace YOUR_ORG JOB_ID
```

You can also use **Organization Settings → Jobs** to view runs and **Billing → Compute Usage** to monitor cost. Review failed jobs promptly, and remind students to use descriptive names such as `team2-diffusion`.

## Step 7 — Establish a simple GPU budget for the course

(Already done). 

A reasonable *starting* budget is **$200 in organization compute credits**, reviewed after the teams' first successful small runs. The following published on-demand prices are approximate and subject to change:

| Hugging Face GPU flavor | NVIDIA GPU | VRAM | Approximate hourly price | Suggested workload |
| --- | --- | ---: | ---: | --- |
| `l4x1` | L4 | 24 GB | $0.80 | ACT, Diffusion Policy, SmolVLA |
| `l40sx1` | L40S | 48 GB | $1.80 | Memory-efficient GR00T fine-tuning |
| `rtx-pro-6000` | RTX PRO 6000 | 96 GB | $2.75 | Larger GR00T configurations |

**Example:** Four teams receiving 20 hours each on L4 GPUs, plus one team receiving 30 hours on L40S, would consume approximately **$118** in nominal GPU compute charges. This is a budget scenario, not a prediction of each team's training time.

Require students to use a short verification run before launching full training, and confirm persistent checkpoint/model storage before spending substantial GPU time. Replenish credits only after checking actual use.

---

## Instructor checklist

- [ ] Add billing and an initial compute-credit balance to the existing organization.
- [ ] Invite student accounts and verify appropriate permissions.
- [ ] Have students install the CLI and authenticate individually.
- [ ] Run a successful `l4x1` GPU test billed to `YOUR_ORG`.
- [ ] Assign per-team hardware/time limits and model output repositories.
- [ ] Check Jobs status, compute costs, and saved checkpoints during training.

## Official documentation

- [Hugging Face Jobs quickstart](https://huggingface.co/docs/hub/jobs-quickstart)
- [Jobs pricing and billing](https://huggingface.co/docs/hub/jobs-pricing)
- [Jobs configuration: authentication, secrets, volumes, GPUs, and timeouts](https://huggingface.co/docs/hub/jobs-configuration)
- [Training models on Jobs](https://huggingface.co/docs/hub/jobs-training)
- [Managing Jobs](https://huggingface.co/docs/hub/jobs-manage)
- [Hugging Face organization access control](https://huggingface.co/docs/hub/organizations-security)

*Instructions and published hardware prices checked November 20, 2026. Confirm the current documentation before running production training jobs.*
