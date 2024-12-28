import gdown
import zipfile
import os

# C:/youth_policy 경로가 없다면 생성
output_dir = "C:/youth_policy"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Google Drive 파일 ID (Google Drive 공유 링크에서 추출 가능)
file_id = "1gsnBybXP8OOP3PldFdi6F8yhGCL-cy5k" 

# 다운로드 받을 파일 경로 설정
zip_file_path = os.path.join(output_dir, "chroma_db.zip")

# Google Drive에서 .zip 파일 다운로드
gdown.download(f"https://drive.google.com/uc?id={file_id}", zip_file_path, quiet=False)

# .zip 파일의 압축 풀기
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(output_dir)

print("Download and extraction complete.")