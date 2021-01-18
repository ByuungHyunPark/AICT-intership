### Fake News Challenge(FNC))
- baseline 코드 리뷰 (2020/12/28)
- www.fakenewschallenge.org
- https://github.com/FakeNewsChallenge
---
# Feature Engineering

```python
X_overlap = word_overlap_features(h, b)
X_refuting = refuting_features(h, b)
X_polarity = polarity_features(h, b)
X_hand = hand_features(h, b)

X = np.c_[X_overlap, X_refuting, X_polarity, X_hand]
```


##### 1. word_overlap_features 
- Jaccard Similarity
- 본문과 내용 단어 겹치는 정도를 나타냄(1차원)
```python
def word_overlap_features(headlines, bodies):
    X = []
    for i, (headline, body) in tqdm(enumerate(zip(headlines, bodies))):
        clean_headline = clean(headline)
        clean_body = clean(body)
        clean_headline = get_tokenized_lemmas(clean_headline)
        clean_body = get_tokenized_lemmas(clean_body)
        
        intersection = set(clean_headline).intersection(clean_body)
        union = set(clean_headline).union(clean_body)
        
        features = [
            len(intersection) / float(len(union))]
        X.append(features)
    return X
```
__example)__ : 자카드 유사도와 동일
|word_overlap_feature|
|:--:|
|0.0055|
|0.0337|
|0.0243|
|0.0172|
|0.0398|

##### 2. refuting_features (15차원)
- 기사 헤드라인이 refuring words 15개에 포함 여부
```python
def refuting_features(headlines, bodies):
    _refuting_words = [
        'fake',
        'fraud',
        'hoax',
        'false',
        'deny', 'denies',
        # 'refute',
        'not',
        'despite',
        'nope',
        'doubt', 'doubts',
        'bogus',
        'debunk',
        'pranks',
        'retract'
    ]
    X = []
    for i, (headline, body) in tqdm(enumerate(zip(headlines, bodies))):
        clean_headline = clean(headline)
        clean_headline = get_tokenized_lemmas(clean_headline)
        features = [1 if word in clean_headline else 0 for word in _refuting_words]
        X.append(features)
    return X
```
|fake|fraud|hoax|false|deny|denies|not|despite|nope|doubt|doubts|bogus|debunk|pranks|retract|
|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|
|0|0|0|0|0|0|0|0|0|0|0|0|0|0|0|
|1|0|0|0|0|0|0|0|0|0|0|0|0|0|0|

##### 3. polarity_features (2차원)
- headline 긍정/부정
- body 긍정/부정
```python
def polarity_features(headlines, bodies):
    _refuting_words = [
        'fake',
        'fraud',
        'hoax',
        'false',
        'deny', 'denies',
        'not',
        'despite',
        'nope',
        'doubt', 'doubts',
        'bogus',
        'debunk',
        'pranks',
        'retract'
    ]

    def calculate_polarity(text):
        tokens = get_tokenized_lemmas(text)
        return sum([t in _refuting_words for t in tokens]) % 2

    X = []

    for i, (headline, body) in tqdm(enumerate(zip(headlines, bodies))):
        clean_headline = clean(headline)
        clean_body = clean(body)
        features = []
        features.append(calculate_polarity(clean_headline))
        features.append(calculate_polarity(clean_body))
        X.append(features)
    return np.array(X)
```
|headline_polarity|body_polarity|
|--|--|
|0|0|
|1|0|
|1|1|


##### 4. hand_features
- __binary_co_occurence__ (2차원) 
    - 동시 등장
    - Count how many times a token in the title
    - appears in the body text.
- __binary_co_occurence_stops__ (2차원) 
    - Count how many times a token in the title
    - appears in the body text. 
    - Stopwords in the title are ignored.

|co-Count|co-Count-early[:255]|co-Count-stop|co-Count-stop-early[:255]|
|:--:|:--:|:--:|:--:|
|2|2|1|1|

- __count_grams__ (22차원)
    - Count how many times an n-gram of the title
    - appears in the entire body, and intro paragraph
    1. chargrams (3차원 * 4)
        - __grams_hits__ : text_body
        - __grams_early_hits__ : [:255]
        - __grams_first_hits__ : [:100]
    2. ngrams (2차원 * 5)
        - __grams_hits__ 
        - __grams_early_hits__  [:255]
- 2 + 2 + 22 = __26 차원__
```python
def hand_features(headlines, bodies):

    def binary_co_occurence(headline, body):
        # 헤드라인이 본문에 포함되는 단어의 수
        # Count how many times a token in the title
        # appears in the body text.
        bin_count = 0
        bin_count_early = 0
        for headline_token in clean(headline).split(" "):
            if headline_token in clean(body):
                bin_count += 1
            if headline_token in clean(body)[:255]:
                bin_count_early += 1
        return [bin_count, bin_count_early]

    def binary_co_occurence_stops(headline, body):
        # stopword 를 제외한 동시 등장 단어
        # Count how many times a token in the title
        # appears in the body text. Stopwords in the title
        # are ignored.
        bin_count = 0
        bin_count_early = 0

        for headline_token in remove_stopwords(clean(headline).split(" ")):
            if headline_token in clean(body):
                bin_count += 1
                bin_count_early += 1
        return [bin_count, bin_count_early]

    def count_grams(headline, body):
        # Count how many times an n-gram of the title
        # appears in the entire body, and intro paragraph

        clean_body = clean(body)
        clean_headline = clean(headline)
        features = []
        features = append_chargrams(features, clean_headline, clean_body, 2)
        features = append_chargrams(features, clean_headline, clean_body, 8)
        features = append_chargrams(features, clean_headline, clean_body, 4)
        features = append_chargrams(features, clean_headline, clean_body, 16)
        features = append_ngrams(features, clean_headline, clean_body, 2)
        features = append_ngrams(features, clean_headline, clean_body, 3)
        features = append_ngrams(features, clean_headline, clean_body, 4)
        features = append_ngrams(features, clean_headline, clean_body, 5)
        features = append_ngrams(features, clean_headline, clean_body, 6)
        return features

    X = []
    for i, (headline, body) in tqdm(enumerate(zip(headlines, bodies))):
        X.append(binary_co_occurence(headline, body)
                 + binary_co_occurence_stops(headline, body)
                 + count_grams(headline, body))

    return X
```

ex) 
|co-Count|co-Count-early[:255]|co-Count-stop|co-Count-stop-early[:255]|
|:--:|:--:|:--:|:--:|
|2|2|1|1|

---
# Modeling
- K-Fold (k = 10)
- GradientBoostingClassifier
- __Scoring is as follows:__
  - +0.25 for each correct `unrelated`
  - +0.25 for each correct related (label is any of `agree`, - `disagree`, `discuss`)
  - +0.75 for each correct agree, disagree, discuss


  동해물과 백두산이 마르고 닳도록 하느님이 보우하사 우리나만세

- 동해물과 백두산이
- 백두산이 마르고
