# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
import faiss

class DailyRecommendationSystem:
    def __init__(self, embedding_model='snunlp/KR-SBERT-V40K-klueNLI-augSTS',
                 bart_tokenizer='gogamza/kobart-base-v2', bart_model='gogamza/kobart-base-v2'):
        # 데이터 로드
        self.wedding_data = pd.read_csv('daily_final.csv')
        
        # 모델 로드
        self.sentence_model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained('./kogpt2-base-v2')
        self.kogpt = GPT2LMHeadModel.from_pretrained('./kogpt2-base-v2')

        # 패딩 토큰 설정
        if self.tokenizer.pad_token is None:
            self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
            self.kogpt.resize_token_embeddings(len(self.tokenizer))

        # 임베딩 생성
        self.wedding_data['embeddings'] = list(
            self.sentence_model.encode(self.wedding_data['색감_분위기_통합'].tolist()))
        self.embeddings = np.array(self.wedding_data['embeddings'].tolist())

        # FAISS 인덱스 초기화
        self.dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(self.embeddings)

    def extract_keywords_from_text(self, user_input: str) -> str:
        prompt = f"""
        아래 문장에서 주요 키워드(색감, 분위기, 동작, 배경)를 추출하세요:
        입력: {user_input}
        출력: 분위기: <분위기>, 동작: <동작>, 배경: <배경>.
        """
        input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=256).input_ids
        output_ids = self.kogpt.generate(input_ids, max_length=100, num_beams=4, early_stopping=True)
        output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return output

    def recommend_photographers(self, user_embedding, top_k=3, mood_filter=None):
        """추천 로직 구현"""
        filtered_data = self.wedding_data
        if mood_filter:
            filtered_data = filtered_data[filtered_data['색감_분위기_통합'].str.contains(mood_filter, na=False)]

        if filtered_data.empty:
            filtered_data = self.wedding_data  # 필터 결과가 없으면 전체 데이터 사용

        filtered_embeddings = np.array(filtered_data['embeddings'].tolist())
        filtered_index = faiss.IndexFlatL2(self.dimension)
        filtered_index.add(filtered_embeddings)

        distances, indices = filtered_index.search(np.array(user_embedding), top_k)
        recommendations = filtered_data.iloc[indices[0]].copy()

        # 추천 이유 생성
        reasons = []
        for _, row in recommendations.iterrows():
            prompt = f"색감과 분위기를 기준으로 '{row['색감_분위기_통합']}'과 유사한 데이터를 추천합니다."
            input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=256).input_ids
            output_ids = self.kogpt.generate(input_ids, max_length=100, num_beams=4, early_stopping=True)
            reason = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
            reasons.append(reason)

        recommendations['recommendation_reason'] = reasons

        # 필터된 이미지 파일명 생성 (기존 컬럼 존재 여부 확인 후 처리)
        if 'image_filename' in recommendations.columns:
            recommendations['filtered_image_filename'] = recommendations['image_filename'].str.replace(
                r'_\d{2}\.(jpg|png)', '', regex=True
            )
        else:
            recommendations['filtered_image_filename'] = None  # 기본값 설정

        required_columns = ['filtered_image_filename', 'image_filename', 'recommendation_reason', '게시물수', '팔로워수', '팔로잉수']
        missing_columns = [col for col in required_columns if col not in recommendations.columns]

        if missing_columns:
            raise KeyError(f"필요한 컬럼이 데이터에 없습니다: {missing_columns}")

        return recommendations[required_columns]

    def get_recommendations(self, text=None, options=None, top_k=3):
        """텍스트와 옵션을 기반으로 추천 수행"""
        mood_filter = options.get('색감_분위기_통합') if options else None
        text_embedding = None
        options_embedding = None

        # text 입력 처리
        if text:
            keywords = self.extract_keywords_from_text(text)
            text_embedding = self.sentence_model.encode([keywords])

        # 옵션 입력 처리
        if options:
            combined_options = ' '.join([f"{k}: {v}" for k, v in options.items() if v])
            options_embedding = self.sentence_model.encode([combined_options])

        # 입력값이 없을 경우 에러 처리
        if text_embedding is None and options_embedding is None:
            raise ValueError("텍스트 또는 분위기 옵션 중 하나는 필수입니다.")

        # 유사도 평균 계산
        if text_embedding is not None and options_embedding is not None:
            combined_embedding = (text_embedding + options_embedding) / 2
        else:
            combined_embedding = text_embedding if text_embedding is not None else options_embedding

        # 추천 실행
        return self.recommend_photographers(combined_embedding, top_k, mood_filter)


