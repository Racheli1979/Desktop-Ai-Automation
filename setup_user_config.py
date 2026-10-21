
from getpass import getpass

import keyring


SERVICE_NAME = "DesktopAiAutomation"
OPENAI_KEY_NAME = "openai_api_key"


def main() -> None:
    print("Desktop AI Automation - Initial Setup")
    print("--------------------------------------")

    api_key = getpass("Enter your OpenAI API key: ").strip()

    if not api_key:
        print("No API key entered. Setup cancelled.")
        return

    keyring.set_password(
        SERVICE_NAME,
        OPENAI_KEY_NAME,
        api_key,
    )

    print("OpenAI API key saved securely for this Windows user.")


if __name__ == "__main__":
    main()