import ast
import numpy as np
import pandas as pd
from skbio import DistanceMatrix
from skbio.stats.distance import permanova
from scipy.spatial.distance import pdist, squareform
from tqdm import tqdm
import argparse
import time


def get_Emb_lst(df, lang):
    def str2lst(text):
        return ast.literal_eval(text)
    def lst2ary(lst):
        return np.array(lst)
    
    Emb_lst = df[f'{lang}Emb'].tolist()
    Emb_lst = [lst2ary(str2lst(Emb)) for Emb in Emb_lst]
    Emb_lst = np.vstack(Emb_lst)
    return Emb_lst


def compare_2lang(df, lang1, lang2, permutations):
    def get_cos_sim(v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    def get_langfullname(lang):
        return {'en': 'English', 'ko': 'Korean', 'zh': 'Chinese',
                'es': 'Spanish', 'de': 'German', 'hi': 'Hindi'}[lang]
    if lang1 == lang2:
        return np.nan, np.nan
    
    start_time = time.time()
    
    lang1Emb_lst = get_Emb_lst(df, lang1)
    lang2Emb_lst = get_Emb_lst(df, lang2)

    combined = np.vstack([lang1Emb_lst, lang2Emb_lst])
    
    dist_matrix = DistanceMatrix(squareform(pdist(combined, metric=get_cos_sim)))
    grouping = [get_langfullname(lang1)] * len(df) + [get_langfullname(lang2)] * len(df)
    print(f'* {lang1,lang2} dist matrix end')

    result = permanova(dist_matrix, grouping, permutations=permutations)
    print(f'* {lang1,lang2} permanova end\n')
    stats, pval = result['test statistic'], result['p-value']
    #print(f'* {lang1},{lang2} {time.time()-start_time} passed!')
    return stats, pval

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--df_dir', type=str, default='/home/seunguk/MSQAD/Q&A response Emb/')
    parser.add_argument('--save_dir', type=str, default='/home/seunguk/MSQAD/Q&A PM/')
    parser.add_argument('--topic', type=str, default='Rights of Older People')

    parser.add_argument('--permutations', type=int, default=5000)
    args = parser.parse_args()

    topic = args.topic
    df = pd.read_csv(args.df_dir+topic+'_responseEmb.csv', encoding='utf-8-sig')

    
    for seed in [42, 52, 62]:
        np.random.seed(seed)

        for lang1 in ['en', 'ko', 'zh', 'es', 'de', 'hi']:
            globals()[f'{lang1}_PM'] = []

            for lang2 in tqdm(['en', 'ko', 'zh', 'es', 'de', 'hi'], total=6):
                stats, pval = compare_2lang(df, lang1, lang2, args.permutations)
                globals()[f'{lang1}_PM'].append([stats, pval])
                print(globals()[f'{lang1}_PM'])

        PMdf = pd.DataFrame({'en': en_PM, 'ko': ko_PM, 'zh': zh_PM, 'es': es_PM, 'de': de_PM, 'hi': hi_PM})
        PMdf.to_csv(args.save_dir+topic+'_PM_seed{seed}.csv', encoding='utf-8-sig', index=False)