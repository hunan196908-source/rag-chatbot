from operator import itemgetter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
import config_data as config
from vector_stores import VectorStoryService
from file_history import get_history


class RagService(object):
    def __init__(self):
        self.service = VectorStoryService(
            embedding=DashScopeEmbeddings(model=config.embedding_model),
        )

        self.prompt_template = ChatPromptTemplate(
            [
                ("system", "以我提供的已知的参考资料为主,"
                           "简洁和专业的回答用户的问题。参考资料；{context}"),
                ("system", "并且向我提问"),
                MessagesPlaceholder(variable_name="history"),
                ("user", "请输入对话{input}"),
            ]
        )

        self.chat_model = ChatTongyi(model=config.chat_model_name)

        self.chain = self._get_chain()

    def _get_chain(self):
        retriever = self.service.get_retriever()

        def format_prompt(docs: list[Document]):
            if not docs:
                return "无可奉告"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档的片段：{doc.page_content}\n文档元素库；{doc.metadata}\n\n"

            return formatted_str

        chain = (
            {
                "input": itemgetter("input"),
                "context": itemgetter("input") | retriever | format_prompt,
                "history": itemgetter("history"),
            } | self.prompt_template | self.chat_model | StrOutputParser()
        )
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        return chain_with_history

if __name__=="__main__":
    res=RagService().chain.invoke(
        {"input": "体重180，尺码推荐"}, config=config.session_config
    )
    print(res)
