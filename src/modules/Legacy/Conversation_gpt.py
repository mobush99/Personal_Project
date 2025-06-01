import openai
from dotenv import load_dotenv

load_dotenv()

def update_prompt(dialogue_history, user_input):
    messages = [
        {"role": "system",
         "content": (
             "You are a helpful assistant for movie entity extraction. "
             "Extract all entities such as movies, actors, directors, and genres. "
             "List them in the following format: [Movie: ...], [Actor: ...], [Director: ...], [Genre: ...]"
         )}
    ]
    for turn in dialogue_history:
        messages.append({"role": turn['role'], "content": turn['content']})
    messages.append({"role": "user", "content": user_input})
    return messages


def chat():
    print("Test Session")
    dialogue_history = []
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() == "exit":
            break
        messages = update_prompt(dialogue_history, user_input)
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # 또는 "gpt-4o", "gpt-4-turbo" 등
            messages=messages,
            temperature=0.8,
            max_tokens=512
        )
        # OpenAI 응답에서 assistant 메시지 추출
        assistant_reply = response.choices[0].message.content.strip()
        print(f"\nSystem: {assistant_reply}")

        dialogue_history.append({"role": "user", "content": user_input})
        dialogue_history.append({"role": "assistant", "content": assistant_reply})

if __name__ == "__main__":
    chat()
