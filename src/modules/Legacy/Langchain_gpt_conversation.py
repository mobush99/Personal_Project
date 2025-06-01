import os
from dotenv import load_dotenv
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from .Parse_output import parse_output
from .Update_graph_neo4j import update_nodes

load_dotenv()
class ConversationModule():
    def __init__(self, model_name='gpt-3.5-turbo', temperature=0.8, max_tokens=512, num_recommend=3, database='test'):
        self.model = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
        self.num_recommend = num_recommend
        self.database = database
        self.dialogue_history = []

    def build_system_prompt(self):
        return SystemMessage(
            content=f"""
            You are a helpful assistant for movie recommendation and entity extraction.
            MUST follow these instructions:

            1. If there is not enough information about the user's preferences, ask additional questions instead of making recommendations.
            2. If you do make recommendations, limit the number of recommended movies to {self.num_recommend}.
            3. when recommending movies, you MUST follow this format, and **do not add any words**:
            <m>Movie Title</m>: <a>actor1, actor2, ...</a> <d>director</d>
            4. **Do not use any other format, tags, or tokens and words for output.** 
            ONLY use '<m>', '</m>', '<a>', '</a>', '<d>', '</d>' exactly as shown.
            """
        )

def update_messages(dialogue_history, user_input, num=5):
    messages = [
        SystemMessage(
            content=f"""
            You are a helpful assistant for movie recommendation and entity extraction.
            MUST follow these instructions:
            
            1. If there is not enough information about the user's preferences, ask additional questions instead of making recommendations.
            2. If you do make recommendations, limit the number of recommended movies to {num}.
            3. when recommending movies, you MUST follow this format, and **do not add any words**:
            <m>Movie Title</m>: <a>actor1, actor2, ...</a> <d>director</d>
            4. **Do not use any other format, tags, or tokens and words for output.** only use '<m>', '</m>', '<a>', '</a>', '<d>', '</d>' exactly as shown.
            """
        )
    ]
    for turn in dialogue_history:
        if turn['role'] == 'user':
            messages.append(HumanMessage(content=turn['content']))
        elif turn['role'] == 'assistant':
            messages.append(AIMessage(content=turn['content']))
    messages.append(HumanMessage(content=user_input))
    return messages


def chat():
    print("Test Session: LangChain-GPT-Rec&Extraction")
    dialogue_history = []
    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.8, max_tokens=512)
    while True:
        parsed_results = []
        user_input = input("\nUser: ")
        if user_input.lower() == 'exit':
            break
        messages = update_messages(dialogue_history, user_input, 3)
        response = llm.invoke(messages)
        assistant_reply = response.content.strip()

        print(f"\nSystem: {assistant_reply}")
        parsed_results = parse_output(assistant_reply)
        print(f"\nParsed: {parsed_results}")

        dialogue_history.append({"role": "user", "content": user_input})
        dialogue_history.append({"role": "assistant", "content": assistant_reply})
        if parsed_results:
            update_nodes(parsed_results, database='test')

# if __name__ == '__main__':
#     chat()


