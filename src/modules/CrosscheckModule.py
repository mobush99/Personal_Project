from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

load_dotenv()

class CrosscheckModule:
    def __init__(self, model=None):
        self.model = model or ChatOpenAI(model="gpt-3.5-turbo", temperature=0.8)
        self.text_splitter = CharacterTextSplitter(chunk_size=500)
        self.embedder = OpenAIEmbeddings()

    def retrieve_wikipedia(self, query):
        wiki_loader = WikipediaLoader(query=query)
        wiki_docs = wiki_loader.load()
        splitted_docs = self.text_splitter.split_documents(wiki_docs)
        return splitted_docs

    def build_vector_db(self, docs):
        vectorstore = FAISS.from_documents(docs, self.embedder)
        return vectorstore

    def rag(self, query, vectorstore):
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.model,
            retriever=retriever,
            return_source_documents=True
        )
        result = qa_chain(query)
        return result["result"], result["source_documents"]

    def cross_check(self, answer, sources):
        context = "\n\n".join([doc.page_content for doc in sources])
        prompt = (
            "Given the following context from Wikipedia: \n"
            f"{context}\n\n"
            f"And the following answer: \n{answer}\n\n"
            "Does the answer accurately reflect the facts from Wikipedia? "
            "Reply JUST BY 'Yes' or 'No'."
        )
        check = self.model.invoke(prompt)
        return check.content.strip()

    def run(self, query, custom_answer=None):
        docs = self.retrieve_wikipedia(query)
        vectorstore = self.build_vector_db(docs)
        answer, sources = self.rag(query, vectorstore)
        if custom_answer:
            answer = custom_answer
        crosscheck_result = self.cross_check(answer, sources)
        return {
            "Question": query,
            "Answer": answer,
            "Wiki_Source": [doc.page_content for doc in sources],
            "Crosscheck_Result": crosscheck_result
        }

if __name__ == "__main__":
    checker = CrosscheckModule()
    query = "Does Keanu Reeves acted in John Wick series?"
    wrong_answer = 'No. He did not.'
    result = checker.run(query, custom_answer=wrong_answer)
    print(result)
