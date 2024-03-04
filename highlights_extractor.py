from dotenv import load_dotenv
from gpt.gpt_client import gpt_client

from utils.text_processing import prepare_df, get_larger_chunks, combine_chunks
from utils.functions import get_jsons_from_chunks, build_final_json, calculate_duration


class HighlightsExtractor:
    def __init__(self, gpt_client):
        self.gpt_client = gpt_client
        self.update_system_prompt()
        self.system_prompt = gpt_client.system_prompt

    def full_pipeline(self, text, date):
        df = prepare_df(text)
        time_data = df.time.to_list()
        origin_duration = calculate_duration(time_data[0], time_data[-1])
        combined_df = get_larger_chunks(df, self.gpt_client)
        embedding_tokens = combined_df.tokens.sum()
        large_chunks = combine_chunks(combined_df)
        list_of_jsons, input_tokens, output_tokens = get_jsons_from_chunks(large_chunks, self.gpt_client)

        final_json = build_final_json(list_of_jsons, date)
        return final_json, embedding_tokens, input_tokens, output_tokens, origin_duration

    def update_system_prompt(self,
                             tags='Agenda, Decision, ChangeTheme, KeyQuestion, Idea, Task, Reaction, ActionItem',
                             granularity=None):
        example = '[{"startAt": "08:59:37","endAt": "09:00:20","KeyMomentType": "Agenda","RawText": "Дмитрий Крюков:  Тема встречи - это интеграция с оутлуком."},{"startAt": "09:05:44","endAt": "09:06:27","KeyMomentType": “ChangeTheme","RawText": "Также обсудим любимых котов т.к. это важно"}, {"startAt": "09:10:09","endAt": "09:10:34","KeyMomentType": "Decision","RawText": "Подводя итоги встречи, Иван будет заниматься интеграцией с ChatGPT"}, ...]'
        system_prompt = f"""
        Ты модель, которая помогает пользователям узнать произошедшее на онлайн-встрече. Ты принимаешь на вход файл .txt, который является транскрибацией онлайн-конференции нашей компании. Твоя задача - на основе текстового файла определить ключевые моменты (highlights):
        - Выделить хайлайт. {'Выдели ' + granularity + ' хайлайтов' if granularity else ''}
        - Определить его временные рамки (startAt - первая реплика хайлайта, endAt - следующая за последней реплика)
        - Создать краткое описание хайлайта в одно предложение, желательно меньше 15 слов и записать в RawText
        - Создать tag для хайлайта, к примеру, {tags} и тп и записать его в KeyMomentType
        Выдели только важные моменты, осмысленные моменты.
        Результатом твоей работы должен быть список словарей следующего формата - пример:
        {example}"""
        self.gpt_client.system_prompt = system_prompt


highlights_extractor = HighlightsExtractor(gpt_client)
