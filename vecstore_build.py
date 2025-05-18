from PyPDF2 import PdfReader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import glob

#读取文件的路径，嵌入模型，向量库存储位置
pdf_path='./books'
embedding_model="sentence/all-MiniLM-L6-v2"
vecterdb_path='./question_db'

# load pdf text,get txt list
pdf_docs=glob.glob(pdf_path + '/**/*.pdf', recursive=True)
# pdf_docs = ['./books/必修一第一章.pdf']
def read_pdf(pdf_docs):
    text=''
    for pdf in pdf_docs:
        print('loading', pdf)
        pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# split text to chunks
def split_text(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_split = text_splitter.split_text(docs)
    return text_split

#build vectorestore
def get_vectorstore(text_chunks):
    # embeddings = OpenAIEmbeddings(api_key="************")#need moudle 'openai'
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def create_vecdb(pdf_path='./books',vecterdb_path='./question_db'):
    pdf_docs=glob.glob(pdf_path + '/**/*.pdf', recursive=True)
    text=read_pdf(pdf_docs)
    print('splitting text to chunks')
    text_split=split_text(text)
    print("build vectorestore")
    get_vectorstore(text_split).save_local(vecterdb_path)
    print('done')

def main():
    create_vecdb(pdf_path='./books',vecterdb_path='./question_db')
    create_vecdb(pdf_path='./books_tplan',vecterdb_path='./tplan_db')

if __name__ == "__main__":
    main()
