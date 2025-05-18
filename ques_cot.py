from stream_answer import stream_ans
from openai import RateLimitError
import streamlit as st
import re

sys_messages=r"""
你是高中数学老师，擅长回答学生问题,
回答中数学公式输出格式参考：\[\(\frac{x^2}{y}\)+\x\times\y \]

"""
#st.session_state可以定义不被重置的量
def clear_chat_history():
    del st.session_state.history

def init_chat_history():
    with st.chat_message("assistant", avatar='🤖'):
        st.markdown("您好，我 是IM Teacher，很高兴为您服务")
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
    return st.session_state.history

# 提示词参考  https://github.com/codelion/optillm/blob/main/optillm/cot_reflection.py
def cot(system_prompt, user_prompt):
    cot_prompt = """
    {}
    你是一个使用思维链（Chain of Thought，简称 CoT）方法并结合反思来回答问题的人工智能助手。请按照以下步骤操作：

    1. 在 `<thinking>` 标签内，逐步思考问题。
    2. 在 `<reflection>` 标签内，反思你的思考过程，检查是否有错误或可以改进的地方。
    3. 根据你的反思，进行必要的调整。
    4. 在 `<output>` 标签内，提供你最终简洁的答案。

    **重要提示**：`<thinking>` 和 `<reflection>` 部分仅用于你自己的内部推理过程。不要在这些部分包含任何最终答案的内容。对查询的实际回答必须完全包含在 `<output>` 标签内。

    请按照以下格式给出你的回答：

    <thinking>
    [你的逐步推理过程写在这里。这是你的内部思考过程，不是最终答案。]
    <reflection>
    [你对自己推理过程的反思，检查是否有错误或可以改进的地方]
    </reflection>
    [根据你的反思对思考过程做出的任何调整]
    </thinking>
    <output>
    [你对查询的最终简洁回答。这将是唯一展示给用户的内容。]
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
        if prompt := st.chat_input("Shift + Enter 换行, Enter 发送"):
            with st.chat_message("user", avatar='🧑'):
                st.markdown(prompt)
            response=cot(sys_messages,prompt)
             # 输出思考结果
            if response:
                match = re.search(r"<output>(.*?)(?:</output>|$)", response, re.DOTALL)
                result= match.group(1).strip() if match else response
                st.session_state.history.append({"role": "user", "content": prompt})
                st.session_state.history.append({"role": "assistant", "content": response})
                st.session_state.history.append({"role": "assistant", "content": result})
                st.button("清空对话", on_click=clear_chat_history)
                with st.chat_message("assistant", avatar='🤖'):
                    st.markdown(result)
                return result
            else: return ""

if __name__ == "__main__":
    main()