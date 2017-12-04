# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 09:07:23 2017

@author: User
"""

import urllib
import requests
from lxml import html
import numpy as np
import csv
import re
import pymorphy2


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN


sitemap_url = 'https://besplatka.ua/sitemap.xml'
path_to_file = 'Data/search_on_site.csv'
path_to_result = 'Data/scored_keywords.csv'
path_to_result_clusters = 'Data/ready_clusters.csv'


def read_data(path_to_file):
    with open(path_to_file) as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            yield row


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
        if '-search-' in url_sm:
            for url_final in get_url_final(url_sm):
                res_sitemap.add(
                        urllib.parse.unquote(urllib.parse.unquote(url_final))
                        )
    return res_sitemap


def clean_key_6(line_6):
    '''чистим два варианта "бу" -б-у- -б,у- -б.у- и -б/у- в середине запроса'''
    trouble_to_change = [' б-у ', ' б/у ', ' б,у ', ' б.у ', ' б\у ']
    for trouble in trouble_to_change:
        pattern = re.compile(trouble, re.IGNORECASE)
        line_6 = re.sub(pattern, ' бу ', line_6)
    return line_6


def clean_key_7(line_7):
    '''чистим варианты бу вначале строки б-у- б,у- б.у- б\у- и б/у-'''
    trouble_to_change = [
            '^(б-у )', '^(б,у )', '^(б.у )', '^(б/у )', '^(б\у )', '^(б.у. )',
            '^(б.у.)', '^(б-/-у )'
            ]
    for trouble in trouble_to_change:
        pattern = re.compile(trouble, re.IGNORECASE)
        line_7 = re.sub(pattern, 'бу ', line_7)
    return line_7


def clean_key_8(line_8):
    '''чистим варианты бу в конце строки -б-у -б,у -б.у -б\у и -б/у'''
    trouble_to_change = [
            '( б-у)+$', '( б,у)+$', '( б.у)+$', '( б--у)+$', '( б\у)+$',
            '( б/у)+$', '( б.у.)+$', '( б-у)+$'
            ]
    for trouble in trouble_to_change:
        pattern = re.compile(trouble, re.IGNORECASE)
        line_8 = re.sub(pattern, ' бу', line_8)
    return line_8


def clean_key_9(line_9):
    '''Проверяем входящий запрос/ключ на ситуации типа "r-r-r-r" или "k-k"
    'eeeeeeee', '11111111' '''
    if len(line_9.split(' ')) == 1:
        if len(set(line_9)) >= 1:
            return line_9
    elif len(set(line_9.split(' '))) != 1:
        return line_9
    elif len(set(line_9.split(' '))) == 1:
        return line_9.split(' ')[0]


def clean_key_10(line_10):
    '''чистим разделители в строке отличные от '-' все что другое заменяем
    на установленный формат разделителя'''
    print(line_10)
    trouble_to_change = ['\\', '/', '.', ',', '*', ':', ';']
    for trouble in trouble_to_change:
        if trouble in line_10:
            line_10 = line_10.replace(trouble, ' ')
        else:
            continue
    return line_10


def clean_key_11(line_11):
    '''Удаляем последний набор букв из запроса/ключа, если он принадлежит
    данному списку т.к. это предлог, который не несет значимой нагрузки
    в данной задаче'''
    garbige_list = [
            'в', 'на', 'под', 'у', 'к', 'с', 'над', 'от', 'по', 'до',
            'из-за', 'из-под', 'по-над', 'по-за', 'вдоль', 'ввиду', 'о', 'за',
            'а', 'но', 'и', 'что', 'если', 'как', 'когда', 'будто', 'потому',
            'прежде', 'чем', 'то', 'из', 'вокруг', 'мимо', 'между', 'около',
            'перед', 'через', 'поперёк', 'среди', 'против', 'подле', 'возле',
            'близ',	'вне', 'внутри', 'сквозь', 'накануне', 'благодаря',
            'вследствие', 'для', 'ради', 'без', 'насчёт', 'об',	'про', 'не',
            'нет'
            ]
    if '-' in line_11:
        if line_11.split(' ')[-1:][0] in garbige_list:
            return '-'.join(line_11.split('-')[:-1])
        else:
            return line_11
    else:
        return line_11


def clean_keyword(word):
    keyword = clean_key_11(
            clean_key_10(
                    clean_key_9(clean_key_8(clean_key_7(clean_key_6(word))))))
    return keyword


def get_query(stroka):
    '''
    Возвращает запрос из урл типа /q-
    '''
#    print(clean_keyword(stroka[stroka.find('/q-')+len('/q-'):]), stroka)
    return clean_keyword(
            stroka[stroka.find('/q-')+len('/q-'):]
            ).replace('+', ' ')


def get_url(stroka):
    '''
    Возвращает урл без запроса из урл типа /q-
    '''
    return stroka[:stroka.find('/q-')]


def get_keywords(sitemap_url):
    '''
    Возвращает список запросов из сайтмапа
    в полном объеме
    '''
    res_list_keys = list()
    url_dict = url_list_in_sitemap(sitemap_url)
    for url in url_dict:
        res_list_keys.append(get_query(url).replace('+', ' '))
    return res_list_keys


def get_keywords_1(sitemap_url):
    '''
    Возвращает список запросов из сайтмапа
    как ключей из словаря запрос - урл с запросом
    '''
    res_list_keys = list()
    res_dict_keys = dict()
    url_dict = url_list_in_sitemap(sitemap_url)
    for url in url_dict:
        if get_query(url).replace('+', ' ') in res_dict_keys:
            res_dict_keys[get_query(url).replace('+', ' ')].append(url)
        else:
            res_dict_keys[get_query(url).replace('+', ' ')] = [url]
    res_list_keys = list(res_dict_keys.keys())
    return res_list_keys, res_dict_keys


def data_get_from_file(path_to_file):
    res_dict = dict()
    file = read_data(path_to_file)
    for line in file:
        print(line[0])
        index = get_query(line[0])
        text = get_url(line[0])
        if index in res_dict:
            res_dict[index].append(text)
        else:
            res_dict[index] = [text]
    return res_dict


def labled_get_result(res_keys_1):
    vect = TfidfVectorizer()
    cls = DBSCAN(eps=0.8, min_samples=5)
    res_lables = cls.fit_predict(vect.fit_transform(np.array(res_keys_1)))
    pairs = list(zip(res_keys_1, res_lables.tolist()))
    labled = dict()
    for pair in pairs:
        if pair[1] in labled:
            labled[pair[1]].append(pair[0])
        else:
            labled[pair[1]] = [pair[0]]
    return labled


def pymorphy_score(labled):
    pymorphy_res = []
    morph = pymorphy2.MorphAnalyzer()
    for ind in range(0, len(labled) - 1):
        classter_list = labled[ind]
        score_max = 0
        word_max = ''
        for word in classter_list:
            if morph.parse(word)[0][3] > score_max:
                score_max = morph.parse(word)[0][3]
                word_max = morph.parse(word)[0][0]
        pymorphy_res.append([word_max, score_max])
        print(word_max, score_max)
    return pymorphy_res


def get_sitemap_data(sitemap_url):
    res_keys = get_keywords_1(sitemap_url)[0]
    labled = labled_get_result(res_keys)
    scored_results = pymorphy_score(labled)
    return labled, scored_results


def get_file_data(path_to_file):
    res_dict = data_get_from_file(path_to_file)
    res_keys_1 = list(res_dict.keys())
    labled = labled_get_result(res_keys_1)
    scored_results = pymorphy_score(labled)
    return labled, scored_results


def write_to_file(scored, path_to_result):
    with open(path_to_result, 'a') as out:
        csv_out = csv.writer(out, dialect='excel')
        csv_out.writerow(['keywords', 'pymorphy_score'])
        for row in scored:
            csv_out.writerow(row)


def write_to_file_dict(labled, path_to_result):
    with open(path_to_result, 'a') as out:
        csv_out = csv.writer(out, dialect='excel')
        csv_out.writerow(['Mark', 'Keyword'])
        for key in labled:
            for raw in labled[key]:
                csv_out.writerow([key, raw])


if __name__ == '__main__':
#    labled, scored = get_sitemap_data(sitemap_url)
    labled, scored = get_file_data(path_to_file)
    write_to_file(scored, path_to_result)
    write_to_file_dict(labled, path_to_result_clusters)


#    res_keys = get_keywords(sitemap_url)
#    res_keys_1 = res_keys[:60000]
#    res_dict = data_get_from_file(path_to_file)
#    res_keys_1 = list(res_dict.keys())
#    labled = labled_get_result(res_keys_1)
#    scored_results = pymorphy_score(labled)
