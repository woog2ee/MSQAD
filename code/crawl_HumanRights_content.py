from utils_HumanRights import topic_num_dic
import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
from tqdm import tqdm

def get_soup(url, sec):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    time.sleep(sec)
    return soup

def info2firstparagraph(info):
    info = str(info).split('p>')
    
    candidate = []
    for text in info:
        # text line must have <p> and </p>
        if '</' not in text:
            continue
        else:
            #text = re.sub(r'</', '', text)
            
            # text line is not short
            if len(text) <= 5:
                continue 
            # text line does not have to start with '<'
            elif text[0] == '<':
                continue
            # text line must have content
            elif text == '':
                continue
            # text line should end with appropriate punctuation ('-3' consider for '</')
            elif text[-3] in [',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                continue
            else:
                # remove hyperlink
                text = re.sub(r'<a href="[a-zA-Z0-9://.-]+">', '', text)
                text = re.sub(r'</a>', '', text)
                
                # remove '</' from '</p>'
                text = re.sub(r'</', '' ,text)
                return text
    return ''

article_content_xpath_dic = {
     'Statement': '#block-hrw-design-content > article > div > div:nth-child(2) > div > div.grid-2.w-full.flex-col.lg\:flex.lg\:w-3\/5.lg\:px-0 > div > div:nth-child(1) > div > div > p'
}


if __name__ == '__main__':
    
    ### decide which topic to crawl
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str)
    
    args = parser.parse_args()
    if args.topic not in list(topic_num_dic.keys()):
        raise Exception('wrong topic passed, please refer to Human Rights Watch website')
        
    
    ### get the topic informations
    df = pd.read_csv(f'./{args.topic}_url.csv', encoding='utf-8-sig')
    
    
    ### get all first paragraphs per article
    firstparagraph_lst = []
    for i in tqdm(range(len(df))):
        url = df.loc[i]['url']
        
        soup = get_soup(url, 0.1)
        info = soup.select(article_content_xpath_dic['Statement'])
        
        firstparagraph_lst.append(info2firstparagraph(info))
        
        
    ### save
    df['first paragraph'] = firstparagraph_lst
    df.to_csv(f'./{args.topic}_content.csv', encoding='utf-8-sig', index=False)
        
    