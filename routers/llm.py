from fastapi import APIRouter, Body, HTTPException, Request, BackgroundTasks
from fastapi.encoders import jsonable_encoder
import requests
from models.llm import Prompt, PostQuery, PostCompletion, PostAnalysis, Response
from analysis.llm.ollama.calls import generate_text_from_ollama
from utils.constants import DB_HOST


llm_router = APIRouter(prefix="/llm")
PROMPT_PREFIX = "You are a news provider whose job is to write a title and summary for news events. Provide a title and summary for the following event."


@llm_router.post("/prompt")
async def compute_prompt_result(prompt: Prompt = Body(...)):
    prompt_text = prompt.prompt

    if prompt_text == "":
        raise HTTPException(status_code=400, detail="Prompt is empty")

    prompt_result = generate_text_from_ollama(prompt.prompt, prompt.query, Response)
    return {
        "message": "Prompt result generated",
        "result": jsonable_encoder(prompt_result),
    }


@llm_router.post("/generate-analysis")
async def generate_summary(
    _: Request,
    background_tasks: BackgroundTasks,
    post_query: PostQuery = Body(...),
):
    if post_query.text == "":
        return {"message": "Text to analyze is empty"}

    background_tasks.add_task(compute_analysis, post_query)
    return {"message": "Summarization in progress", "summary_id": post_query.id}


def compute_analysis(post_query: PostQuery):
    post_completion = generate_text_from_ollama(
        prompt=PROMPT_PREFIX, query=post_query.text, response_dt=PostCompletion
    )

    post_analysis = PostAnalysis(
        id=post_query.id, post_id=post_query.post_id, completion=post_completion
    )

    make_db_request("llm/add-analysis", jsonable_encoder(post_analysis))


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
