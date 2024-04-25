import requests

from utils.constants import OLLAMA_HOST
from pydantic import BaseModel
from langchain_community.llms import Ollama
from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate


OLLAMA_MODEL = "gemma"
OLLAMA_TIMEOUT = 15


def generate_text_from_ollama(prompt: str, query: str, response_dt: BaseModel):
    parser = JsonOutputParser(pydantic_object=response_dt)

    prompt = PromptTemplate(
        template=prompt + "\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm = Ollama(
        model=OLLAMA_MODEL, temperature=0, base_url=f"http://{OLLAMA_HOST}:11434"
    )
    chain = prompt | llm | parser

    return_dt = chain.invoke({"query": query})
    return response_dt(**return_dt)


def add_model_to_ollama():
    ollama_url = f"http://{OLLAMA_HOST}:11434/api/pull"

    try:
        response = requests.post(
            ollama_url,
            json={"name": OLLAMA_MODEL, "stream": False},
            timeout=OLLAMA_TIMEOUT,
        )
    except requests.exceptions.RequestException as e:
        print("Could not add model to Ollama", e)
        return

    if response.status_code == 200:
        print("Added model to Ollama")
    else:
        print("Failed to add model to Ollama,", response.json())


if __name__ == "__main__":
    # summary_intro = "You are a news provider whose job is to write short summaries for news events. You need to write a summary to describe the following event in a paragraph. The paragraph needs to be only a few sentences so that readers get the gist of the event."  # and output only the summary and nothing else. Give the summary in the following format - SUMMARY: Your summary here :"
    # summary_intro = "Summarize this news article in 1 short paragraph and return the summary only: "
    # title_intro = "Give a title for this news article; output one title only; return only the title and nothing else; Give the title in the following format - TITLE: Your title here :"
    # title_intro = "Generate a title for the following text and output only the title and nothing else. Give only one title in the following format - TITLE: Your title here :"
    # title_intro = "You are a news provider whose job is to write short posts for news events. You need to write a title for your post that describes the following event. Whatever you output will be the title used in the post so keep it concise."

    from pydantic import BaseModel, Field

    class NewsEventInfo(BaseModel):
        title: str = Field(description="title of the news event")
        summary: str = Field(description="summary of the news event")

    prompt = "You are a news provider whose job is to write a title and summary for news events. Provide a title and summary for the following event."
    query = ""

    print(generate_text_from_ollama(prompt, query, NewsEventInfo))
