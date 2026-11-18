# Lab 3 Summary: Developing a Tiny Transformer Language Model

**Module:** PUSL3205 Large Language Models and Generative AI

## 1. Lab sheet at a glance
| Item | Details |
|---|---|
| Title | Developing a Tiny Transformer Language Model |
| Dataset | `roneneldan/TinyStories` (Hugging Face): short stories written with simple words |
| Goal | Build, train and evaluate a small Transformer that predicts the next token, then generate stories with it |
| Tasks | 11 tasks, plus an optional Gradio chat window |
| Discussion | Which mechanisms are used to improve performance |

## 2. The 11 tasks and what was done

| # | Lab sheet task | What was done |
|---|---|---|
| 1 | Load and explore the dataset: show stories, text length and structure | Downloaded the first part of the TinyStories files, kept 3000 training and 300 validation stories, displayed stories, and plotted length statistics |
| 2 | Select a subset and tokenize (characters or a tokenizer) | Cleaned special symbols, joined stories into one text, built a **character-level** vocabulary |
| 3 | Prepare input and target sequences for next-token prediction | Random blocks of 128 characters; the target is the input shifted by one character; batch size 32 |
| 4 | Build the Transformer architecture | Token and positional embeddings, masked multi-head self-attention, feed-forward layers, residual connections, layer normalization |
| 5 | Initialize the model, loss and optimizer | Normal(0, 0.02) weights, cross-entropy loss, AdamW optimizer |
| 6 | Train the model | Predict next characters, compute loss, backpropagate, update; 8 epochs of 100 steps |
| 7 | Monitor training | Recorded and plotted training and validation loss per epoch |
| 8 | Evaluate: validation loss and perplexity | Computed validation loss and perplexity |
| 9 | Generate stories from a prompt | Started from "Once upon a time" and other prompts, with temperature and top-k sampling |
| 10 | Experiment with layers, heads and epochs | Trained 4 variants and compared loss and generated text |
| 11 | Save the trained model | Saved the weights, configuration and vocabulary, then reloaded them to check |
| Optional | Chat window with Gradio | A small web page where you type a story start and get the generated text |

## 3. The model

**Settings of the main model**
| Setting | Value |
|---|---|
| Tokenizer | Character level |
| Block size (context) | 128 characters |
| Embedding size | 128 |
| Layers / heads | 4 / 4 |
| Dropout | 0.1 |
| Optimizer | AdamW, learning rate 1e-3, weight decay 0.01, gradient clipping 1.0 |
| Training | 8 epochs of 100 steps (batch size 32) |

**Architecture (decoder-only Transformer)**
1. **Token embeddings** turn each character into a vector.
2. **Positional embeddings** add the position of each character.
3. Each of the stacked **blocks** applies: LayerNorm, then **masked multi-head self-attention** (a position can look only at earlier characters), then a residual connection; then LayerNorm, a **feed-forward** network (GELU) and another residual connection.
4. A final LayerNorm and a linear layer give the scores for the next character.
5. The input embedding and the output layer **share weights** (weight tying).

## 4. Results

### Main training run
| Item | Value |
|---|---|
| Vocabulary size | 74 |
| Parameters | 819,200 |
| Initial loss (should be close to ln(vocab size)) | 4.304 |
| Final training loss | 1.4716 |
| Final validation loss | 1.4237 |
| Perplexity (per character) | 4.15 |



### Experiments (5 epochs each)
| Setting | Parameters | Validation loss | Perplexity |
|---|---|---|---|
| 1 layer, 4 heads | 224,384 | 1.7793 | 5.93 |
| 2 layers, 4 heads | 422,656 | 1.7361 | 5.67 |
| 4 layers, 1 head | 819,200 | 1.6563 | 5.24 |
| 4 layers, 4 heads | 819,200 | 1.7303 | 5.64 |

**What the experiments show**
- The lowest loss came from **4 layers with 1 head** (1.656, perplexity 5.24).
- **More layers helped:** with 4 heads, the loss fell from 1.779 (1 layer) to 1.736 (2 layers) to 1.730 (4 layers).
- **More heads did not help** in this test: 4 layers with 1 head did better than 4 layers with 4 heads. Each run was short and used one random start, so a gap of this size may be partly chance.
- Deeper models were slower per epoch (about 4 s for 1 layer and about 10 s for 4 layers on the GPU), but their loss fell faster in the later epochs.
- In every run, loss fell from about 2.3 at epoch 1 to about 1.7 to 1.8 at epoch 5, so more training reduced the loss.

### Generated text
*Once upon a time, there day named "You are! So said, are out some of the larke the the cat. He rab dog her and bet was friend and stilly all he will now his oned around but don the poorted in if to he caround. He downe the the the cots and Shelp the they all that it says, "I a a care you said in you. "I her aren yr*

## 5. Key concepts
| Concept | Meaning |
|---|---|
| Next-token prediction | The model reads a context and predicts the next character; training teaches it the patterns of the text |
| Character-level tokenization | One token per character; the vocabulary is small, but the model must learn spelling before meaning |
| Self-attention | Each position weighs the earlier positions to decide what matters |
| Masked (causal) attention | A mask hides future positions, so the model cannot see the answer |
| Multi-head attention | Several attention heads look at different relationships at once |
| Cross-entropy loss | How surprised the model is by the true next character; lower is better |
| Perplexity | e raised to the loss; here, per character. Random guessing equals the vocabulary size |
| Temperature | Low gives safe, repetitive text; high gives varied but messier text |
| Top-k sampling | Choose only among the k most likely next characters |

## 6. Mechanisms that improve performance (discussion task)
- **Token and positional embeddings:** give the model meaning and order, because attention alone ignores order.
- **Masked self-attention:** gives context from earlier characters while keeping next-token prediction fair.
- **Multi-head attention:** captures several kinds of relationships in parallel.
- **Feed-forward layers:** add non-linear processing after attention.
- **Residual connections:** let information and gradients flow through deep stacks.
- **Layer normalization:** keeps values stable, so training is faster and steadier.
- **Dropout and weight decay:** reduce overfitting.
- **AdamW and gradient clipping:** efficient and stable updates.
- **Weight tying:** fewer parameters.
- **Sampling settings (temperature, top-k):** improve generated text without changing the model.
- **More data, a larger model and more training:** lower the loss further.

## 7. Challenges and how they were solved
- On the local PC, `import pandas` and then `import torch` failed with "An Application Control policy has blocked this file". Windows security blocked the `pyarrow` and `torch` files.
- The Hugging Face `datasets` library needs `pyarrow`, so the notebook downloads the dataset text files directly instead.
- The notebook was run in **Google Colab with a GPU**, which also made training much faster.
- Results were downloaded from Colab (screenshots, the `results` folder and the notebook with outputs) before closing it, because Colab deletes its files.

## 8. Limitations
- A tiny model trained on a small subset for a short time gives short-range, often inconsistent stories.
- Each experiment was a single short run, so small differences may be due to chance.
- Perplexity here is per character and cannot be compared with word-level perplexity.

## 9. What was submitted
```
Lab-03-Tiny-Transformer/
├── README.md
├── notebooks/lab03_tiny_transformer.ipynb
└── results/
    ├── 01_dataset_stories.png ... 12_gradio.png   (output screenshots)
    ├── loss_curve.png
    ├── experiments_val_loss.png
    ├── experiments.csv
    └── saved_model/   (tiny_transformer.pt, config.json, vocab.json)
```

**Citation:** Eldan, R. and Li, Y. (2023). *TinyStories: How Small Can Language Models Be and Still Speak Coherent English?* arXiv:2305.07759.
