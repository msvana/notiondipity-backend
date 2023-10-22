# Working with arbitrary sources

# Interesting functions and methods

- `nltk.word_tokenize()`
- `nltk.clean_html()` I can also use BS4 for this
- `feedparser` - a library for parsing RSS feeds
- `nltk.Index()` - can create indices and inverted indices for quick lookup of information based on its contents
- `nltk.Text.findall()` - works well with regular expressions

# Regular expressions cheat-sheet

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/92b6f967-388d-4faa-b336-e652fd2e2d1e/Untitled.png)

# Text normalization

Making text lowercase is a form of normalization. Normalization can be understood as making certain tokens look the same. Other common forms of normalization include stemming and lemmatization.

## Stemming

Stemming means removing affixes from words. NLTK offers a `PorterStemmer` and `LancasterStemmer`. One interesting use case for stemming is indexing when we want to group various forms of the same word together.

## Lemmatization

Lemmatization on the other hand transforms a token into its standard dictionary form. It’s more complex than stemming.

---

In many use cases it’s important to detect non-standard words such as abbreviations

# Tokenization

Tokenization means splitting text into some smaller units such as words. NLTK offers multiple different tokenizers such such as `Punkt` or `regexp_tokenize`.

No tokenizer is perfect. One way to evaluate the quality of a tokenizer is by comparing the tokenization results to a standard dictionary.

Sometimes we also need to deal with abbreviations such as “n’t”. This is traditionally done by using lookup tables. 

NLTK also offers tools for Sentence segmentation which is a problem similar to tokenization.

# Word segmentation

When working with some languages or audio recordings you might need to segment a stream of characters into individual words. The solution to such problem can be represented as a string of bits where 1 means that there is a split after a given position.

We can define an objective function to minimize as a sum of the total length of unique words in the extracted dictionary and the total number of segments found. 

Simulated annealing can be then used to solve this optimization problem.

# String formatting in Python

When using formatting strings I can apply the following:

```python
f'{name:[justification][witdh][.precision][type]}'
```

Justification can be either `<` or `>`.
