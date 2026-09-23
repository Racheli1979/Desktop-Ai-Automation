from agent2_meeting_agent.llm_client import create_llm


llm = create_llm()

response = llm.invoke(
    "Reply with exactly: OPENAI CONNECTION OK"
)

print(response.content)
