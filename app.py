from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

from db.database_operations import add_highlight, get_db_session
from highlights_extractor import highlights_extractor
import uvicorn

from utils.functions import calculate_highlight_duration

app = FastAPI()


@app.post("/process-text/")
async def process_text(
        file: UploadFile = File(
            ...,
            description='.txt файл транскрибации в формате "bandicam 2022-09-29 18-01-57-982.mp3.txt"'),
        tags: str = Form(None,
                         description='Оставить пустым для дефолтных тэгов. Тэги в формате "Agenda, ActionItem, Reaction..."')):
    try:
        if tags:
            highlights_extractor.update_system_prompt(tags=tags)
        file_name = file.filename
        date = file_name.split(' ')[1]
        content = await file.read()
        decoded_content = content.decode("utf-8")
        text = decoded_content.split('\n\n')

        final_json, embedding_tokens, input_tokens, output_tokens, origin_duration_seconds = \
            highlights_extractor.full_pipeline(text, date)

        highlight_duration_seconds = calculate_highlight_duration(final_json)

        highlight_data = {'filename': file_name,
                          'date': date,
                          'text': decoded_content[:80],
                          'highlights_json': final_json,
                          'embedding_tokens': int(embedding_tokens),
                          'input_tokens': int(input_tokens),
                          'output_tokens': int(output_tokens),
                          'origin_duration_seconds': int(origin_duration_seconds),
                          'origin_duration': f'{int(origin_duration_seconds // 60)}:{int(origin_duration_seconds % 60)}',
                          'highlight_duration_seconds': int(highlight_duration_seconds),
                          'highlight_duration': f'{int(highlight_duration_seconds // 60)}:{int(highlight_duration_seconds % 60)}'}
        with get_db_session() as db:
            add_highlight(db, highlight_data)

        if tags:
            highlights_extractor.update_system_prompt()

        return JSONResponse(content=final_json)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
