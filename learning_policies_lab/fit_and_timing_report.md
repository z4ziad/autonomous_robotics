# Fit-and-Timing Report: Instructions

Autonomous Robotics II · one page per team · due before your first training night.

Two questions, answered with measurements: does your policy fit on the station's RTX 5080 (16 GB), and is it fast enough for the 30 Hz loop?

## What to hand in

One page, as a table with these rows, plus one sentence per row saying how you measured it. Fill the "expected" column *before* you run anything, from the Lecture 11 formulas; a measurement far from the expected value is a bug to find, not a result to report.

| Row | Expected (from the formulas) | Measured |
|---|---|---|
| Parameters N (total) and N_train (the ones you will update) | from the model card / config | printed by the code |
| Run-time GPU memory at batch 1, bf16, two camera views | ≈ 2 bytes × N, plus a little | peak allocated, in GB |
| Seconds per call at batch 1 | ≥ 2N / (960 GB/s) per weight read, × reads per call | mean of 20 calls after 5 warm-ups |
| Actions per call k (the chunk) and the loop check | k × 33 ms must be ≥ seconds per call | yes / no, with the margin |
| Training GPU memory at your batch size | ≈ 2 × N + 16 × N_train, plus activations | peak allocated, in GB |
| Seconds per training step, and steps per night | one night = 8 h = 28,800 s | measured over 20 steps |
| Your recipe | — | full fine-tune / expert only / LoRA (rank, which layers), batch size, learning rate |

---

## Part 1 — Run time: does it fit, and is it fast enough?

1. **Load the base checkpoint** (the one you will fine-tune from) on the station PC in bf16. Do not train anything yet.
2. **Build one real input:** two camera frames from an s01 episode at the resolution the model expects, the robot's joint state, and the instruction "pick up the vial and place it in the rack."
3. **Call the policy once at batch 1** and record peak GPU memory: `torch.cuda.max_memory_allocated()` in GB (or the number `nvidia-smi` shows while the call runs). Expected: about 2 bytes per parameter, so a 3 B model is about 6 GB, a 0.45 B model about 1 GB. If you measure 2–3× more, something is still in fp32.
4. **Time the call:** 5 warm-up calls, then 20 timed calls; report the mean in milliseconds. The floor is one read of the weights per pass, 2N / 960 GB/s: about 7 ms for 3 B parameters. A token-output model pays that once *per token*; a flow or diffusion head pays the VLM once plus a few small passes of the expert.
5. **The loop check:** your policy returns k actions per call. The arm runs at 30 Hz, so one call may take at most k × 33 ms. Write both numbers and the margin. If the call is too slow, the fixes are, in order: a bigger chunk k, fewer denoising / flow steps, a smaller image.

Report what you measured even if it fails the check; the point of the page is to know before the first training night.

---

## Part 2 — Training: does it fit, and how much can you do in a night?

1. **Run 20 training steps** on your s01 episodes with the recipe you intend to use (see the LoRA section and your team's note below). Start from the default batch size of the training code you use (LeRobot, openpi, or Isaac-GR00T; see the per-team notes).
2. **Record peak GPU memory** the same way as in Part 1. Expected: 2 bytes × N for the frozen weights, plus 16 bytes × N_train for the weights you update (gradient, two optimizer averages, fp32 copy), plus the activations, which grow with batch size and image size.
3. **If it runs out of memory**, change one thing at a time and re-run the 20 steps, in this order: halve the batch size; turn on gradient checkpointing (recomputes activations instead of storing them; slower, much less memory); turn off EMA if the code keeps one; freeze more of the model or switch to LoRA. Write down which step made it fit.
4. **Record seconds per step** and compute steps per night: 28,800 s divided by seconds per step. With 80 real + 30 sim episodes at 30 Hz you have roughly 100 k frames; divide to see how many passes over the data one night gives you.
5. **Check that it is learning:** the loss after 20 steps should be lower than at step 1. Not a result yet, just proof the pipeline is wired.

---

## LoRA: who needs it, and what to set

**Do you have to choose a LoRA rank?** Only if your model is too big to fine-tune in full on 16 GB, which means Teams 3, 4 and 5 (3 B-parameter models). Team 2 trains only SmolVLA's action expert with the VLM frozen, and Team 1 trains its DiT policy from scratch; neither needs LoRA.

**What LoRA is, in one line (Lecture 11):** every pretrained weight matrix W stays frozen and the model learns a small correction beside it, W′ = W + B × A, where A is r × d and B is d × r. Only A and B are trained, so the 16-bytes-per-parameter training cost applies to 2 × d × r numbers per matrix instead of d × d. At run time nothing changes: the correction is folded into W, so speed is identical to the base model.

**Three settings, in order of how much they matter:**

1. **Which parts get adapted (matters most).** Apply LoRA to every linear layer of the language model and the action head, not only to the attention matrices. Keep the vision encoder trainable (LoRA on it too) if memory allows: in OpenVLA's fine-tuning study, freezing the vision encoder cost 23 points of success (69.7 % → 47.0 %), far more than any rank choice.
2. **Batch size and gradient checkpointing (matter for memory).** These, not the rank, decide whether training fits: activations dominate once the weights are frozen.
3. **The rank r and the scale α (matter least).** Use the default of the training code your team runs and do not tune it: Isaac-GR00T's fine-tuning script (Team 5) uses r = 64, α = 128; openpi (Teams 3 and 4) ships its own LoRA training configs; OpenVLA used r = 32. OpenVLA measured r = 32 and r = 64 at the same success rate (68.2 % both, against 69.7 % for a full fine-tune) while the trainable count doubled (97.6 M → 195.2 M) and memory barely moved (59.7 → 60.5 GB). The rule of thumb is α = 2r, and the learning rate for LoRA is usually higher than for full fine-tuning (again, keep the default of that code).

**The arithmetic to put in the report:** N_train = (number of adapted matrices) × 2 × d × r. For a 3 B model with r = 32 on all linear layers this comes to roughly 50–100 M parameters, so the training-side memory is about 2 × 3 × 10⁹ = 6 GB (frozen) + 16 × 10⁸ ≈ 1.6 GB (adapters) + activations. Whether the activations fit in the remaining 8 GB is what the 20-step dry run tells you.

---

## Per-team notes

| Team | Model | Recipe to expect | Watch out for |
|---|---|---|---|
| 1 | DiT (diffusion transformer policy) | LeRobot (huggingface/lerobot) diffusion-policy training, or your own DiT code: train from scratch on your episodes; everything trainable; no LoRA | the denoising steps set your seconds per call; measure at the step count you will deploy with |
| 2 | SmolVLA (0.45 B) | LeRobot (huggingface/lerobot) fine-tune from `smolvla_base`: VLM frozen, action expert (≈ 100 M) trained in full; no LoRA | run-time memory about 1 GB; the loop check should pass easily; report the chunk size you use |
| 3 | π₀ (3.3 B) | openpi (Physical-Intelligence/openpi), its LoRA fine-tuning config: LoRA on the VLM and the action expert | openpi's own table says LoRA fine-tuning needs more than 22.5 GB at its default batch size: expect the first dry run to fail on 16 GB, then cut the batch size, disable EMA, and report where it fits (or that it does not) |
| 4 | π₀-FAST (3.3 B) | same as Team 3 | same memory note; at run time measure seconds per call *including* the 30–60 FAST tokens, since each token is one weight read |
| 5 | GR00T N1.5 (3 B) | Isaac-GR00T (NVIDIA/Isaac-GR00T) `gr00t_finetune.py` with its LoRA flags (r = 64, α = 128); language model frozen by default | NVIDIA used two 24 GB cards for LoRA fine-tuning; on one 16 GB card start with the smallest batch and gradient checkpointing, and report where it fits |

If a model does not fit for training on the station after the steps in Part 2, say so on the page with the numbers; that is a valid result and we will decide together whether to train it elsewhere, quantize the base weights, or change the recipe.
