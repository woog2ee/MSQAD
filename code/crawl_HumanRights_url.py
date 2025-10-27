from utils_HumanRights import (topic_num_dic, topic_maxpage_dic,
                               get_url, get_category, get_title, get_subtitle, url2date)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import argparse
import pandas as pd
from tqdm import tqdm


if __name__ == '__main__':
    
    ### decide which topic to crawl
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str)
    
    args = parser.parse_args()
    if args.topic not in list(topic_num_dic.keys()):
        raise Exception('wrong topic passed, please refer to Human Rights Watch website')
    
    
    ### go to the news pages
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    time.sleep(3)
    
    news_per_page = f'https://www.hrw.org/news?topic%5B0%5D={topic_num_dic[args.topic]}&page='
    
    url_lst, date_lst, category_lst, title_lst, subtitle_lst = [], [], [], [], []
    for page in tqdm(range(0, topic_maxpage_dic[args.topic]+1, 1)):
        
        driver.get(news_per_page+str(page))
        time.sleep(1)
        
        
        ### get all urls, dates, categories, titles, and subtitles per page
        for i in range(1, 15+1, 1):
            try:
                url, case = get_url(driver, i)
                date = url2date(url)
                category = get_category(driver, i, case)
                title = get_title(driver, i, case)
                subtitle = get_subtitle(driver, i, case)
                
                url_lst.append(url)
                date_lst.append(date)
                category_lst.append(category)
                title_lst.append(title)
                subtitle_lst.append(subtitle)
                
                if case:
                    # for an only one article per page
                    break
            except Exception as e:
                # over the max articles per page
                break
             
            
    ### save
    topic_lst = [args.topic] * len(url_lst)
    df = pd.DataFrame({'topic': topic_lst, 'url': url_lst, 'date': date_lst,
                       'category': category_lst, 'title': title_lst, 'subtitle': subtitle_lst})
    df.to_csv(f'./{args.topic}_url.csv', encoding='utf-8-sig', index=False)