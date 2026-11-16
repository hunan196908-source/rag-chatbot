# 创建 web 端页面
import time
import streamlit as st
from knowledge_base import KnowledgeBaseService
st.title("知识数据库更新")  # 在 web 端添加标题

# 上传文件（限制 txt，单个）
uploader_file = st.file_uploader(
    label="Upload your file",
    type=['txt'],
    accept_multiple_files=False,
)

#里面是个字典
if "service" not in st.session_state:
    st.session_state["service"] =KnowledgeBaseService()

if uploader_file is not None:
    file_name:str = uploader_file.filename
    file_type = uploader_file.content_type
    file_size = uploader_file.size / 1024  # 转成 KB
    file_content = uploader_file.getvalue().decode("utf-8")

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | 大小: {file_size:.2f} KB")

    st.text_area("文件内容", file_content, height=300)
    with st.spinner("载入知识库中。。。。"):
        time.sleep(1)
    result=st.session_state["service"].upload_by_str(file_content,file_name)
    st.write(result)