from app.tasks.celery_app import celery_app
from app.db.mongodb import db
from bson import ObjectId
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize LLM
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)

# Prompt template: summarize + categorize + suggest reply
prompt_template = """
You are an AI assistant for support tickets.
Ticket Title: {title}
Ticket Description: {description}

Tasks:
1. Summarize the ticket in 1-2 sentences.
2. Categorize the ticket: billing, bug, account, other.
3. Suggest a reply to the user.

Respond in JSON format like:
{{ "summary": "...", "category": "...", "suggested_reply": "..." }}
"""

prompt = PromptTemplate(input_variables=["title", "description"], template=prompt_template)
chain = LLMChain(llm=llm, prompt=prompt)


@celery_app.task
def analyze_ticket(ticket_id: str, title: str, description: str):
    # Run LangChain
    result = chain.run(title=title, description=description)

    # Convert result to dict
    import json
    try:
        data = json.loads(result)
    except:
        data = {"summary": "", "category": "other", "suggested_reply": ""}

    # Update ticket in MongoDB
    db.tickets.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": {
            "summary": data.get("summary"),
            "category": data.get("category"),
            "suggested_reply": data.get("suggested_reply")
        }}
    )
