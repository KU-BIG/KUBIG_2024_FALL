def map_to_educcat2(row):
    if pd.isna(row["EDUCCAT2"]):  # EDUCCAT2가 NaN인 경우만 처리
        if 1 <= row["IREDUHIGHST2"] <= 7:
            return 1  # Less than high school
        elif row["IREDUHIGHST2"] == 8:
            return 2  # High school graduate
        elif 9 <= row["IREDUHIGHST2"] <= 10:
            return 3  # Some college
        elif row["IREDUHIGHST2"] == 11:
            return 4  # College graduate
    return row["EDUCCAT2"]  # 기존 값 유지

# EDUCCAT2 값 채우기
df2["EDUCCAT2"] = df2.apply(map_to_educcat2, axis=1)
df2["EDUCCAT2"].isna().sum() 
df2.drop(columns=["IREDUHIGHST2"], inplace=True)
df2["JBSTATR2"] = df2["JBSTATR2"].fillna(df2["WRKSTATWK2"])
df2["TXEVER"] = df2["TXEVER"].fillna(df2["TXEVRRCVD"])
df2["TXYREVER"] = df2["TXYREVER"].fillna(df2["TXYRRECVD"])
df2.drop(columns=["WRKSTATWK2","TXEVRRCVD", "TXYRRECVD"], inplace=True)
df2['QUESTID2'] = df2['year'].astype(str) + "_" + df2['QUESTID2'].astype(str)

df = pd.read_csv("C:/Users/badr1/Downloads/everyone_combined_data.csv")
df['QUESTID2'] = df['year'].astype(str) + "_" + df['QUESTID2'].astype(str)
df_merged = pd.merge(df, df2, how="inner", left_on="QUESTID2", right_on="QUESTID2")

import pandas as pd
import numpy as np
from scipy.stats import shapiro
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# 데이터 불러오기
data = pd.read_csv("C:/Users/badr1/Downloads/selected_covariates_with_QUESTID2 (1).csv")

# 정규성 검정 및 스케일링 함수 정의
def check_normality_and_scale(df, columns):
    scaler_dict = {}
    for col in columns:
        # Shapiro-Wilk 검정 수행
        stat, p_value = shapiro(df[col])
        print(f"{col} 정규성 검정 p-value: {p_value:.4f}")
        
        # 정규성을 만족하면 StandardScaler, 아니면 MinMaxScaler
        if p_value > 0.05:  # 정규성을 따름
            print(f"{col} -> 정규분포: StandardScaler 적용")
            scaler = StandardScaler()
        else:  # 정규성을 따르지 않음
            print(f"{col} -> 비정규분포: MinMaxScaler 적용")
            scaler = MinMaxScaler()
        
        # 스케일링 수행 (데이터프레임에 수정된 변수만 업데이트)
        df[col] = scaler.fit_transform(df[[col]])
        scaler_dict[col] = scaler
    
    return df, scaler_dict

# 대상 변수 리스트
columns = ['IRHHSIZ2', 'NOBOOKY2', 'CG30EST', 'AL30EST']

# 함수 실행
data, scalers = check_normality_and_scale(data, columns)

# 결과 확인
print("\n스케일링 결과:")
print(data.head())

# 스케일링된 데이터를 파일로 저장
data_filename = "X_scaled_data.csv"
data.to_csv(data_filename, index=False)
print(f"스케일링된 데이터가 {data_filename} 파일로 저장되었습니다.")
