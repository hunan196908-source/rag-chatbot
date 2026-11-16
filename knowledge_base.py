#文件管理的包
import os
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config#其他的包的
import hashlib
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

def check_md5(md5_str:str):
 if not os.path.exists(config.md5_path):
     open(config.md5_path, 'w').close()
     return False
 else:
    for line in open(config.md5_path, 'r', encoding='utf-8').readlines():
        line=line.strip()
        if line==md5_str:
            return True
    return False
def save_md5(md5_str:str):
    with open(config.md5_path, 'a', encoding='utf-8') as f:
        f.write(md5_str+'\n')



def get_md5(input_str:str,encoding='utf-8'):
    str_bytes = input_str.encode(encoding)
    md5_obj=hashlib.md5()
    md5_obj.update(str_bytes)#更新数据并且要将内容转换为16进制
    mde5_hex=md5_obj.hexdigest()#文件得到十六进制字符串
    return mde5_hex



class KnowledgeBaseService:
    def __init__(self):
        os.makedirs(config.persist_directory,exist_ok=True)
        self.chroma=Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model=config.embedding_model),
            persist_directory=config.persist_directory,
        )
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,#分割后的最大长度
            chunk_overlap=config.chunk_overlap,#连续文本间的字符重复数量
            separators=config.separators,#自然段部落划分段落
            length_function=len,
        )#文本分割器的对象

    def upload_by_str(self,data:str,filename):
        md5_hex=get_md5(data)

        if check_md5(md5_hex):
            return"[跳过]内容已经存在字符串"

        if len(data) > config.max_split_char_number:
            knowledge_chunks:list[str]=self.spliter.split_text(data)
        else:
            knowledge_chunks=[data]

        metadata={
        "source":filename,
        "create_time":datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "operator":"胡南"
        }

        self.chroma.add_texts(
            knowledge_chunks,
            metadata=[metadata for _ in range(len(knowledge_chunks))]

        )
        save_md5(md5_hex)

        return"[成功]内容已经成功加载入数据库"

if __name__ == "__main__":
    service=KnowledgeBaseService()
    service.upload_by_str("周杰伦","testfile")




