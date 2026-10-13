from agent2_meeting_agent.llm_client import create_llm


def test_openai_connection() -> None:
    try:
        llm = create_llm()

        response = llm.invoke(
            "Reply with exactly: OPENAI CONNECTION OK"
        )

        print(response.content)

    except ValueError as error:
        print(f"[CONFIG ERROR] {error}")

    except Exception as error:
        print(
            "[OPENAI ERROR] "
            f"Failed to connect to OpenAI: {error}"
        )


if __name__ == "__main__":
    test_openai_connection()