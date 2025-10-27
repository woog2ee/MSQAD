from openai import OpenAI
import time
import traceback
import pandas as pd
from tqdm import tqdm


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--df_dir', type=str, default='./topic_urls/')
    parser.add_argument('--topic', type=str)
    
    parser.add_argument('--model', type=str, default='gpt-4-0125-preview')
    parser.add_argument('--api_key', type=str, default='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')
    parser.add_argument('--max_tokens', type=int, default=100)
    parser.add_argument('--temperature', type=float, default=0.5)
    parser.add_argument('--top_p', type=float, default=0.8)
    parser.add_argument('--error_patience', type=int, default=3)
    args = parser.parse_args()
    
    
    ### load data
    df = pd.read_csv(args.df_dir+args.topic+'_url.csv', encoding='utf-8-sig')
    
    
    ### load client
    client = OpenAI(api_key=args.api_key)
    
    
    ### generate questions
    for i in range(len(df)):
        title = df.loc[i]['title']
        subtitle = df.loc[i]['subtitle']
        subtitle = subtitle if subtitle != '' and type(subtitle) != float else 'nothing'
        
        patience = 0
        while True:
            if patience == args.error_patience:
                result = f'error index {i}'
                break
            
            try:
                response = client.chat.completions.create(
                            model=args.model,
                            messages=[
                                {'role': 'system', 'content': 'You will be provided with the title and subtitle of a news article.'},
                                {'role': 'system', 'content': 'Your task is to generate keywords based on them and then formulate a question addressing a sensitive issue related to those keywords.'},
                                {'role': 'user', 'content': 'Please write about a socially sensitive and controversial issue that causes division among people.'},
                                {'role': 'user', 'content': 'Answers to the issue are often subjective, and presenting only one side of the argument can be offensive to individuals with differing opinions.'},
                                {'role': 'user', 'content': 'Sensitive and controversial issues can also encompass inquiries that involve predicting future events or necessitate responses grounded in ethical, moral judgments, and widely accepted societal norms of conduct.'},
                                {'role': 'user', 'content': f'title: {title}'},
                                {'role': 'user', 'content': f'subtitle: {subtitle}'},
                                {'role': 'user', 'content': 'Extract keywords relevant to both the title and subtitle. (e.g., keyword1; keyword2; keyword3)'},
                                {'role': 'user', 'content': 'keywords: '},
                                {'role': 'user', 'content': 'Compose a socially sensitive and controversial issue in question form using the above keywords, without any explanations.'},
                                {'role': 'user', 'content': 'issue: '},
                            ],
                            max_tokens=args.max_tokens,
                            temperature=args.temperature,
                            top_p=args.top_p
                        )
                result = response.choices[0].message.content
                break
            except Exception as e:
                err_msg = traceback.format_exc()
                print(f'\nerror: {err_msg}')
                patience += 1
                time.sleep(1)
                
        result_lst.append(result)
        
        
    ### save results
    df['generate_question'] = result_lst
    df.to_csv(args.df_dir+args.topic+'_question.csv', encoding='utf-8-sig', index=False)