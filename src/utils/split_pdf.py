from azure.storage.blob import ContainerClient
from pypdf import PdfReader
import io
from typing import List


def process_pdf_from_blob(container_client: ContainerClient, pdf_blob_name: str) -> List[str] | None:
    try:
        # Blobクライアントを取得
        blob_client = container_client.get_blob_client(pdf_blob_name)

        # PDFファイルをダウンロード
        pdf_data = blob_client.download_blob().readall()

        # BytesIOオブジェクトを作成
        pdf_file = io.BytesIO(pdf_data)

        # PDFを読み込む
        pdf_reader = PdfReader(pdf_file)

        # ページごとに分割
        documents = []
        for page in pdf_reader.pages:
            documents.append(page.extract_text())

        print(f"{pdf_blob_name}を{len(documents)}ページに分割しました。")
        return documents

    except Exception as ex:
        print(f"エラーが発生しました: {ex}")
        return None

# 使用例
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from connect_blobDB import connect_blobDB
    from keywords_pdf_mapping import load_keyword_mapping, find_matching_files

    load_env()

    connection_string=os.environ['AZURE_BLOB_CONNECTION_STRING']
    container_name=os.environ['AZURE_BLOB_CONTAINER_NAME']
    csv_file = "resources/csv/keywords_pdf_mapping.csv"
    
    keyword_mapping = load_keyword_mapping(csv_file)
    print(keyword_mapping)
    
    input_text = input("テキストを入力してください: ")
    pdf_blob_name = find_matching_files(input_text, keyword_mapping)[0] #一つのファイルに限定
    
    container_client = connect_blobDB(connection_string, container_name)
    
    if container_client:
        documents = process_pdf_from_blob(container_client, pdf_blob_name)
        if documents:
            print(f"PDFの処理に成功しました。{len(documents)}ページが抽出されました。")
            # ここでresult（ページごとのテキスト）を使用して追加の処理を行うことができます            
            documents = "".join(documents)
            # print(documents)
        else:
            print(documents)
            print("PDFの処理に失敗しました。")
    else:
        print("Blob Storageへの接続に失敗しました。")
