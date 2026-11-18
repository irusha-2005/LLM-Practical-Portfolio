# Lab 4 Summary: Fine-Tuning an LLM using LoRA/QLoRA

**Module:** PUSL 3205 - Large Language Models and Generative AI
**Lab sheet:** Lab Sheet 4 - Fine-Tuning an LLM using LoRA/QLoRA

## 1. What this lab was about

The goal of the lab was to take a small, instruction-tuned language model and **fine-tune** it on a small dataset from a specific domain, using **LoRA/QLoRA** so that it can be done on a limited GPU. After fine-tuning, the original model and the fine-tuned model are tested with the same questions to see the difference.

**What I did in one paragraph:** I used Google Colab with a free T4 GPU, loaded the model Qwen/Qwen2.5-0.5B-Instruct, created a dataset of 32 question-and-answer pairs about a fictional computer shop (TechNest Computers), set up QLoRA (4-bit model + LoRA adapters) with PEFT, trained it with TRL's SFTTrainer, and then compared the original and fine-tuned model on 6 questions (3 from the training data and 3 new ones).

---

## 2. Summary of every task on the lab sheet

| Task | Lab sheet requirement | What I did | Result |
|---|---|---|---|
| 1 | Install the required libraries: transformers, datasets, peft, trl, accelerate, bitsandbytes | Ran one `pip install` command in Colab for all six libraries | Libraries installed (a harmless `cudf`/`pyarrow` warning appeared and was ignored) |
| 2 | Check whether a GPU is available and identify its type and memory. Record: What GPU is available? Why is a GPU useful for LLM fine-tuning? | Used `torch.cuda.is_available()`, `get_device_name` and the memory property | NVIDIA Tesla T4, about 15 GB memory. A GPU is useful because training is mostly matrix multiplication, which a GPU does in parallel on thousands of cores, with fast memory for weights and gradients |
| 3 | Choose a small, instruction-tuned causal language model that is compatible with the GPU and current Hugging Face tools | Chose **Qwen/Qwen2.5-0.5B-Instruct** | About 0.5 billion parameters, instruction-tuned, fits easily on the T4 |
| 4 | Create a small dataset of at least 30 question-and-answer pairs about a specific domain (example: a computer shop) | Wrote **32 Q&A pairs** about a fictional shop, TechNest Computers, in chat format | Dataset of 32 pairs (opening hours, prices, warranty, repairs, delivery, payments, etc.) |
| 5 | Use PEFT to configure LoRA. If GPU memory is limited, use QLoRA with 4-bit quantisation | Loaded the model in 4-bit NF4 (QLoRA) and added LoRA adapters: r=16, alpha=32, dropout=0.05, on the attention and MLP layers | 8,798,208 trainable parameters out of 502,830,976 (about 1.75%) |
| 6 | Use a supported supervised fine-tuning workflow, such as TRL's SFTTrainer | Trained with `SFTTrainer` and `SFTConfig`: 10 epochs, batch size 4, gradient accumulation 2, learning rate 2e-4, cosine schedule | Training completed and the loss went down |
| 7 | Test both the original and fine-tuned model using the same questions, including questions not in the training data | Asked both models the same 6 questions: 3 from the dataset and 3 new ones | Original gave generic answers; fine-tuned gave TechNest-style answers |
| 8 | (Repeat of task 7 on the lab sheet) | Covered by the same comparison as task 7 | Same as task 7 |

---

## 3. Key settings

**Model:** Qwen/Qwen2.5-0.5B-Instruct

**QLoRA (4-bit) settings**
- Quantisation: NF4 with double quantisation
- Compute dtype: float16

**LoRA settings**
- Rank `r` = 16
- `lora_alpha` = 32
- `lora_dropout` = 0.05
- Target modules: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`

**Training settings (SFTTrainer)**
- Epochs: 10
- Per-device batch size: 4, gradient accumulation steps: 2
- Learning rate: 2e-4 with a cosine schedule, 4 warm-up steps
- Optimiser: `paged_adamw_8bit`

**Test questions (same for both models)**

| No. | Question | In training data? |
|---|---|---|
| 1 | What are your opening hours? | Yes |
| 2 | Do you offer instalment plans? | Yes |
| 3 | How much is a 1TB SSD? | Yes |
| 4 | Do you sell gaming headsets? | No |
| 5 | Is there a discount for university staff? | No |
| 6 | Do you sell webcams? | No |

---

## 4. Results

- **Original model:** gave general, generic answers. It has no knowledge of TechNest Computers, so it could not give the real opening hours, instalment plans or prices.
- **Fine-tuned model:** answered the training-data questions with TechNest facts and in the TechNest answer style. This shows that LoRA taught the model the new domain.
- **New (unseen) questions:** the fine-tuned model copies the TechNest style, but it has no real facts about those products, so it may invent details. This is a limit of a very small dataset.

## 5. Problems I met and how they were fixed

| Problem | Cause | Fix |
|---|---|---|
| Red warning after `pip install` about `cudf` and `pyarrow` | A Colab package that this lab does not use | Ignored, because it is only a warning |
| Local computer could not run the lab | Local PyTorch is blocked and there is no GPU | Used Google Colab with a free T4 GPU |
| `SFTConfig` error: unexpected argument `warmup_ratio` | The newer library version removed this argument | Used `warmup_steps=4` instead |
| `NotImplementedError ... not implemented for 'BFloat16'` during training | The model's number type (bfloat16) did not work with fp16 training on the T4 | Reloaded a fresh 4-bit model in float16 and turned off `fp16`/`bf16` in `SFTConfig` |

## 6. What I learned

- **LoRA** trains only small adapter matrices (about 1.75% of the parameters) instead of the whole model, so it is fast and needs little memory.
- **QLoRA** also stores the frozen base model in 4-bit, which cuts memory a lot, so a model can be fine-tuned on a free T4 GPU.
- Fine-tuning on a small dataset teaches **style and the training facts**, but it does not give the model new knowledge about things it never saw.
- For real, up-to-date facts (like prices), a bigger dataset or **RAG** (retrieval) would work better.

## 7. Files for this lab

| File | Description |
|---|---|
| `Lab4_LoRA_QLoRA.ipynb` | Full notebook with code and outputs for tasks 1 to 8 |
| `README.md` | Full lab report with screenshots |
| `Lab4_Summary.md` | This summary |
| `01_gpu.png` to `05_comparison.png` | Screenshots of the results |
