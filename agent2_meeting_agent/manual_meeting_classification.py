from .meeting_classifier import MeetingClassifier
from .meeting_source import get_meetings


def main():
    meetings = get_meetings()

    if not meetings:
        print("No meetings found.")
        return

    classifier = MeetingClassifier()

    for meeting in meetings:
        try:
            decision = classifier.classify(meeting)

            print(f"Meeting: {meeting.title}")
            print(f"Important: {decision.important}")
            print(f"Reason: {decision.reason}")
            print()

        except ValueError as error:
            print(
                f"[CLASSIFICATION ERROR] "
                f"{meeting.title}: {error}"
            )

        except Exception as error:
            print(
                f"[AI ERROR] "
                f"{meeting.title}: {error}"
            )


if __name__ == "__main__":
    main()