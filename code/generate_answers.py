import os
import time
import argparse
import traceback
import pandas as pd
import torch
from tqdm import tqdm
from openai import OpenAI  # openai==1.2.0
from transformers import pipeline, AutoTokenizer
#from transformers import AutoModelForCausalLM, AutoTokenizer, AutoPromptTemplate
from huggingface_hub import notebook_login
#from messages import *
from vllm import LLM, SamplingParams
from vllm_messages import *


def get_llama_messages(lang, topic, question, AorNA, force_lang=True): #
    # llama
    topic = get_topic(lang, topic)

    system_prompt = get_system_prompt(lang, topic, AorNA)
    user_prompt = get_user_prompt(lang, question, AorNA, force_lang)

    messages = [{'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}]
    return messages

def get_mistral_messages(lang, topic, question, AorNA, force_lang=True):
    # mistral, phi
    topic = get_topic(lang, topic)

    system_prompt = get_system_prompt(lang, topic, AorNA)
    user_prompt = get_user_prompt(lang, question, AorNA, force_lang)

    messages = [{'role': 'user', 'content': system_prompt + ' ' + user_prompt}]
    return messages


if __name__ == '__main__':
    # CUDA_VISIBLE_DEVICES=3 python vllm_infer.py
    parser = argparse.ArgumentParser()
    parser.add_argument('--df_dir', type=str, default='/home/seunguk/MSQAD/Q&A/')
    parser.add_argument('--save_dir', type=str, default='/home/seunguk/MSQAD/Q&A vllm/')
    parser.add_argument('--topic', type=str, default='Rights of Older People')
    parser.add_argument('--model_type', type=str, default='phi3medium',
                        choices=['mistral0.3', 'mistral0.2', 'mistral0.1',
                        'llama3', 'llama2', 'llama2chat', 'airavata', 'solar1',
                        'phi3mini', 'phi3medium',
                        'gemma', 'qwen'])
    
    parser.add_argument('--max_tokens', type=int, default=500)
    parser.add_argument('--temperature', type=float, default=0.5)
    parser.add_argument('--top_p', type=float, default=0.8)

    parser.add_argument('--gpu_memory_utilization', type=float, default=0.9)

    parser.add_argument('--patience', type=int, default=3)
    args = parser.parse_args()


    if args.model_type == 'mistral0.3':
        model_name = 'mistralai/Mistral-7B-Instruct-v0.3'
    elif args.model_type == 'mistral0.2':
        model_name = 'mistralai/Mistral-7B-Instruct-v0.2'
    elif args.model_type == 'mistral0.1':
        model_name = 'mistralai/Mistral-7B-Instruct-v0.1'
    elif args.model_type == 'llama3':
        model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
    elif args.model_type == 'llama2':
        model_name = 'meta-llama/Llama-2-7b-hf'
    elif args.model_type == 'llama2chat':
        model_name = 'meta-llama/Llama-2-7b-chat-hf'
    elif args.model_type == 'airavata':
        model_name = 'ai4bharat/Airavata'
    elif args.model_type == 'solar1':
        model_name = 'Upstage/SOLAR-10.7B-Instruct-v1.0'
    elif args.model_type == 'phi3mini':
        model_name = 'microsoft/Phi-3-mini-4k-instruct'
    elif args.model_type == 'phi3medium':
        model_name = 'microsoft/Phi-3-medium-4k-instruct'
    elif args.model_type == 'gemma':
        model_name = 'google/gemma-7b-it'
    elif args.model_type == 'qwen':
        model_name = 'Qwen/Qwen1.5-7B-Chat'


    df = pd.read_csv(args.df_dir+args.topic+'_concat.csv', encoding='utf-8-sig')
    

    sampling_params = SamplingParams(temperature=args.temperature, top_p=args.top_p,
                                     max_tokens=args.max_tokens)
    llm = LLM(model=model_name, gpu_memory_utilization=args.gpu_memory_utilization,
                tensor_parallel_size=2)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print(f'* load {model_name}\n')

    topic = args.topic

    #df = df[:4]
    for lang in tqdm(['en', 'ko', 'zh', 'es', 'de', 'hi'], total=6):
        #topic = get_topic(lang, args.topic)

        #system_prompt_A = get_system_prompt(lang, topic, 'A')
        #system_prompt_NA = get_system_prompt(lang, topic, 'NA')

        prompt_lst,message_lst = [],[]
        for i in range(len(df)):
            question = df.loc[i][f'{lang}Q']
            #user_prompt_A = get_user_prompt(lang, question, 'A')
            #user_prompt_NA = get_user_prompt(lang, question, 'NA')

            #prompt = system_prompt_A + user_prompt_A
          
            if 'llama' in model_name or 'Qwen' in model_name:
                message_ = get_llama_messages(lang, topic, question, 'A')
            elif 'mistral' in model_name or 'Phi' in model_name or 'gemma' in model_name:
                message_ = get_mistral_messages(lang, topic, question, 'A')
            message = tokenizer.apply_chat_template(message_, tokenize=False, add_generation_prompt=True)

            #prompt = globals()[f'get_{args.model_type}_prompt'](system_prompt_A, user_prompt_A)
            prompt_lst.append(message)
            message_lst.append(message_)

        outputs = llm.generate(prompt_lst, sampling_params)
        contents = [output.outputs[0].text for output in outputs]
        df[f'{lang}A_{args.model_type}'] = contents
        df[f'{lang}A_{args.model_type}_messages'] = message_lst
     

    
    # save point
    df.to_csv(args.save_dir+args.topic+f'_A_{args.model_type}.csv', encoding='utf-8-sig', index=False)
    print('* first save point!')



    for lang in tqdm(['en', 'ko', 'zh', 'es', 'de', 'hi'], total=6):
        #topic = get_topic(lang, args.topic)

        #system_prompt_A = get_system_prompt(lang, topic, 'A')
        #system_prompt_NA = get_system_prompt(lang, topic, 'NA')

        prompt_lst,message_lst = [],[]
        for i in range(len(df)):
            question = df.loc[i][f'{lang}Q']
            #user_prompt_A = get_user_prompt(lang, question, 'A')
            #user_prompt_NA = get_user_prompt(lang, question, 'NA')

            #prompt = system_prompt_NA + user_prompt_NA

            if 'llama' in model_name or 'Qwen' in model_name:
                message_ = get_llama_messages(lang, topic, question, 'NA')
            elif 'mistral' in model_name or 'Phi' in model_name or 'gemma' in model_name:
                message_ = get_mistral_messages(lang, topic, question, 'NA')
            message = tokenizer.apply_chat_template(message_, tokenize=False, add_generation_prompt=True)

            #prompt = globals()[f'get_{args.model_type}_prompt'](system_prompt_NA, user_prompt_NA)
            prompt_lst.append(message)
            message_lst.append(message_)

        outputs = llm.generate(prompt_lst, sampling_params)
        contents = [output.outputs[0].text for output in outputs]
        df[f'{lang}NA_{args.model_type}'] = contents
        df[f'{lang}NA_{args.model_type}_messages'] = message_lst
     
    
    # save point
    df.to_csv(args.save_dir+args.topic+f'_NA_{args.model_type}.csv', encoding='utf-8-sig', index=False)
    print('* second save point!')
