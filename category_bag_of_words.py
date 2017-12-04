# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 16:15:31 2017

@author: User
"""

import requests
from lxml import html
import urllib
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import csv

sitemap_url = 'https://besplatka.ua/sitemap.xml'
controls = ['/electronika-i-bitovaya-tehnika/smartfone-telefone']
start = 1
end = 3
ko_0 = 0.3
ko_1 = 1.8
word_size = 1


def get_url_sitemap(sitemap_url):
    res = requests.get(sitemap_url)
    sub_res = html.fromstring(res.content).xpath('//sitemap/loc/text()')
    return sub_res


def get_url_final(sitemap_url):
    res = requests.get(sitemap_url)
    sub_res = html.fromstring(res.content).xpath('//url/loc/text()')
    return sub_res


def url_list_in_sitemap(sitemap_url):
    res_sitemap = set()
    for url_sm in get_url_sitemap(sitemap_url):
        if '-categories-' in url_sm:
            for url_final in get_url_final(url_sm):
                res_sitemap.add(
                        urllib.parse.unquote(urllib.parse.unquote(url_final))
                        )
        elif '/sitemap-besplatka' in url_sm:
            for url_final in get_url_final(url_sm):
                res_sitemap.add(
                        urllib.parse.unquote(urllib.parse.unquote(url_final))
                        )          
    return res_sitemap


def tags_to_string(header_tag):
    string = ''
#    print(len(header_tag))
    if len(header_tag) > 1:
        for tag in header_tag:
            if len(tag.strip()) > 5:
                string += str(tag).strip() + ' '
            else:
                string += 'no_tag_ '
#        print(string)
        return string
    elif len(header_tag) == 1:
        if len(header_tag[0].strip()) > 5:
            string = str(header_tag[0].strip())
        else:
            string = 'no_tag '
        return string.strip()
    elif len(header_tag) == 0:
        string = 'no_tag '
        return string.strip()


def get_ads_title(parsed_body):
    '''
    Получаем заголовки объявлений
    из категории
    '''
    try:
        ads_title = parsed_body.xpath('//div[@class="title"]/a/text()')
#        print(tags_to_string(ads_title))
    except:
        ads_title = ['no ads at all']
#        print(tags_to_string(ads_title))
#    return tags_to_string(ads_title)
    print(type(ads_title))
    return ads_title


def page_tags(parsed_body):
    print(get_ads_title(parsed_body))
    return get_ads_title(parsed_body)


def srap_page(page_url):
    response = requests.get(page_url)
    parsed_body = html.fromstring(response.text)
    return page_tags(parsed_body)


def semantica_graber(url_list, controls):
    res_dict = dict()
    for url in url_list:
        for control in controls:
            if control in url:
                if url in res_dict:
                    res_dict[url].append(srap_page(url))
                else:
                    res_dict[url] = srap_page(url)
    return res_dict


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
                
        
def write_to_file(selected_dict):
    with open("output_keywords.csv","a",newline="") as f:
        cw = csv.writer(f)
        for key in selected_dict:
            if selected_dict[key][0]:
                cw.writerow([key])
                print(key)
                for key_1, value_1 in selected_dict[key][0].items():
                    cw.writerow([key_1, value_1])
        
    
if __name__ == '__main__':
    
    url_set = url_list_in_sitemap(sitemap_url)
    sem_dict = semantica_graber(url_set, controls)
    result_dict = freq_count(sem_dict)
    selected_dict = result_select(result_dict)
    write_to_file(one_word_clean(selected_dict))
    
#    print(len(result_dict))


#    result_dict = dict()
#
#    for key in sem_dict:
#        vect = vectorizer(start, end)
#        vect.fit(sem_dict[key])
#        for raw in sem_dict[key]:
#            if key in result_dict:
#                result_dict[key].append(dict(list(zip(list(vect.get_feature_names()), list(vect.transform([raw]).toarray()[0])))))
#            else:
#                result_dict[key] = [dict(list(zip(list(vect.get_feature_names()), list(vect.transform([raw]).toarray()[0]))))]