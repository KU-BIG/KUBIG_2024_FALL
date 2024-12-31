import os
import zipfile
import json
import pandas as pd
from typing import List
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_upstage import UpstageLayoutAnalysisLoader


# 환경 변수 이름을 정의
API_KEYS = {
    "UPSTAGE_API_KEY": None,
    "LANGCHAIN_API_KEY": None,
    "TAVILY_API_KEY": None
}

''' 환경 변수를 로드하는 함수 정의 '''
def load_env():
    # running in Google Colab
    if "google.colab" in str(get_ipython()):
        from google.colab import userdata
        for key in API_KEYS.keys():
            API_KEYS[key] = os.environ.setdefault(key, userdata.get(key))

    # running in local Jupyter Notebook
    else:
        load_dotenv()  # .env 파일을 로드
        for key in API_KEYS.keys():
            API_KEYS[key] = os.environ.get(key)

    return tuple(API_KEYS.values())

# 환경 변수 값을 로드하여 변수에 저장
UPSTAGE_API_KEY, LANGCHAIN_API_KEY, TAVILY_API_KEY = load_env()


''' pdf 파일 및 사진 파일 폴더 생성 및 옮기기 '''

# Path to the folder containing the files
folder_path = r"C:\Users\wnsgu\Desktop\upstage\cookbook\file"

# Define subfolder paths for categorized files
pdf_folder = os.path.join(folder_path, "pdf")
photo_folder = os.path.join(folder_path, "사진")

# Create subfolders if they do not exist
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(photo_folder, exist_ok=True)

# Function to extract files from ZIP to a new subfolder
def extract_zip(file_path: str, extract_to: str):
    subfolder = os.path.join(extract_to, os.path.splitext(os.path.basename(file_path))[0])
    os.makedirs(subfolder, exist_ok=True)
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(subfolder)
    return subfolder

# Function to convert hwp, hwpx files to PDF (assuming you have an appropriate tool installed)
def convert_to_pdf(file_path: str, output_folder: str) -> str:
    pdf_path = os.path.join(output_folder, os.path.basename(file_path) + ".pdf")
    # Placeholder for conversion logic, you should replace this with actual conversion code.
    # For example, using pyhwp, unoconv, or calling an external script to do the conversion.
    # convert(file_path, pdf_path)
    return pdf_path

# Gather all files from the folder (including extracted ZIP files)
all_files = []

for root, _, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)

        # Extract ZIP files to a new subfolder
        if file.lower().endswith(".zip"):
            try:
                extract_zip(file_path, photo_folder)  # Extract ZIP files to '사진' folder
            except Exception as e:
                print(f"Failed to extract ZIP: {file_path}, reason: {e}")

        # Convert hwp, hwpx files to PDF and save in 'pdf' folder
        elif file.lower().endswith((".hwp", ".hwpx")):
            try:
                pdf_file = convert_to_pdf(file_path, pdf_folder)
                all_files.append(pdf_file)
            except Exception as e:
                print(f"Failed to convert to PDF: {file_path}, reason: {e}")

        # Move PDF files to 'pdf' folder
        elif file.lower().endswith(".pdf"):
            pdf_dest = os.path.join(pdf_folder, os.path.basename(file_path))
            os.rename(file_path, pdf_dest)
            all_files.append(pdf_dest)

        # Move images or Excel files to '사진' folder
        elif file.lower().endswith((".jpg", ".jpeg", ".png", ".xls", ".xlsx")):
            photo_dest = os.path.join(photo_folder, os.path.basename(file_path))
            os.rename(file_path, photo_dest)

''' pdf파일 layoutanalyzer 이용해서 변환 '''

''' UPSTAGE API 사용 - UpstageLayoutAnalysisLoader '''
# Function to analyze PDF files using UpstageLayoutAnalysisLoader
def layout_analysis(filenames: List[str]) -> List[Document]:
    layout_analysis_loader = UpstageLayoutAnalysisLoader(filenames, output_type="html")
    return layout_analysis_loader.load()

# Function to extract files from ZIP to a new subfolder
def extract_zip(file_path: str, extract_to: str):
    subfolder = os.path.join(extract_to, os.path.splitext(os.path.basename(file_path))[0])
    os.makedirs(subfolder, exist_ok=True)
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(subfolder)
    return subfolder

# Function to convert hwp, hwpx files to PDF (assuming you have an appropriate tool installed)
def convert_to_pdf(file_path: str) -> str:
    pdf_path = file_path + ".pdf"
    # Placeholder for conversion logic, you should replace this with actual conversion code.
    # For example, using pyhwp, unoconv, or calling an external script to do the conversion.
    # convert(file_path, pdf_path)
    return pdf_path

# Path to the folder containing the files
folder_path = r"C:\Users\wnsgu\Desktop\upstage\cookbook\file\pdf"

# Gather all files from the folder (including extracted ZIP files)
all_files = []
failed_files = []

for root, _, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)

        # Extract ZIP files to a new subfolder
        if file.lower().endswith(".zip"):
            try:
                new_subfolder = extract_zip(file_path, root)
                # Add extracted files to all_files list
                for sub_root, _, sub_files in os.walk(new_subfolder):
                    all_files.extend([os.path.join(sub_root, sub_file) for sub_file in sub_files])
            except Exception as e:
                failed_files.append({"file": file_path, "reason": f"Failed to extract ZIP: {e}"})
        else:
            all_files.append(file_path)

# Process all files (convert to PDF if necessary)
pdf_files = []
for file_path in all_files:
    if file_path.lower().endswith((".hwp", ".hwpx")):
        try:
            pdf_file = convert_to_pdf(file_path)
            pdf_files.append(pdf_file)
        except Exception as e:
            failed_files.append({"file": file_path, "reason": f"Failed to convert to PDF: {e}"})
    elif file_path.lower().endswith(".pdf"):
        pdf_files.append(file_path)

# Analyze PDFs and keep track of failures
documents = []
for pdf_file in pdf_files:
    try:
        docs = layout_analysis([pdf_file])

        # 파일명 추출
        file_name = os.path.splitext(os.path.basename(pdf_file))[0]  # 확장자를 제거한 파일명 (예: 'Rfffff')

        # 각 Document 객체에 파일명을 title로 추가
        for doc in docs:
            doc.metadata['title'] = file_name

        documents.extend(docs)
    except Exception as e:
        failed_files.append({"file": pdf_file, "reason": f"Failed to analyze layout: {e}"})

# Convert failed files list to DataFrame
failed_files_df = pd.DataFrame(failed_files)

# Save the failed files DataFrame to a CSV
failed_files_csv_path = os.path.join(folder_path, "failed_files.csv")
failed_files_df.to_csv(failed_files_csv_path, index=False)

# Output the results
print(f"Number of successfully processed documents: {len(documents)}")
if not failed_files_df.empty:
    print(f"Number of failed files: {len(failed_files_df)}")
    print(failed_files_df)


''' json으로 변환'''
# documents 리스트를 JSON 형식으로 변환하기
documents_data = []
for doc in documents:
    documents_data.append({
        'content': doc.page_content,  # 문서 내용
        'metadata': doc.metadata      # 메타데이터 (예: title 등)
    })

# 저장 경로 설정
documents_json_path = os.path.join(folder_path, "documents.json")

# JSON 파일로 저장하기
with open(documents_json_path, 'w', encoding='utf-8') as f:
    json.dump(documents_data, f, ensure_ascii=False, indent=4)

# 결과 출력
print(f"Documents saved to: {documents_json_path}")


''' 정책 파일 병합 '''

file_path1='C:/Users/wnsgu/Desktop/upstage/cookbook/poly_words/poly_words/법무부_(생활법률지식)1.법률용어_20191231.csv'
file_path2='C:/Users/wnsgu/Desktop/upstage/cookbook/poly_words/poly_words/생활법령_근로.csv'
file_path3='C:/Users/wnsgu/Desktop/upstage/cookbook/poly_words/poly_words/생활법령_복지.csv'
file_path4='C:/Users/wnsgu/Desktop/upstage/cookbook/poly_words/poly_words/생활법령_주거.csv'
file_path5='C:/Users/wnsgu/Desktop/upstage/cookbook/poly_words/poly_words/주택청약 용어.csv'
file_path6='C:/Users/wnsgu/Desktop/upstage/cookbook/poly_words/poly_words/청년정보 용어사전.csv'

a=pd.read_csv(file_path1, encoding='cp949')
b=pd.read_csv(file_path2)
c=pd.read_csv(file_path3)
d=pd.read_csv(file_path4)
e=pd.read_csv(file_path5)
f=pd.read_csv(file_path6)

a.drop(columns=['용어번호'], inplace=True)
a.rename(columns={'용어명': 'title', '설명': 'text'}, inplace=True)
e.rename(columns={'용어': 'title', '설명': 'text'}, inplace=True)
f.rename(columns={'용어': 'title', '뜻': 'text'}, inplace=True)
result = pd.concat([a, b, c, d, e, f], axis=0, ignore_index=True)
df_sorted = result.sort_values(by='title')
df_sorted.to_csv("df_sorted.csv", index=False)


'''OCR'''
# document ocr을 이용한 파일 정보 가지고오기

# Load API key from .env file
load_dotenv()
api_key = os.getenv("API_KEY")

# Path to the folder containing the image files
folder_path = r"C:\Users\wnsgu\Desktop\upstage\cookbook\file\사진"

# Gather all image files from the folder
image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
image_files = [os.path.join(root, file) for root, _, files in os.walk(folder_path) for file in files if file.lower().endswith(image_extensions)]

# Process each image file with UpstageLayoutAnalysisLoader
documents = []
failed_files = []

for image_file in image_files:
    try:

        ''' UPSTAGE API 사용 - UpstageLayoutAnalysisLoader '''
        # Load the image file with OCR
        layzer = UpstageLayoutAnalysisLoader([image_file], output_type="html", use_ocr=True)

        # Use lazy_load method for better memory efficiency
        docs = layzer.load()  # You can use layzer.lazy_load() if needed

        # Extract filename without extension
        file_name = os.path.splitext(os.path.basename(image_file))[0]

        # Append the result to documents
        for doc in docs:
            doc.metadata['title'] = file_name
            documents.append({
                'content': doc.page_content,  # 문서 내용
                'metadata': doc.metadata      # 메타데이터 (예: title 등)
            })

    except Exception as e:
        # Record the failure for this file
        failed_files.append({"file": image_file, "reason": str(e)})

# Save the results as JSON
documents_json_path = os.path.join(folder_path, "documents.json")
with open(documents_json_path, 'w', encoding='utf-8') as f:
    json.dump(documents, f, ensure_ascii=False, indent=4)

# Save failed files to a CSV
if failed_files:
    failed_files_df = pd.DataFrame(failed_files)
    failed_files_csv_path = os.path.join(folder_path, "failed_files.csv")
    failed_files_df.to_csv(failed_files_csv_path, index=False)

# Output the results
print(f"Number of successfully processed documents: {len(documents)}")
if failed_files:
    print(f"Number of failed files: {len(failed_files)}")
    print(failed_files_df)
    print(f"Failed files saved to: {failed_files_csv_path}")

print(f"Documents saved to: {documents_json_path}")