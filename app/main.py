from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse
from app.agent import run_agent
from app.memory import add_to_memory
import uuid

app = FastAPI(title="AI Support Agent")


@app.get("/health")
async def health_check():
    return {"status": "ok"}

# @app.post("/agent/chat", response_model=ChatResponse)
# async def chat_endpoint(request: ChatRequest):
#     session_id = request.session_id or str(uuid.uuid4())
#     message = request.message

#     memory = get_memory(session_id)

#     lower_message = message.lower()
#     if "order" in lower_message:
#         reply = get_order_status("ORD-1001")
#     elif "return" in lower_message or "refund" in lower_message or "payment" in lower_message:
#         reply = search_faqs_tool(message)
#     else:
#         reply = f"You said: {message}"

@app.post("/agent/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    message = request.message

    reply = run_agent(session_id, message)

    add_to_memory(session_id, f"User: {message}")
    add_to_memory(session_id, f"Agent: {reply}")

    return ChatResponse(
        reply=reply,
        session_id=session_id
    )
