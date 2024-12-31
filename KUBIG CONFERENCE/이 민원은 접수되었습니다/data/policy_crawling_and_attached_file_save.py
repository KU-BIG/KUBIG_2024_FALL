import requests
import xml.etree.ElementTree as ET
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import glob


# API URL 및 인증키
url = "https://www.youthcenter.go.kr/opi/youthPlcyList.do"
openApiVlak = "7cee014e92a6c9ea4875d926"  # 발급받은 인증키


# 요청 파라미터 설정 (초기값)
params = {
    "openApiVlak": openApiVlak,
    "display": 100,  # 출력 건수
    "pageIndex": 1,  # 조회할 페이지
    "srchPolicyId": "",
    "query": "",
    "bizTycdSel": "023020,023040",  # 정책유형 코드
    "srchPolyBizSecd": ""
}

# XML과 CSV 데이터를 저장할 파일명
output_xml_file = "policies.xml"
output_csv_file = "youth_policies.csv"

# 모든 정책 정보를 저장할 리스트 (CSV용)
policies_data = []

# 모든 페이지 데이터를 수집하여 저장 (XML, CSV 둘 다)
with open(output_xml_file, 'w', encoding='utf-8') as xml_file:
    while True:
        # API 호출
        response = requests.get(url, params=params)

        if response.status_code == 200:
            # 응답을 텍스트로 받아옴
            xml_data = response.text

            # XML 데이터를 파일에 저장
            xml_file.write(xml_data)
            xml_file.write("\n\n")  # 페이지 간 구분을 위한 빈 줄 추가

            # XML 파싱
            root = ET.fromstring(xml_data)

            # 첫 번째 페이지에서 총 데이터 수 확인
            if params["pageIndex"] == 1:
                total_count = int(root.findtext(".//totalCnt"))
                print(f"총 데이터 수: {total_count}")

            # 현재 페이지 인덱스와 표시된 항목 수 확인
            page_index = int(root.findtext(".//pageIndex"))
            item_count = len(root.findall(".//youthPolicy"))

            print(f"페이지 {page_index}에서 {item_count}개의 항목을 가져왔습니다.")

            # 정책 데이터 추출하여 CSV용 리스트에 저장
            for item in root.findall(".//youthPolicy"):
                policy_info = {child.tag: child.text for child in item}  # 모든 자식 요소를 딕셔너리로 변환
                policies_data.append(policy_info)

            # 마지막 페이지인지 확인 (totalCnt와 display로 계산한 마지막 페이지까지 확인)
            if page_index * params["display"] >= total_count:
                print("모든 데이터를 수집했습니다.")
                break

            # 다음 페이지로 넘어감
            params["pageIndex"] += 1
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

# 수집한 데이터를 DataFrame으로 변환
df = pd.DataFrame(policies_data)

# CSV 파일로 저장
df.to_csv(output_csv_file, index=False, encoding='utf-8-sig')
print(f"모든 정책 데이터를 XML 파일 '{output_xml_file}'과 CSV 파일 '{output_csv_file}'에 저장했습니다.")

# 첨부파일 다운로드 -1
chrome_options = Options()
output_folder = os.path.abspath('file')  # 절대 경로로 변경
os.makedirs(output_folder, exist_ok=True)

# 다운로드 위치 설정
prefs = {
    "download.default_directory": output_folder,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
}
chrome_options.add_experimental_option("prefs", prefs)

# ChromeDriverManager를 통해 ChromeDriver를 자동 설치 및 경로 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # CSV 파일 읽기
    df = pd.read_csv('youth_policies.csv')

    # 첫 번째 1/4 데이터 처리
    first_quarter_df = df.iloc[:len(df) // 4]

    # 유효한 행 필터링
    valid_rows = first_quarter_df[first_quarter_df['etct'].notnull() &
                                  (first_quarter_df['etct'] != '') &
                                  (first_quarter_df['etct'] != '-')]

    for _, row in valid_rows.iterrows():
        bizId = row['bizId']
        url = f"https://www.youthcenter.go.kr/youngPlcyUnif/youngPlcyUnifDtl.do?bizId={bizId}"

        driver.get(url)

        try:
            file_link_xpath = '//*[@id="content"]/div[1]/div[10]/ul/li[6]/div[2]/div/a'
            file_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, file_link_xpath))
            )
            file_link.click()
            time.sleep(5)

            downloaded_files = glob.glob(os.path.join(output_folder, '*'))
            downloaded_file_name = max(downloaded_files, key=os.path.getctime) if downloaded_files else None

            if downloaded_file_name:
                file_extension = os.path.splitext(downloaded_file_name)[1]
                new_file_path = os.path.join(output_folder, f"{bizId}{file_extension}")
                os.rename(downloaded_file_name, new_file_path)
                print(f"첫 번째 1/4: 파일이 '{new_file_path}'로 변경되었습니다.")
            else:
                print("다운로드된 파일을 찾을 수 없습니다.")

        except Exception as e:
            print(f"첫 번째 1/4: 오류 발생: {e}")

finally:
    driver.quit()

# 첨부파일 다운로드 - 2

# 이전 코드를 그대로 복사한 후 변경할 부분만 추가
try:
    df = pd.read_csv('youth_policies.csv')

    # 두 번째 1/4 데이터 처리
    second_quarter_df = df.iloc[len(df) // 4:len(df) // 2]

    valid_rows = second_quarter_df[second_quarter_df['etct'].notnull() & (second_quarter_df['etct'] != '') & (second_quarter_df['etct'] != '-')]

    for _, row in valid_rows.iterrows():
        bizId = row['bizId']
        url = f"https://www.youthcenter.go.kr/youngPlcyUnif/youngPlcyUnifDtl.do?bizId={bizId}"

        driver.get(url)

        try:
            file_link_xpath = '//*[@id="content"]/div[1]/div[10]/ul/li[6]/div[2]/div/a'
            file_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, file_link_xpath))
            )
            file_link.click()
            time.sleep(5)

            downloaded_files = glob.glob(os.path.join(output_folder, '*'))
            downloaded_file_name = max(downloaded_files, key=os.path.getctime) if downloaded_files else None

            if downloaded_file_name:
                file_extension = os.path.splitext(downloaded_file_name)[1]
                new_file_path = os.path.join(output_folder, f"{bizId}{file_extension}")
                os.rename(downloaded_file_name, new_file_path)
                print(f"두 번째 1/4: 파일이 '{new_file_path}'로 변경되었습니다.")
            else:
                print("다운로드된 파일을 찾을 수 없습니다.")

        except Exception as e:
            print(f"두 번째 1/4: 오류 발생: {e}")

finally:
    driver.quit()

# Chrome 옵션 설정
chrome_options = Options()
output_folder = os.path.abspath('file')  # 절대 경로로 변경
os.makedirs(output_folder, exist_ok=True)

# 다운로드 위치 설정
prefs = {
    "download.default_directory": output_folder,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
}
chrome_options.add_experimental_option("prefs", prefs)

# ChromeDriverManager를 통해 ChromeDriver를 자동 설치 및 경로 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 이전 코드를 그대로 복사한 후 변경할 부분만 추가
try:
    df = pd.read_csv('youth_policies.csv')

    # 세 번째 1/4 데이터 처리
    third_quarter_df = df.iloc[len(df) // 2:(len(df) // 4) * 3]

    valid_rows = third_quarter_df[third_quarter_df['etct'].notnull() & (third_quarter_df['etct'] != '') & (third_quarter_df['etct'] != '-')]

    for _, row in valid_rows.iterrows():
        bizId = row['bizId']
        url = f"https://www.youthcenter.go.kr/youngPlcyUnif/youngPlcyUnifDtl.do?bizId={bizId}"

        driver.get(url)

        try:
            file_link_xpath = '//*[@id="content"]/div[1]/div[10]/ul/li[6]/div[2]/div/a'
            file_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, file_link_xpath))
            )
            file_link.click()
            time.sleep(5)

            downloaded_files = glob.glob(os.path.join(output_folder, '*'))
            downloaded_file_name = max(downloaded_files, key=os.path.getctime) if downloaded_files else None

            if downloaded_file_name:
                file_extension = os.path.splitext(downloaded_file_name)[1]
                new_file_path = os.path.join(output_folder, f"{bizId}{file_extension}")
                os.rename(downloaded_file_name, new_file_path)
                print(f"세 번째 1/4: 파일이 '{new_file_path}'로 변경되었습니다.")
            else:
                print("다운로드된 파일을 찾을 수 없습니다.")

        except Exception as e:
            print(f"세 번째 1/4: 오류 발생: {e}")

finally:
    driver.quit()

# Chrome 옵션 설정
chrome_options = Options()
output_folder = os.path.abspath('file')  # 절대 경로로 변경
os.makedirs(output_folder, exist_ok=True)

# 다운로드 위치 설정
prefs = {
    "download.default_directory": output_folder,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
}
chrome_options.add_experimental_option("prefs", prefs)

# ChromeDriverManager를 통해 ChromeDriver를 자동 설치 및 경로 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 이전 코드를 그대로 복사한 후 변경할 부분만 추가
try:
    df = pd.read_csv('youth_policies.csv')

    # 네 번째 1/4 데이터 처리
    fourth_quarter_df = df.iloc[(len(df) // 4) * 3:]

    valid_rows = fourth_quarter_df[fourth_quarter_df['etct'].notnull() & (fourth_quarter_df['etct'] != '') & (fourth_quarter_df['etct'] != '-')]

    for _, row in valid_rows.iterrows():
        bizId = row['bizId']
        url = f"https://www.youthcenter.go.kr/youngPlcyUnif/youngPlcyUnifDtl.do?bizId={bizId}"

        driver.get(url)

        try:
            file_link_xpath = '//*[@id="content"]/div[1]/div[10]/ul/li[6]/div[2]/div/a'
            file_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, file_link_xpath))
            )
            file_link.click()
            time.sleep(5)

            downloaded_files = glob.glob(os.path.join(output_folder, '*'))
            downloaded_file_name = max(downloaded_files, key=os.path.getctime) if downloaded_files else None

            if downloaded_file_name:
                file_extension = os.path.splitext(downloaded_file_name)[1]
                new_file_path = os.path.join(output_folder, f"{bizId}{file_extension}")
                os.rename(downloaded_file_name, new_file_path)
                print(f"네 번째 1/4: 파일이 '{new_file_path}'로 변경되었습니다.")
            else:
                print("다운로드된 파일을 찾을 수 없습니다.")

        except Exception as e:
            print(f"네 번째 1/4: 오류 발생: {e}")

finally:
    driver.quit()