md5_path="./md5.text"
collection_name="rag"
persist_directory="./chroma_db"
embedding_model="text-embedding-v4"

#spliter  文本分割器相关的
chunk_size=500
chunk_overlap=50
separators=["，","。","？","！","；",]

# 超过该字符数才做分段，否则整段作为一条知识
max_split_char_number=1000


similarity_threshold=1   #检索文档的数量


embedding_model_name="text-embedding-v4"
chat_model_name="qwen-max"

session_config={
    "configurable":{
        "session_id":"user_001"
    }

}