# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 22:26:31 2017

@author: Kirill
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import pandas as pd
import numpy as np


start = 1
end = 3
ko_0 = 0.3
ko_1 = 1.8
word_size = 1


def vectorizer(start, end):
    stop_w = stopwords.words('russian')
#    mass_vectorizer = CountVectorizer(ngram_range=(start, end),
#                                      token_pattern=r'\b\w\w\w+\b', stop_words=stop_w, use_idf=True)
    mass_vectorizer = TfidfVectorizer(
            ngram_range=(start, end),
            token_pattern=r'\b\w\w\w+\b',
            stop_words=stop_w,
            analyzer='word',
            use_idf=False)
#            use_idf=True)
    
    return mass_vectorizer


def freq_count(sem_dict):
    result_dict = dict()
    for key in sem_dict:
#        print(key)
        if sem_dict[key]:
            vect = vectorizer(start, end)
            vect.fit(sem_dict[key])
            for raw in sem_dict[key]:
#                print(raw)
                if raw:
                    if key in result_dict:
                        result_dict[key].append(dict(list(zip(list(vect.get_feature_names()), list(vect.transform([raw]).toarray()[0])))))
                    else:
                        result_dict[key] = [dict(list(zip(list(vect.get_feature_names()), list(vect.transform([raw]).toarray()[0]))))]
    return result_dict


def result_select(result_dict):
    result = dict()
    for key in result_dict:
        df = pd.DataFrame.from_records(result_dict[key], columns = result_dict[key][0].keys())
        total = df.apply(np.sum)
        std = total.std()
        median = total.median()
        mean = total.mean()
        print(std, mean, median)
        if std:
            if std < median:
                result[key] = [total[total > (mean + ko_0 * std)][total < (mean + ko_1 * std)].to_dict()]
            elif std >= median:
                result[key] = [total[total > (mean + ko_0 * std)][total < (mean + ko_1 * std)].to_dict()]
#            result[key] = [total[total > (mean - 1.5 * std)][total < (mean + 1.5 * std)].to_dict()]
        else:
            result[key] = result_dict[key]  
    return result


def one_word_clean(selected_dict):
    result_dict = dict()
    for key_url in selected_dict:
        for key_word in selected_dict[key_url][0]:
            if len(key_word.split()) > word_size:
                if key_url in result_dict:
                    result_dict[key_url][0][key_word] = selected_dict[key_url][0][key_word]
                else:
                    result_dict[key_url] = [{key_word: selected_dict[key_url][0][key_word]}]
    return result_dict


