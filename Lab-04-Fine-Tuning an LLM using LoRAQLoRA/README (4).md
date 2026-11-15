# Lab 4: Fine-Tuning an LLM using LoRA/QLoRA

**Module:** PUSL 3205 - Large Language Models and Generative AI
**Model:** Qwen/Qwen2.5-0.5B-Instruct
**Domain:** TechNest Computers (a fictional computer shop)
**Method:** QLoRA (4-bit quantisation + LoRA adapters) with Hugging Face TRL `SFTTrainer`
**Platform:** Google Colab (free NVIDIA T4 GPU)

---

## 1. Overview

In this lab I fine-tuned a small instruction-tuned language model so that it can answer customer questions for a computer shop. I created my own dataset of 32 question-and-answer pairs, trained LoRA adapters on top of a 4-bit quantised model (QLoRA), and then compared the original model with the fine-tuned model using the same questions, including questions that were **not** in the training data.

## 2. Folder Structure
```
Lab-03-Tiny-Transformer/
├── README.md
├── notebook/
│   └── Lab_04_Fine_Tuning_an_LLM_using_LoRA_QLoRA_(2).ipynb
└── screenshots
    └── 01_gpu.png ... 07_discussion.png   (screenshots of outputs)
```

## 3. Tasks and Implementation
Full code: [`notebook/lab03_tiny_transformer.ipynb`](notebook/Lab_04_Fine_Tuning_an_LLM_using_LoRA_QLoRA_(2).ipynb)

Libraries used: `transformers`, `datasets`, `peft`, `trl`, `accelerate`, `bitsandbytes`.

---

## 4. Task-by-task report

### Task 1: Install the required libraries

I installed the six required libraries with one command:

```python
!pip install -q -U transformers datasets peft trl accelerate bitsandbytes
```

### Task 2: Check the GPU

I checked the GPU with PyTorch (`torch.cuda.is_available()`).

![GPU check](screenshots/01_gpu.png)

**What GPU is available?**
An NVIDIA Tesla T4 with about 15 GB of memory, provided free by Google Colab.

**Why is a GPU useful for LLM fine-tuning?**
Fine-tuning is mostly huge numbers of matrix multiplications. A GPU has thousands of small cores that run these calculations in parallel, so training is many times faster than on a CPU. A GPU also has fast, high-bandwidth memory (VRAM) that holds the model weights, activations and gradients.

### Task 3: Choose the model

I chose **Qwen/Qwen2.5-0.5B-Instruct** because:
- It is small (about 0.5 billion parameters), so it fits easily on the T4 GPU.
- It is already instruction-tuned, so it understands the chat format.
- It is a causal language model that is supported by the current Hugging Face transformers, PEFT and TRL libraries.

### Task 4: Create the dataset

I created **32 question-and-answer pairs** about a fictional computer shop called **TechNest Computers**. Because the shop is made up, the original model cannot know the answers, so the effect of fine-tuning is easy to see.

The dataset covers: shop name and location, opening hours, laptops, gaming laptops, desktops, custom PC builds, warranty, repairs, upgrades, RAM and SSD prices, monitors, accessories, payment methods, instalment plans, student discount, delivery, returns, trade-ins, contact details and refurbished laptops.

Each example is stored in chat format (`user` question and `assistant` answer).

![Dataset](screenshots/02_dataset.png)

### Task 5: Configure LoRA with PEFT (QLoRA)

To save GPU memory I loaded the model in **4-bit (QLoRA)** and added LoRA adapters with PEFT.

| Setting | Value |
|---|---|
| Quantisation | 4-bit NF4 with double quantisation |
| Compute dtype | float16 |
| LoRA rank (`r`) | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| Target modules | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |

![LORA](screenshots/03_LORA.png)

Result: **8,798,208 trainable parameters out of 502,830,976 in total (about 1.75%)**. Only the small adapters are trained and the original weights stay frozen.

### Task 6: Supervised fine-tuning with SFTTrainer

I trained the model with Hugging Face TRL's `SFTTrainer`.

| Setting | Value |
|---|---|
| Epochs | 10 |
| Batch size | 4 (with gradient accumulation of 2) |
| Learning rate | 2e-4 (cosine schedule) |
| Warm-up steps | 4 |
| Optimiser | `paged_adamw_8bit` |

The training loss went down during training, which shows that the model was learning from the dataset.

![Training](screenshots/04_training.png)

### Tasks 7 and 8: Compare the original and the fine-tuned model

Task 8 on the lab sheet repeats task 7, so one comparison covers both.

I asked **both models the same 6 questions**. The first 3 were in the training data and the last 3 were **new questions** that were not in the dataset.

| No. | Question | In training data? |
|---|---|---|
| 1 | What are your opening hours? | Yes |
| 2 | Do you offer instalment plans? | Yes |
| 3 | How much is a 1TB SSD? | Yes |
| 4 | Do you sell gaming headsets? | No |
| 5 | Is there a discount for university staff? | No |
| 6 | Do you sell webcams? | No |

**Original model (before fine-tuning):**

![Original model answers](screenshots/05_original_answers.png)

**Original vs fine-tuned (side by side):**

![Comparison](screenshots/06_comparison.png)

---

## 5. Results and discussion

- **Original model:** It gave generic answers. It knows nothing about TechNest Computers, so for shop-specific questions (opening hours, prices, instalment plans) it gave general advice or guessed.
- **Fine-tuned model:** For the questions that were in the training data it answered with the facts and the style of TechNest Computers. This shows that LoRA successfully taught the model the new domain.
- **Unseen questions:** For the new questions the fine-tuned model copies the TechNest answer style, but it has no real facts about those products, so it can invent details (hallucinate). This is expected with a very small dataset.

![Discussion](screenshots/07_discussion.png)

### Why LoRA/QLoRA is efficient
- Only about 1.75% of the parameters are trained, so training is fast and needs little memory.
- 4-bit quantisation shrinks the frozen base model to about a quarter of its memory.
- Together, this makes fine-tuning possible on a free T4 GPU.

### Limitations
- The dataset has only 32 examples, so the model mostly learns the training facts and the style.
- The shop data is fictional, so the model cannot be used as a real product catalogue.

### Possible improvements
- Use a larger and more varied dataset with many ways of asking the same question.
- Combine the fine-tuned model with retrieval (RAG) so that prices and products come from a real database.

### How to run the notebook
1. Open [Google Colab](https://colab.research.google.com) and upload `Lab4_LoRA_QLoRA.ipynb`.
2. Click **Runtime > Change runtime type** and choose **T4 GPU**.
3. Click **Runtime > Run all**.

Libraries used: `transformers`, `datasets`, `peft`, `trl`, `accelerate`, `bitsandbytes`.

## 6. Conclusion

LoRA and QLoRA make it practical to adapt a language model to a specific domain with very little GPU memory and only a small number of trainable parameters. In this lab the fine-tuned model clearly learned the TechNest Computers domain compared with the original model, and I learned the limits of fine-tuning on a small dataset.
