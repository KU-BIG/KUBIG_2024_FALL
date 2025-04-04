from typing import Dict, Optional
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import faiss

class WeddingRecommender:
    def __init__(self):
        self.wedding_data = pd.read_csv('wedding_final.csv')

        # 결합된 텍스트 컬럼 생성
        self.wedding_data['combined_text'] = self.wedding_data[
            ['색감_분위기_통합', '고유한 특징', '촬영 구도', '동작', '의상', '인물 수']
        ].apply(lambda x: ' '.join(x.dropna()), axis=1)

        # 모델 로드
        self.sentence_model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-base-v2')
        self.kobart = BartForConditionalGeneration.from_pretrained('gogamza/kobart-base-v2')

        # 임베딩 생성
        self.wedding_data['embeddings'] = list(
            self.sentence_model.encode(self.wedding_data['combined_text'].tolist())
        )
        embeddings = np.array(self.wedding_data['embeddings'].tolist())

        # FAISS 인덱스 초기화
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        self.dimension = dimension

    def extract_keywords_from_text(self, user_input: str) -> str:
        prompt = f"""
        아래 문장에서 주요 키워드(색감, 분위기, 동작, 배경)를 추출하세요:
        입력: {user_input}
        출력: 분위기: <분위기>, 동작: <동작>, 배경: <배경>.
        """
        input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).input_ids
        summary_ids = self.kobart.generate(input_ids, max_length=50, num_beams=4, early_stopping=True)
        output = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return output

    def recommend_photographers(self, user_embedding: np.ndarray, filters: Dict[str, str], top_k: int = 3) -> pd.DataFrame:
        filtered_data = self.wedding_data.copy()

        for key, value in filters.items():
            if key in filtered_data.columns:
                filtered_data = filtered_data[filtered_data[key] == value]

        if filtered_data.empty:
            raise ValueError("해당 조건에 맞는 데이터가 없습니다.")

        # 필터링된 데이터에 대해 FAISS 인덱스를 생성
        filtered_embeddings = np.array(filtered_data['embeddings'].tolist())
        filtered_index = faiss.IndexFlatL2(self.dimension)
        filtered_index.add(filtered_embeddings)

        distances, indices = filtered_index.search(np.array(user_embedding), top_k)
        recommendations = filtered_data.iloc[indices[0]].copy()

        # 필터된 이미지 파일명 생성 (기존 컬럼 존재 여부 확인 후 처리)
        if 'image_filename' in recommendations.columns:
            recommendations['filtered_image_filename'] = recommendations['image_filename'].str.replace(
                r'_\d{2}\.(jpg|png)', '', regex=True
            )
        else:
            recommendations['filtered_image_filename'] = None

        # 추천 이유 생성
        reasons = []
        for _, row in recommendations.iterrows():
            prompt = f"색감과 분위기를 기준으로 '{row['색감_분위기_통합']}'과 유사한 데이터를 추천합니다."
            input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).input_ids
            summary_ids = self.kobart.generate(input_ids, max_length=50, num_beams=4, early_stopping=True)
            reason = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            reasons.append(reason)

        recommendations['recommendation_reason'] = reasons

        # 필요한 컬럼 확인
        required_columns = ['filtered_image_filename', 'image_filename', 'recommendation_reason', '게시물수', '팔로워수', '팔로잉수']
        missing_columns = [col for col in required_columns if col not in recommendations.columns]

        if missing_columns:
            raise KeyError(f"필요한 컬럼이 데이터에 없습니다: {missing_columns}")

        return recommendations[required_columns]


    def recommend(self, text: Optional[str] = None, options: Optional[Dict[str, str]] = None, top_k: int = 3) -> pd.DataFrame:
        if not text and not options:
            raise ValueError("촬영 인원, 구도와 텍스트 입력은 필수입니다.")

        # text 입력 처리
        if text:
            keywords = self.extract_keywords_from_text(text)
            text_embedding = self.sentence_model.encode([keywords])

        # 입력값이 없을 경우 에러 처리
        if text_embedding is None:
            raise ValueError("입력값(text 또는 options)이 필요합니다.")

        return self.recommend_photographers(text_embedding, options or {}, top_k)

# 사용 예제
# recommender = WeddingRecommender("wedding_final.csv")
# recommendations = recommender.recommend(
#     text="따뜻한 분위기와 자연스러운 동작으로 촬영된 사진을 원합니다.",
#     options={"촬영 구도": "클로즈업", "인물수": "2명"},
#     top_k=3
# )
# print(recommendations)
