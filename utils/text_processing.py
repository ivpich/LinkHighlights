import pandas as pd
from utils.functions import num_tokens_from_string, cosine_similarity
import numpy as np

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_transcription(path):
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read().split('\n\n')
    return text


def split_text(text):
    try:
        meta, content = text.split('\n')
        time = meta.split(' ')[-1]
        speaker = ' '.join(meta.split(' ')[:-1])
        return speaker, time, content
    except Exception as e:
        print(e)


def larger_chunks(df, minimum_tokens=300):
    temp_data = []

    temp_content = ""
    temp_tokens = 0
    temp_speaker = ""
    start_time = ""
    temp_raw_text = ""

    for index, row in df.iterrows():
        if temp_tokens == 0:
            temp_speaker = row['speaker']
            start_time = row['time']
            temp_raw_text = row['raw_text']
        temp_content += " " + row['content'] + '.'
        temp_tokens += row['tokens']

        if temp_tokens >= minimum_tokens:
            temp_data.append(
                {'speaker': temp_speaker, 'time': start_time, 'content': temp_content.strip(), 'tokens': temp_tokens,
                 'raw_text': temp_raw_text})
            temp_content = ""
            temp_tokens = 0

    if temp_tokens > 0:
        temp_data.append(
            {'speaker': temp_speaker, 'time': start_time, 'content': temp_content.strip(), 'tokens': temp_tokens,
             'raw_text': temp_raw_text})

    if temp_data:
        combined_df = pd.DataFrame(temp_data)
    else:
        combined_df = pd.DataFrame(columns=['speaker', 'time', 'content', 'tokens', 'raw_text'])
    return combined_df


def prepare_df(text):
    df = pd.DataFrame(map(split_text, text), columns=['speaker', 'time', 'content'])
    df.dropna(inplace=True)
    df['tokens'] = df.content.apply(lambda x: num_tokens_from_string(x, "cl100k_base"))
    df['raw_text'] = df['speaker'] + ' ' + df['time'] + ' - ' + df['content']
    return df


def get_larger_chunks(df, gpt_client):
    df = larger_chunks(df, minimum_tokens=300)
    print(df)
    df['emb'] = df.content.apply(lambda x: np.array(gpt_client.get_embedding(x)))
    return df


def combine_chunks(combined_df):
    counter = 0
    l = [0]
    while counter < len(combined_df) - 13:
        left_context = combined_df.iloc[counter: counter + 5].emb.sum()
        a = combined_df.iloc[counter + 5].emb
        b = combined_df.iloc[counter + 6].emb
        c = combined_df.iloc[counter + 7].emb
        right_context = combined_df.iloc[counter + 8: counter + 13].emb.sum()
        print(
            f'a = left context - {cosine_similarity(a, left_context)}, right context - {cosine_similarity(a, right_context + b + c)}')
        print(
            f'b = left context - {cosine_similarity(b, left_context + a)}, right context - {cosine_similarity(b, right_context + c)}')
        print(
            f'c = left context - {cosine_similarity(c, left_context + a + b)}, right context - {cosine_similarity(c, right_context)}')
        print('_______')
        if cosine_similarity(c, left_context + a + b) < cosine_similarity(c, right_context):
            counter += 5 + 3
            l.append(counter)
            continue
        if cosine_similarity(b, left_context + a) < cosine_similarity(b, right_context + c):
            counter += 5 + 2
            l.append(counter)
            continue
        if cosine_similarity(a, left_context) < cosine_similarity(a, right_context + b + c):
            counter += 5 + 1
            l.append(counter)
            continue
        else:
            counter += 5
            l.append(counter)

    print(l)
    large_chunks = []
    for i in range(len(l[:-1])):
        content_large = (combined_df.iloc[l[i]:l[i + 1]].raw_text + ' \n').sum() + \
                        combined_df.iloc[l[i + 1]].raw_text.split(' - ')[0] + " - ..."
        large_chunks.append(content_large)

    large_chunks.append((combined_df.iloc[l[-1]:].raw_text + ' \n').sum())
    return large_chunks
