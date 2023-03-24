# Notes

This notes are extracted from my original Colab's notebook

## Datasets

1. `hackernews-urls-from-browser-deduplicated.csv`  
    Deduplicated urls from my most recent browser session  
    most recent date: 2022-10-16 15:20:47
2. `hackernews-data-from-phone.json`  
    Urls from my phone. Still has one `poll` type data (easily filtered)  
    most recent date: 2022-10-11 23:20:45
3. `hackernews-stories-since-2018.csv`
    HN stories data since 2018. Dumped from BQ public dataset  
    most recent date: 2022-10-14 00:01:15+0000
4. `hackernews-stories-since-2022-10-14.csv`  
    Additional HN data for (3) should be used along with the test case (5)  
    most recent date: 2022-10-24 23:54:08
5. `hackernews-since-20221016`  
    Urls of the articles I've most recently opened (since 2022-10-16) should be used as test case
6. `hackernews-2019-2022-sessions.csv`  
    Deduplicated urls from my stored browser session (it's longer)

There are basically two dataset: the `Joined` dataset from a `set(1 + 2 + 5 + 6)` and `HN` dataset (`since 2018` (3) the first one I dumped and `since 20221014` (4) the most recent dump)

- Models are created using data from (3)
- Joined are split between before October 14 (4 `min()`) and after that
- Profile building are done using data from before October 14
- Validation are done using data after October 14

## Queries

```sql
SELECT title, url, timestamp, type, id
FROM `bigquery-public-data.hacker_news.full`
WHERE
    type = 'story'AND
    title IS NOT NULL AND
    timestamp BETWEEN 'START_DATE' AND 'END_DATE'  -- YYYY-MM-DD format
    -- or could be
    -- timestamp >= DATE_STRING
```

## Processes

1. There are titles with different language included in the training set, like Spanish and Indonesian. I don't remove them because they don't amount to much and I don't think I have a good way to identify them. I've tried [langdetect][Language Detection], but it doesn't work well with short texts :/
2. Apparently I don't have to create my own sentence transformer embeddings because BERTopic by default uses it. Also, stop words are automatically handled by the vectorizer in my case
3. BERTopic `cachedir` issues (coming from HDBSCAN) [1][Cachedir Issue 1] [2][Cachedir Issue 2].  
   Solved by installing HDBSCAN first before installing BERTopic as, *"If you install this dependency before running pip install it won't install it again. This means to you can install your patched version and then your package:"* -- [SO link][Cachedir SO]
4. BERTopic finished training, but crashes as it process the result.  
   I tried playing with parameters such as `min_df` and `low_memory` but they doesn't help. So, I tried [online topic modeling][Online Topic Modeling]. Tried River, but it's too slow. The IncrementalPCA and BatchKMeans works nicely for my case (and it doesn't take too long!)
5. As I'm using online modeling, the topics learned are somehow not sorted correctly. This breaks the visualization mechanism of BERTopic (that's why the README is lacking in visualizations). It's probably easily to solve: sort the topics along with the sentence and feed the result back to the `topic_model`. But, I haven't tried this!
6. Using Kaggle and Colab interchangeably because of GPU restrictions (also, good news from [Kaggle][Kaggle Good News])
7. Colab's CPU and GPU environment different `gdown` version breaks my path to Drive. Needs to anticipate for this
8. Some library that I wanted to try (I think it's cuML) needed python version above 3.7, but the python installed in Colab and Kaggle are 3.7 :(
9. Lemmatizations (in my intuition) made the model better
10. Somehow the `ngram` when first applied doesn't really work for me. Maybe because the sentence are too short?
11. I've had issue installing BERTopic in Colab. Apparently, the transformer must be with the specific `4.20.1` version and the flag `--upgrade-strategy only-if-needed` must be passed when installing BERTopic
12. I've created 10 models, and three that are good are with settings of:
  - 30 components, 100 clusters, 0.646 coherence score
  - 60 components, 200 clusters, 0.653 coherence score
  - 200 components, 300 clusters, 0.662 coherence score  
  Despite the drawbacks of coherence score as mentioned [here](Perplexity), these three are nicely matched with my intuition. They go from big picture (100) to specific (300). Results are in README

## Further Improvements

1. Try to visualize more stuffs and try to understand what happened (I'm not good with visualizations...)
2. The result from testing the model are good profile-wise, but not really matched to my taste. I've only got a little testing dataset with me, but it have the accuracy of 0.012 (12 per 1000). To resolve this issue, I think I could either:
    1. Tune the hyperparameter and focus on what's match with the end testing dataset.
    2. Use other aggregation and weighting mechanism for the profile.
    3. Use the output from BERTopic as a feature for another model (try to get the "middle" point where my taste is located).
3. Identify weird clusters and find a way to clear them
4. Use more data (use all the data in the public dataset)
5. Migrate the project to Kedro so that the workflow are much more clean (plus try experiment tracking tools like MLFlow)
6. Implement BTM and Top2Vec to compare the result
7. Try to solve OOV(s) in case it does happen
8. Use [perplexity][Perplexity] based measure in addition to coherence score (Another [example][Naive LDA])

## Useful References

1. Time
    1. [Python time format reference](https://strftime.org/)
    2. [UNIX timestamp to datetime](https://stackoverflow.com/questions/3682748/converting-unix-timestamp-string-to-readable-date)
2. [Colab's super feature!](https://www.youtube.com/watch?v=rNgswRZ2C1Y)
3. Short-text topic modeling:
    1. [Biterm Topic Model](https://github.com/maximtrp/bitermplus)
    2. [Top2Vec](https://github.com/ddangelov/Top2Vec)
    3. [BERTopic](https://github.com/MaartenGr/BERTopic)
4. [Limitations of short-text topic modeling](https://lazarinastoy.com/topic-modelling-limitations-short-text/)
5. Extra NLP Stuff
    1. [Kaggle's NLP](https://www.kaggle.com/learn-guide/natural-language-processing)
    2. [NLP Specializations](https://www.coursera.org/specializations/natural-language-processing)
6. OOV(s)
    1. [Various ways to handle it](https://ychai.uk/notes/2019/03/08/NLP/How-to-handle-Out-Of-Vocabulary-words/)
    2. [Byte Pair Encoding](https://www.youtube.com/watch?v=zjaRNfvNMTs&list=PL98nY_tJQXZk-NeS9jqeH2iY4-IvoYbRC&index=3)
7. Good notebook examples
    1. [BERTopic notebooks are great!](https://github.com/MaartenGr/BERTopic#getting-started)
    2. [BERTopic for covid-related tweets](https://www.kaggle.com/code/accountstatus/analysis-using-bertopic-and-sentence-transformer/notebook)

[//]: # (Links)

[Language Detection]: https://github.com/Mimino666/langdetect
[Cachedir Issue 1]: https://discuss.huggingface.co/t/typeerror-in-importing-bertopic-from-bertopic/24143
[Cachedir Issue 2]: https://github.com/scikit-learn-contrib/hdbscan/commit/ccd8535d3db241398afa9299cd279c4cd85133f5
[Cachedir SO]: https://stackoverflow.com/a/55109747/8996974
[Online Topic Modeling]: https://maartengr.github.io/BERTopic/getting_started/online/online.html
[Kaggle Good News]: https://www.kaggle.com/product-feedback/361104
[Perplexity]: https://pahulpreet86.github.io/standard-metrics-for-lda-model-comparison/
[Naive LDA]: https://alvinntnu.github.io/NTNU_ENC2045_LECTURES/nlp/topic-modeling-naive.html

