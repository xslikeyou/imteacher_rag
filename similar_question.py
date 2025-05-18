
import re
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from stream_answer import stream_ans
embedding_model="./all-MiniLM-L6-v2"
vecterdb_path='./question_db'

def init_chat_history():
    st.write("请输入问题和答案，我将尝试生成相似的题目")
    #提前加载知识库,大概两分钟
    if "question_db" not in st.session_state:
        st.session_state.question_db = None
# 提示词参考  https://github.com/codelion/optillm/blob/main/optillm/cot_reflection.py
def cot(system_prompt, user_prompt):
    cot_prompt = """
    {}
    你是数学命制题目小能手
    你擅长使用思维链（Chain of Thought，简称CoT）方法并结合反思来完成数学题目命制。遵循以下步骤:

    1. 在<analysis>标签内分析知识点，以及答案的思想方法
    2. 在 <thinking> 根据分析出的知识点，以及思想方法命制题目。
    3. 在 <reflection> 标签内反思你<thinking>内容，检查其中是否存在错误或可以改进的地方。
    4. 根据你的反思进行必要的调整
    5. 在 <output> 标签内提供你最终简洁的答案。

    请按照以下格式进行回答：
    <analysis>
    [你对题目的知识点分析，分析]
    </analysis>
    <thinking>
    [你的命题过程写在这里。这是你的命制题目的尝试，不是最终题目。]
    <reflection>
    [你对你命制的题目进行反思，检查其中是否存在错误或可以改进的地方]
    </reflection>
    [根据你命制的题目做的任何调整]
    </thinking>
    <output>
    [你命制的最终题目]
    </output>
    """.format(system_prompt)
    history=[
            {"role": "system", "content": cot_prompt},
            {"role": "user", "content": user_prompt}
        ]
    response = stream_ans(history)
    return response
   


def main():
        init_chat_history()
        if prompt := st.chat_input("请输入问题和答案"):
            with st.chat_message("user", avatar='🧑'):
                st.markdown(prompt)
            search_results_string = ""
            st.write("查询知识库……")
            if  st.session_state.question_db:
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
            response=cot(search_results_string,prompt+'无需解答题目，根据已有信息命制类似的题目')
             # 输出思考结果
            if response:
                match = re.search(r"<output>(.*?)(?:</output>|$)", response, re.DOTALL)
                result= match.group(1).strip() if match else response
                with st.chat_message("assistant", avatar='🤖'):
                    st.markdown(result)
                return result
            else: return ""
            
            
if __name__ == "__main__":
    main()