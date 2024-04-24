from fastapi import APIRouter, Body, HTTPException, Request, BackgroundTasks
from fastapi.encoders import jsonable_encoder
import requests
from models.llm import SummaryQuery, Summary, Prompt, Title, TitleQuery
from analysis.llm.ollama.calls import generate_text_from_ollama, parse_ollama_response
from utils.constants import DB_HOST


llm_router = APIRouter(prefix="/llm")
SUMMARY_PROMPT_PREFIX = (
    "Summarize the following text in at most 2 paragraphs and return only the summary: "
)
TITLE_PROMPT_PREFIX = "Generate a title for the following text that is at most 10 words long and return only the title: "


@llm_router.post("/prompt")
async def compute_prompt_result(prompt: Prompt = Body(...)):
    prompt_text = prompt.prompt

    if prompt_text == "":
        raise HTTPException(status_code=400, detail="Prompt is empty")
    elif prompt_result := generate_text_from_ollama(prompt.prompt):
        return {"message": "Prompt result generated", "result": prompt_result}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate prompt result")


@llm_router.post("/generate-summary")
async def generate_summary(
    _: Request,
    background_tasks: BackgroundTasks,
    summary_query: SummaryQuery = Body(...),
):
    if summary_query.text == "":
        return {"message": "Text to summarize is empty"}

    background_tasks.add_task(start_summarization, summary_query)
    return {"message": "Summarization in progress", "summary_id": summary_query.id}


@llm_router.post("/generate-title")
async def generate_title(
    _: Request,
    background_tasks: BackgroundTasks,
    title_query: TitleQuery = Body(...),
):
    if title_query.text == "":
        return {"message": "Text to make title is empty"}

    background_tasks.add_task(start_title, title_query)
    return {"message": "Making title in progress", "title_id": title_query.id}


def start_summarization(summary_query: SummaryQuery):
    if summary_json := generate_text_from_ollama(
        SUMMARY_PROMPT_PREFIX + summary_query.text
    ):
        summary_text = parse_ollama_response(summary_json)
        summary = Summary(
            id=str(summary_query.id),
            post_id=summary_query.post_id,
            summary=summary_text,
        )
        make_db_request("llm/add-summary", jsonable_encoder(summary))
    else:
        print("Failed to generate summary")


def start_title(title_query: TitleQuery):
    if title_json := generate_text_from_ollama(
        SUMMARY_PROMPT_PREFIX + title_query.text
    ):
        title_text = parse_ollama_response(title_json)
        title = Title(
            id=str(title_query.id),
            post_id=title_query.post_id,
            title=title_text,
        )
        make_db_request("llm/add-title", jsonable_encoder(title))
    else:
        print("Failed to generate title")


def make_db_request(endpoint: str, data: dict):
    db_url = f"http://{DB_HOST}:8000/{endpoint}"

    try:
        response = requests.post(db_url, json=data)
    except requests.exceptions.RequestException as e:
        print(f"Could not make request to {db_url}", e)
    else:
        if response.status_code == 200:
            print(f"Successfully made request to {db_url}")
        else:
            print(f"Failed to make request to {db_url},", response.json())
