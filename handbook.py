import streamlit as st
import base64


with open("images/IMteacher使用教程1.0.pdf", "rb") as f:
    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="800" height="1000" type="application/pdf">'
st.markdown(pdf_display, unsafe_allow_html=True)