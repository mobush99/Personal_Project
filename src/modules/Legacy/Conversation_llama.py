import torch
from transformers import pipeline

model_id = "meta-llama/Llama-3.1-8B-Instruct"

pipe = pipeline(
    "text-generation",
    model=model_id,
    token="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",
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)


def update_prompt(dialogue_history, user_input):
    message = [
        {"role": "system",
         "content": """
         You are a helpful assistant for movie entity extraction. 
         extract all entities such as movies, actors, directors, and genres.
         List them in the following format:
         [Movie: ...], [Actor: ...], [Director: ...], [Genre: ...]"""},
        {"role": "user", "content": "Can I get some movie recommendations?"}
    ]
    if dialogue_history:
        for turn in dialogue_history:
            messages.append({"role": turn['role'], "content": turn['content']})
        messages.append({"role": "user", "content": user_input})
    return message

def chat():
    print("Test Session")
    dialogue_history = []
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() == "exit":
            break
        prompt = update_prompt(dialogue_history, user_input)
        outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature =0.8, return_full_text=False)
        response = outputs[0]['generated_text']
        print(f"\nSystem: {response}")

        dialogue_history.append({"role": "user", "content": user_input})
        dialogue_history.append({"role": "assistant", "content": response})

        # print(f"****DIALOGUE HISTORY****\n{dialogue_history}")

if __name__ == "__main__":
    chat()