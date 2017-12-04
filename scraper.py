# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 21:13:26 2017

@author: Kirill
"""


import csv
import requests
from lxml import html
from transport import url_list_in_sitemap
from res_count import freq_count
from res_count import result_select
from res_count import one_word_clean



sitemap_url = 'https://besplatka.ua/sitemap.xml'
page_limit = 20


def urls_to_scrap(sitemap_url):
    '''
    Получаем из сайтмап список урл
    страниц для сбора текстов
    заголовков объявлений
    '''
    res = url_list_in_sitemap(sitemap_url)
    return res


def check_page_numbers(url):
    '''
    Определяем сколько всего страниц в категории
    '''
    res = requests.get(url)
    sub_res = html.fromstring(res.content).xpath('//li[@class="last"]/a/text()')
    if len(sub_res):
        return int(sub_res[0])
    else:
        return 0
    
    
def gen_new_url(url, number):
    '''
    Генерим все урл страниц в категории
    '''
    result = list()
    result.append(url)
    for item in range(2, number + 1):
        result.append(url + '/page/' + str(item))
    if len(result):
        return result
    else:
        return []
        

def get_ads_title(parsed_body):
    '''
    Получаем заголовки объявлений
    из одной страницы категории
    из текста страницы
    '''
    try:
        ads_title = parsed_body.xpath('//div[@class="title"]/a/text()')

    except:
        ads_title = ['no ads at all']

    return ads_title


def page_tags(parsed_body):
    '''
    Печатаем в консоль заголовки объявлений
    на обрабатываемой странице
    '''
#    print(get_ads_title(parsed_body))
    
    return get_ads_title(parsed_body)


def srap_page(page_url):
    '''
    По списку урл получаем текст страницы
    возвращаем лист заголовков на ней
    '''
    response = requests.get(page_url)
    parsed_body = html.fromstring(response.text)
    
    return page_tags(parsed_body)


def ads_title_graber(url_list):
    '''
    Собираем тексты заголовков по всем страницам
    категории из входного списка страниц
    '''
    res_list = list()
    for url in url_list:
        res_list = res_list + srap_page(url)
        
    return res_list


def pagination_limits(pages, page_limit):
    '''
    ограничитель страниц пагинации
    для скраппинга
    '''
    if pages >= page_limit:
        return page_limit
    else:
        return pages



def result_text_get(url):
    res_dict = dict()
    if check_page_numbers(url):
        if gen_new_url(url, check_page_numbers(url)):
            if url in res_dict:
                res_dict[url] = res_dict[url] + ads_title_graber(gen_new_url(url, pagination_limits(check_page_numbers(url), page_limit)))
            else:    
                res_dict[url] = ads_title_graber(gen_new_url(url, pagination_limits(check_page_numbers(url), page_limit)))
    else:
        if url in res_dict:
            res_dict[url] = res_dict[url] + ads_title_graber([url])
        else:
            res_dict[url] = ads_title_graber([url])    
    return res_dict


def write_to_file(selected_dict):
    with open("output_keywords_phone.csv","a",newline="") as f:
        cw = csv.writer(f)
        for key in selected_dict:
            if selected_dict[key][0]:
                cw.writerow([key])
                print(key)
                for key_1, value_1 in selected_dict[key][0].items():
                    cw.writerow([key_1, value_1])


def main(sitemap_url):
    print(len(urls_to_scrap(sitemap_url)), urls_to_scrap(sitemap_url))
    for url in urls_to_scrap(sitemap_url):
#        res = one_word_clean(result_select(freq_count(result_text_get(url))))
        write_to_file(
                one_word_clean(
                        result_select(
                                freq_count(
                                        result_text_get(url)
                                        )
                                )
                                )
                                )


if __name__ == '__main__':
    main(sitemap_url)
    
#    print(len(urls_to_scrap(sitemap_url)))
    