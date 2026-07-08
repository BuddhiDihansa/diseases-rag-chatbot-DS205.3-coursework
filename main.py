
"""
Entry point - runs the full Medical AI system.

Usage:
    python main.py
"""
from dotenv import load_dotenv
load_dotenv()



from services.pipeline import MedicalAIPipeline


def main():
    pipeline = MedicalAIPipeline()

    print("Medical AI Assistant - Type 'exit' to quit.\n")

    while True:
        user_input = input("Describe your symptoms: ")

        if user_input.strip().lower() == "exit":
            print("Goodbye!")
            break

        pipeline.run(user_input)
        print("\n")


if __name__ == "__main__":
    main()