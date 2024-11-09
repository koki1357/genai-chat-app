import os
from azure.storage.blob import BlobServiceClient


def connect_blobDB(connection_string:str, container_name:str) -> BlobServiceClient:
    try:
        # BlobServiceClientを作成
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # 指定したコンテナのクライアントを取得
        container_client = blob_service_client.get_container_client(container_name)
        return container_client
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

if __name__ == '__main__':
    connection_string = os.environ['AZURE_BLOB_CONNECTION_STRING']
    container_name = os.environ['AZURE_BLOB_CONTAINER_NAME']

    test_client = connect_blobDB(connection_string, container_name)
    if test_client:
        print("接続成功")
    else:
        print("接続失敗")
    