from fastapi import APIRouter, Body, HTTPException, Request, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from utils.funcs import add_data_to_db
from models.llm import Prompt, PostQuery, PostCompletion, PostAnalysis, Response
from analysis.llm.ollama.calls import generate_text_from_ollama


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
    if post_completion := generate_text_from_ollama(
        prompt=PROMPT_PREFIX, query=post_query.text, response_dt=PostCompletion
    ):
        post_analysis = PostAnalysis(
            id=post_query.id, post_id=post_query.post_id, completion=post_completion
        )

        add_data_to_db("llm/add-analysis", post_analysis)
