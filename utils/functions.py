import numpy as np
import tiktoken
from numpy.linalg import norm
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def cosine_similarity(vec_a, vec_b):
    """
    Compute the cosine similarity between two embedding vectors.
    """
    if norm(vec_a) == 0 or norm(vec_b) == 0:
        logging.warning("One of the vectors is zero.")
        return 0.0
    similarity = np.dot(vec_a, vec_b) / (norm(vec_a) * norm(vec_b))
    return similarity


def calculate_duration(start, end):
    format = "%H:%M:%S"
    start_dt = datetime.strptime(start, format)
    end_dt = datetime.strptime(end, format)

    # Adjust for crossing midnight
    if end_dt < start_dt:
        end_dt += timedelta(days=1)

    # Calculate the difference in seconds
    delta = end_dt - start_dt
    return delta.total_seconds()


def num_tokens_from_string(string: str, encoding_name: str = 'cl100k_base') -> int:
    """
    Returns the number of tokens in a text string.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_jsons(large_chunk, gpt_client, max_fails=3):
    """
    Attempts to parse a JSON response from the GPT client.
    """
    try:
        answer = gpt_client.answer_prompt(large_chunk)
        print(answer)
        jsons = json.loads(answer)
        return jsons
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding failed: {e}")
        if max_fails > 0:
            return get_jsons(large_chunk, gpt_client, max_fails=max_fails - 1)
        else:
            logging.error("Max retries reached. Returning empty list.")
            return []


def get_jsons_from_chunks(large_chunks, gpt_client):
    """
    Aggregates JSON responses from multiple chunks.
    """
    jsons_list = []
    input_tokens = 0
    output_tokens = 0
    for curr_chunk in large_chunks:
        response_jsons_list = get_jsons(curr_chunk, gpt_client)
        input_tokens += num_tokens_from_string(curr_chunk)
        output_tokens += num_tokens_from_string(str(response_jsons_list))
        jsons_list += response_jsons_list
    return jsons_list, input_tokens, output_tokens


def build_final_json(list_of_jsons, date, task_id=1):
    """
    Builds a final JSON structure from a list of JSON objects.
    """
    final_json = {"type": "CreateHighlightsResponse",
                  "data": {
                      "taskId": task_id,
                      "KeyMoments": list_of_jsons
                  }}

    for j in final_json['data']['KeyMoments']:
        j['startAt'] = date + ' ' + j['startAt']
        j['endAt'] = date + ' ' + j['endAt']

    return final_json


def calculate_highlight_duration(highlight_json):
    highlight_duration = 0
    for j in highlight_json['data']['KeyMoments']:
        start = j['startAt'].split(' ')[1]
        end = j['endAt'].split(' ')[1]
        highlight_duration += calculate_duration(start, end)
    return highlight_duration
