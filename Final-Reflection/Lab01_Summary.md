# Lab 1 Summary: Sentiment Analysis Using Traditional Machine Learning

**Module:** PUSL3205 Large Language Models and Generative AI

## 1. Lab sheet at a glance
| Item | Details |
|---|---|
| Title | Sentiment Analysis Using Traditional Machine Learning |
| Objective | Practise basic NLP tasks |
| Topic | Text preprocessing, TF-IDF and machine learning |
| Duration | 1 hour |
| Language | Python |
| Libraries | Pandas, NumPy, NLTK, Scikit-learn, Matplotlib, Seaborn |
| Dataset | UCI *Sentiment Labelled Sentences* (Kotzias et al., KDD 2015) |

**Dataset:** 3000 sentences from Amazon, IMDb and Yelp reviews. There are 1000 per website (500 positive, 500 negative), so 1500 positive (label 1) and 1500 negative (label 0) in total. Each line is `sentence <tab> score`.

## 2. The 8 tasks and what was done

### Task 1: Download and load the dataset
- Read the three `.txt` files with `pd.read_csv(..., sep='\t', names=['text','label'], quoting=3)`.
- Added a `source` column (amazon, imdb, yelp) and combined them into one DataFrame.
- **Result:** shape (3000, 3), with 1500 negative and 1500 positive sentences.

### Task 2: Basic text preprocessing
Requirements: lowercase, remove punctuation and unnecessary characters, remove extra whitespace, create a clean-text column, compare original and cleaned text.

A `clean_text()` function:
1. converts to lowercase,
2. expands contractions so negation survives (`didn't` becomes `did not`, `won't` becomes `will not`),
3. removes punctuation, digits and symbols with a regular expression,
4. removes extra whitespace.

The output is stored in `df['clean_text']`. Example: `Wow...   I didn't like it!!  It's NOT 100% GREAT :)` becomes `wow i did not like it its not great`.

### Task 3: Explore the text data
- Displayed random positive and negative examples.
- Plotted the class balance (two equal bars of 1500).
- Counted the 15 most frequent words per class (stopwords removed for the charts only).
- Compared words shared by both classes with words found in only one class.
- Compared sentence length per class.

**Findings**
- Positive words: *great* (201), *good* (178), *best*, *love*, *excellent*.
- Negative words: *bad* (100), then *terrible*, *worst*, *waste*, *disappointed*, *never*.
- Shared words (*movie, film, phone, food, place, service*) describe the topic, not the sentiment.
- Average length: 11.99 words (negative) and 11.82 words (positive), almost the same.
- *good* appears in 53 negative sentences, but only 13 contain "not good". The rest have other negation or contrast, which shows that counting single words ignores context.

### Task 4: Split the dataset
`train_test_split(test_size=0.2, random_state=42, stratify=y)` gave **2400 training** and **600 test** sentences, with 1200 of each class in the training set.

### Task 5: Bag-of-Words (BoW) representation
- `CountVectorizer(max_features=5000)` turns each sentence into word counts.
- Fitted on the **training data only**, then applied to the test data, to avoid data leakage.
- Stopwords were **not** removed, so negation words ("not", "no") stay in the vocabulary.
- **Result:** matrix of shape (2400, 4504) for training and (600, 4504) for testing.

### Task 6: Train a machine learning model
Two models trained on the BoW features: **Logistic Regression** (`max_iter=1000`) and **Linear SVM** (`LinearSVC`).

### Task 7: Evaluate the models
Metrics on the 600 unseen test sentences:

| Model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Logistic Regression | 0.8217 | 0.7988 | 0.8600 | 0.8283 |
| Linear SVM | 0.8017 | 0.7751 | 0.8500 | 0.8108 |

Precision, recall and F1 are for the positive class. A confusion matrix was drawn for each model.

**What the results show**
- Logistic Regression was slightly better on every metric. With only 600 test sentences, a 2-point gap is small.
- Both models predicted "positive" too often: recall (0.85 to 0.86) was higher than precision (0.78 to 0.80), and negative-class recall was lower (0.78 and 0.75).

**Error analysis**
- "the battery life is highly unacceptable" was predicted Positive because *unacceptable* never appears in the training data.
- "kind of disappointed" was predicted Positive, probably because "gold standard" appears in the same sentence.
- "never had anything to complain about here" is positive but was predicted Negative, because *never* and *complain* are usually negative words.
- Indirect complaints (such as "it also took her forever to bring us the check") have no clear negative words.

### Task 8: Test with new sentences
A `predict_sentiment()` function cleans a sentence, converts it with the trained vectorizer and predicts the label.

| Sentence | LR | SVM |
|---|---|---|
| I absolutely loved this movie, the acting was fantastic! | Positive | Positive |
| The food was cold and the service was terrible. | Negative | Negative |
| This phone has a great battery but the screen is awful. | Positive | Positive |
| Not good at all. | Negative | Negative |
| I wouldn't recommend this to anyone. | Negative | Negative |
| It was okay, nothing special. | Negative | Negative |
| The delivery was fast and the quality is excellent. | Positive | Positive |

Clear and negated sentences were correct. The **mixed** sentence was predicted Positive, and the **neutral** sentence was forced into Negative. Only 7 sentences were tested, so this is weak evidence.

## 3. Key concepts
| Concept | Meaning |
|---|---|
| Preprocessing | Cleaning text (lowercase, no punctuation) to reduce noise; it also loses some signals such as "!!!" |
| Bag-of-Words | Each sentence becomes a vector of word counts; word order and context are ignored |
| TF-IDF | A variant that down-weights very common words (named in the lab title; the notebook used simple counts) |
| Train/test split | Learn from one part of the data, test on unseen data |
| Data leakage | Using test information during training; avoided by fitting the vectorizer on training data only |
| Accuracy | Share of all predictions that are correct |
| Precision | Of the sentences predicted positive, how many really are positive |
| Recall | Of the truly positive sentences, how many were found |
| F1 | The balance of precision and recall |
| Confusion matrix | Counts of true and false positives and negatives |

## 4. Limitations of Bag-of-Words
No word order, no context, trouble with negation, contrast and sarcasm, mixed or neutral sentiment, and unknown words. These limits motivate contextual models such as transformers and LLMs later in the module.

## 5. Problems met and how they were solved
- `FileNotFoundError` when loading the data: Jupyter was looking in a different folder, so the files were moved into a `data` folder and the path was set correctly.
- The scikit-learn stopword list removes "not" and "no", so it was not used for the model.
- The notebook was reorganised into `data`, `notebook` and `screenshots` folders for GitHub.

## 6. What was submitted
```
Lab-01-Machine-Learning/
├── README.md       Objective, Tasks, Results, Observations, Learning Outcomes
├── data/           the 3 dataset files
├── notebook/       lab01.ipynb
└── screenshots/    15 output screenshots
```

**Citation:** Kotzias, D., Denil, M., de Freitas, N. and Smyth, P. (2015). *From Group to Individual Labels using Deep Features.* KDD 2015.
