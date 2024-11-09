# chatbot.py
import os
from pathlib import Path
import base64
import clipboard, pyperclip
import streamlit as st
from langchain import hub
from langchain_openai import AzureChatOpenAI
from langchain.schema import (HumanMessage, AIMessage)
# from langchain.chains import LLMChain
# from langchain import PromptTemplate, ChatPrompmtTemplate
from langchain import PromptTemplate
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import UnstructuredMarkdownLoader, TextLoader
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

from utils.connect_blobDB import connect_blobDB
from utils.split_pdf import process_pdf_from_blob
from utils.keywords_pdf_mapping import load_keyword_mapping, find_matching_files
from utils.custom_notifications import custom_notification
from ui_parts.streamlit_clipboard_with_chat import chat_message_with_copy

# .envファイル読み込み
load_dotenv()

# テンプレートファイル読み込み
def load_template(file_path):
    """テンプレートファイルを読み込み、各行の先頭の空白のみを削除します。

    lstrip()を使用:
    - strip()と違い、行末の空白や改行を保持
    - テンプレートの構造（インデント、空行）を維持しつつ、不要な行頭の空白を除去
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return ''.join(line.lstrip() for line in file)
    except FileNotFoundError:
        st.error(f"テンプレートファイルが見つかりません: {file_path}")
        return None
    except Exception as e:
        st.error(f"テンプレートの読み込み中にエラーが発生しました: {e}")
        return None


def on_copy_click(text):
    st.session_state.copied.append(text)
    pyperclip.copy(text)


def main():
    st.set_page_config(
        page_title="メール返信・画像読み込みAI",
        page_icon="🤖"
    )
    reply_email=os.environ['PULL_OPTION_REPLY_EMAIL']
    reply_from_picture= os.environ['PULL_OPTION_REPLY_FROM_PICTURE']
    # reply_from_email_using_pdfinfo = os.environ['PULL_OPTION_REPLY_FROM_EMAIL_USING_PDF']
    reply_from_email_using_pdfinfo = os.environ['PULL_OPTION_REPLY_FROM_EMAIL_USING_PDFINFO']
    task = st.sidebar.selectbox(
    'AIに実施させたいタスクを選んでください！',
    (reply_from_email_using_pdfinfo, reply_email, reply_from_picture)
    )
    if task == reply_email:
    # メール返信AIの処理
        # chain = initialize_chain() # RAGを使う際に利用する
        llm = AzureChatOpenAI(
            azure_endpoint= os.environ['AZURE_OPEN_AI_END_POINT'],
            openai_api_version="2023-03-15-preview",
            # openai_api_version="2023-12-01-preview",
            deployment_name= os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'],
            openai_api_key= os.environ['AZURE_OPEN_AI_API_KEY'],
            openai_api_type="azure",
        )

        # ページの設定
        st.header(reply_email+" 🤖")
        nortification_contents_nouse_webcontents = load_template(Path(__file__).parent.parent / "resources" / "text" / "nortification_contents_nouse_webcontents.txt")
        custom_notification('warning', nortification_contents_nouse_webcontents)

        # チャット履歴の初期化
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # テンプレートファイルのパスを設定
        template_path = Path(__file__).parent.parent / "resources" / "email_template_content.txt"
        email_template_content = load_template(template_path)
        if email_template_content is None:
            return

        # プロンプトテンプレートを格納
        template = f"""
    
        {email_template_content}
        
        ## 受信したメール
        {{received_mail}}
        """
        
        
        # ユーザーの入力を監視
        if user_input := st.chat_input("メールの内容を入力してください。"):
            st.session_state.messages.append(HumanMessage(content=user_input))
            with st.spinner("GPTが返信を生成しています..."):
                doctor_response_template = PromptTemplate(
                    input_variables=["received_mail"],
                    template=template,
                    )
                doctor_response_template.format(received_mail=user_input)
                # print(user_input, type(user_input))
                # print(doctor_response_template)
                # print(type(doctor_response_template.format(received_mail=user_input)))
                response = llm.invoke(doctor_response_template.format(received_mail=user_input))
            st.session_state.messages.append(AIMessage(content=response.content))
    
        # チャット履歴の表示
        messages = st.session_state.get('messages', [])
        for message in messages:
            if isinstance(message, AIMessage):
                with st.chat_message('assistant'):
                    st.markdown(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message('user'):
                    st.markdown(message.content)
            else:
                st.write(f"System message: {message.content}")

    elif task == reply_from_email_using_pdfinfo:
        keywords_pdf_mapping_csv_file = Path(__file__).parent.parent / "resources" / "csv" / "keywords_pdf_mapping.csv"
        keyword_mapping = load_keyword_mapping(keywords_pdf_mapping_csv_file)
        pdfs_keyword_mapping  = {value:key for key, value in keyword_mapping.items()}

        container_client = connect_blobDB(
            connection_string=os.environ['AZURE_BLOB_CONNECTION_STRING'],
            container_name=os.environ['AZURE_BLOB_CONTAINER_NAME']
        )
            
        # メール返信AIの処理
        # chain = initialize_chain() # RAGを使う際に利用する
        llm = AzureChatOpenAI(
            azure_endpoint= os.environ['AZURE_OPEN_AI_END_POINT_CHAT'],
            openai_api_version="2023-03-15-preview",
            # openai_api_version="2023-12-01-preview",
            deployment_name= os.environ['AZURE_OPENAI_DEPLOYMENT_NAME_CHAT'],
            openai_api_key= os.environ['AZURE_OPEN_AI_API_KEY_CHAT'],
            openai_api_type="azure",
        )
        # ページの設定
        st.header(reply_from_email_using_pdfinfo+" 🤖")
        nortification_contents_use_webcontents = load_template(Path(__file__).parent.parent / "resources" / "text" / "nortification_contents_use_webcontents.txt")
        custom_notification('success', nortification_contents_use_webcontents)

        # チャット履歴の初期化
        # 人 or AIのメッセージ
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # 検索キーワード＋PDF名
        if "search_document" not in st.session_state:
            st.session_state.search_document = []
        
        # クリップボードに格納する文言
        if "copied" not in st.session_state: 
            st.session_state.copied = []

        # テンプレートファイルのパスを設定
        template_path = Path(__file__).parent.parent / "resources" / "email_template_content.txt"
        email_template_content = load_template(template_path)
        if email_template_content is None:
            return
                
        # プロンプトテンプレートを格納
        template = f"""
        ## 事前情報
        {{pdf_info}}
        
        {email_template_content}

        ## 受信したメール
        {{received_mail}}
        """
        
        # ユーザーの入力を監視
        if user_input := st.chat_input("メールの内容を入力してください。"):
            st.session_state.messages.append(HumanMessage(content=user_input))
            
            if container_client:
                pdf_blob_name = find_matching_files(user_input, keyword_mapping)[0] #一つのファイルに限定
                documents = process_pdf_from_blob(container_client, pdf_blob_name)
                pdf_info = "".join(documents) if documents else "事前情報なし"

            with st.spinner("GPTが返信を生成しています..."):
                doctor_response_template = PromptTemplate(
                    input_variables=["received_mail", "pdf_info"],
                    template=template,
                    )
                doctor_response_template.format(received_mail=user_input, pdf_info=pdf_info)
                # print(user_input, type(user_input))
                # print(doctor_response_template)
                # print(type(doctor_response_template.format(received_mail=user_input)))
                response = llm.invoke(doctor_response_template.format(received_mail=user_input, pdf_info=pdf_info))
                # st.session_state.copied.append(response.content)

            st.session_state.messages.append(AIMessage(content=response.content))

            if pdf_blob_name == "":
                st.session_state.search_document.append(AIMessage(content="キーワード：なし  \n参照ファイル：なし"))
            else:
                st.session_state.search_document.append(AIMessage(content="キーワード：{}  \n参照ファイル：{}".format(str(pdfs_keyword_mapping[pdf_blob_name]), str(pdf_blob_name))))


        # チャット履歴の表示
        messages = st.session_state.get('messages', [])
        search_documents = st.session_state.get('search_document', [])
        copied = st.session_state.get("copied", [])
        # for message in messages:
        for i in range(len(messages)):
            # if isinstance(message, AIMessage):
            if isinstance(messages[i], AIMessage):
                with st.chat_message('assistant'):
                    # st.markdown(message.content)
                    st.markdown(messages[i].content)
                    chat_message_with_copy(messages[i].content)
                # st.button("📋", on_click=on_copy_click, args=(messages[i].content,))
                # st.code(messages[i].conte)nt)
                with st.chat_message('assistant'):                        
                    st.markdown(search_documents[i//2].content)
            # elif isinstance(message, HumanMessage):
            elif isinstance(messages[i], HumanMessage):
                with st.chat_message('user'):
                    # st.markdown(message.content)
                    st.markdown(messages[i].content)
            else:
                # st.write(f"System message: {message.content}")
                st.write(f"System message: {messages[i].content}")
    
    elif task == reply_from_picture:
        st.header(reply_from_picture+" 🤖")
        image_template = """
        下記の画像について説明して下さい
        
        {image_base64}
        """


        if uploaded_image := st.file_uploader('画像をアップロードして下さい。(拡張子: png, jpg, jpeg)', type=['png', 'jpg', 'jpeg']):
            pass
            # uploaded_image_base64 = str(base64.b64encode(uploaded_image).decode('utf-8'))
            
        #     image_responce_template = ChatPrompmtTemplate.from_messages([
        #         SystemMessages(c)

        #     ])
        
        # ユーザーの入力を監視
        if user_input := st.chat_input("【※現在作成中】アップロード画像に関連したチャット機能は現在作成中です"):
            st.session_state.messages.append(HumanMessage(content=user_input))
            with st.spinner("GPTが返信を生成しています..."):
                doctor_response_template = PromptTemplate(
                    input_variables=["received_mail"],
                    template=template,
                    )
                doctor_response_template.format(received_mail=user_input)
                # print(user_input, type(user_input))
                # print(doctor_response_template)
                # print(type(doctor_response_template.format(received_mail=user_input)))
                response = llm.invoke(doctor_response_template.format(received_mail=user_input))
            st.session_state.messages.append(AIMessage(content=response.content))
    
        # チャット履歴の表示
        messages = st.session_state.get('messages', [])
        for message in messages:
            if isinstance(message, AIMessage):
                with st.chat_message('assistant'):
                    st.markdown(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message('user'):
                    st.markdown(message.content)
            else:
                st.write(f"System message: {message.content}")


if __name__ == '__main__':
    # print("hello")
    main()