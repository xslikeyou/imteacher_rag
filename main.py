import streamlit as st
import sys
import types

# 修复 torch.classes 被 Streamlit 监视时报错的问题
if 'torch.classes' in sys.modules:
    sys.modules['torch.classes'].__path__ = types.SimpleNamespace(_path=[])

st.set_page_config(page_title="IM Teacher", page_icon="images/logo.png")
st.title("IM Teacher")
st.logo("images/logo.png")


def main():
    #st.Page创建页面
    qa_page = st.Page("stream_answer.py", title="RAG问答",icon="💡")
    cot_page=st.Page("ques_cot.py",title="COT问答")
    ocr_page = st.Page("ques_ocr.py", title="题目识别")
    similarq_page=st.Page("similar_question.py",title="相似题目生成")
    tplan_page=st.Page("teach_plan_helper.py",title="教案助手")
    ziliao_page=st.Page("source_link.py",title="资源库")
    caozuo_page=st.Page("handbook.py",title="操作手册")
    pg = st.navigation([qa_page,cot_page,ocr_page, similarq_page,tplan_page,ziliao_page,caozuo_page])   
    pg.run()
        


if __name__ == "__main__":
    main()
