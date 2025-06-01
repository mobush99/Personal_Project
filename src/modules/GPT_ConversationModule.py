import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from modules.Parse_output import JSON_parse_output
from modules.Update_graph_neo4j import update_nodes

load_dotenv()

class GPTConversationModule():
    def __init__(self, model_name='gpt-3.5-turbo', temperature=0.8, max_tokens=512, num_recommend=3, database='test'):
        self.model = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
        self.response_schemas = [
            ResponseSchema(name='Answer_type', description='Type of answer: Chit-chat, Questioning, of Recommendation'),
            ResponseSchema(name='Movies', description=f'List of {num_recommend} recommended movies. Each movie is an object with title, actors, director'),
            ResponseSchema(name='message', description='Short natural language message for chit-chat or follow-up questions.')
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()
        self.format_instructions = self.format_instructions.replace('{', "{{").replace('}', '}}')

        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
                f"""You are a movie recommendation assistant.
                Follow these rules:
                1. If the user's preferences are very vague, you may ask a clarifying question.
                2. If the user gives some preference (even partial, e.g. likes a director, genre, or a movie), you can provide recommendations, but mention that more information could improve the results.
                3. If you recommend, set answer_type to 'Recommendation'. If you ask a clarifying question, set answer_type to 'Questioning'. For greetings or goodbyes, use 'Chit-chat'.
                4. Always answer in the following JSON format:
                
                {self.format_instructions}
                """
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{user_input}")
        ])

        # 세션별 대화 히스토리 저장소
        self.store = {}

        def get_session_history(session_id: str):
            if session_id not in self.store:
                self.store[session_id] = InMemoryChatMessageHistory()
            return self.store[session_id]

        # RunnableWithMessageHistory 설정
        chain = self.prompt | self.model
        self.runnable_chain = RunnableWithMessageHistory(
            chain,
            get_session_history=get_session_history,
            input_messages_key="user_input",
            history_messages_key="history"
        )

    def get_json_response(self, user_input, session_id="default"):
        response = self.runnable_chain.invoke(
            {"user_input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        return self.output_parser.parse(response.content)

    def chat(self):
        print("TEST SESSION: LangChain-GPT-JSON (with RunnableWithMessageHistory)")
        session_id = "default"
        while True:
            user_input = input("\nUser: ")
            if user_input.lower() == 'exit':
                break
            result = self.get_json_response(user_input, session_id=session_id)

            print("\nSystem: ")
            print(result)

            parsed_output = JSON_parse_output(result)
            print("PARSED:\n", parsed_output)
            if parsed_output is not None:
                update_nodes(parsed_output, database='test')

if __name__ == '__main__':
    ConversationModule = GPTConversationModule()
    ConversationModule.chat()
