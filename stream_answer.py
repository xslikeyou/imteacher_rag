from api import chat
from openai import RateLimitError
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model="./all-MiniLM-L6-v2"
vecterdb_path='./question_db'
sys_messages=r"""
你是高中数学老师，擅长回答学生问题,
回答中数学公式输出格式参考：\[\(\frac{x^2}{y}\)+\x\times\y \]

"""

#st.session_state可以定义不被重置的量
def clear_chat_history():
    del st.session_state.messages
    del st.session_state.history

def init_chat_history():
    with st.chat_message("assistant", avatar='🤖'):
        st.markdown("您好，我是IM Teacher，很高兴为您服务,请输入你的数学疑问")
    #展示对话（有些提示词不能展示）
    if "history" in st.session_state:
         for message in st.session_state.history:
            if message["role"] == "user":
                with st.chat_message(message["role"], avatar = '🧑'):
                    st.markdown(message["content"])
            if message["role"] == "assistant":
                with st.chat_message(message["role"],avatar = '🤖'):
                    st.markdown(message["content"]) 
    else:
        st.session_state.history = []
    #传给大模型
    if "messages" not in st.session_state:
        st.session_state.messages = []
    #提前加载知识库,大概两分钟
    if "question_db" not in st.session_state:
        st.session_state.question_db = []

    return st.session_state.history

def stream_ans(history):
    collected_messages = ""
    with st.chat_message("assistant", avatar='🤖'):
        placeholder = st.empty()
        try:
            response = chat(history)
        except RateLimitError as e:
            st.markdown("Ratelimt error")
            st.session_state.history.append({"role": "assistant", "content": "Ratelimt error"})
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content
            if not chunk_message:
                continue
            collected_messages += chunk_message
            placeholder.write(collected_messages)
        collected_messages=collected_messages.replace(r"\(", "$").replace(r"\)", "$").replace(r"\[", "$$").replace(r"\]", "$$")
        placeholder.write(collected_messages)
        return collected_messages


def main():
        init_chat_history()
        if prompt := st.chat_input("Shift + Enter 换行, Enter 发送"):
            with st.chat_message("user", avatar='🧑'):
                st.markdown(prompt)
                
            search_results_string = ""
            with st.spinner("查询知识库……"):
                if st.session_state.question_db:
                    search_results = st.session_state.question_db.similarity_search(prompt, k=2)#result是document
                else:
                    st.write("首次访问需加载知识库...请稍后")
                    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
                    vectorstore = FAISS.load_local(folder_path=vecterdb_path, embeddings=embeddings, allow_dangerous_deserialization=True)
                    st.session_state.question_db = vectorstore
                    st.write("知识库加载完成")
                    search_results = st.session_state.question_db.similarity_search(prompt, k=2)
                for result in search_results:
                    search_results_string += result.page_content + "\n"
            with st.expander("查询结果"):
                st.write(search_results)
            st.session_state.messages.append({ "role": "system","content": search_results_string+sys_messages})
            st.session_state.messages.append({"role": "user", "content":'我的问题:\n'+prompt })
            response=stream_ans(st.session_state.messages)
            st.session_state.history.append({"role": "user", "content": prompt})
            st.session_state.history.append({"role": "assistant", "content": response})
            st.button("清空对话", on_click=clear_chat_history)

if __name__ == "__main__":
    main()