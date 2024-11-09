from azure.storage.blob import ContainerClient
from pypdf import PdfReader
import io
import csv
import re
from typing import Dict, List, Tuple


def load_keyword_mapping(csv_file: str) -> Dict[str, str]:
    mapping = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ
        for row in reader:
            if len(row) >= 2:
                filename, keyword = row[0], row[1]
                mapping[keyword.lower()] = filename
    return mapping

def process_complex_keyword(keyword: str) -> Tuple[List[str], List[str]]:
    parts = re.split(r'\s+(and|or)\s+', keyword.lower())
    conditions = parts[::2]
    operators = parts[1::2]
    return conditions, operators

def match_complex_keyword(text: str, complex_keyword: str) -> bool:
    conditions, operators = process_complex_keyword(complex_keyword)
    matched = [condition in text.lower() for condition in conditions]
    
    result = matched[0]
    for i, op in enumerate(operators):
        if op == 'and':
            result = result and matched[i+1]
        elif op == 'or':
            result = result or matched[i+1]
    
    return result

def find_matching_files(text:str, keyword_mapping: Dict[str, str]) -> List[str]:
    matching_files = []
    for keyword, filename in keyword_mapping.items():
        if ' and ' in keyword or ' or ' in keyword:
            if match_complex_keyword(text, keyword):
                matching_files.append(filename)
        elif keyword.lower() in text.lower():
            matching_files.append(filename)
    # インプットとキーワードがマッチしない時は、空文字を付与して返却する
    if matching_files == []:
        matching_files.append("")
    return matching_files


if __name__ == "__main__":
    csv_file = "resources/csv/keywords_pdf_mapping.csv"
    keyword_mapping = load_keyword_mapping(csv_file)
    
    input_text = input("テキストを入力してください: ")
    matching_files = find_matching_files(input_text, keyword_mapping)

    print("マッチしたファイル:", matching_files)
