from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Optional
from wedding_other_ver import WeddingRecommender
from wedding_sy_ver import WeddingRecommendationSystem
from daily_other_ver import DailyRecommender
from daily_sy_ver import DailyRecommendationSystem
from graduation_other_ver import GraduationRecommender
from graduation_sy_ver import GraduationRecommendationSystem

app = FastAPI()

# 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="main/dist"), name="static-main")
app.mount("/wedding/selection/static", StaticFiles(directory="wedding_selection/dist"), name="static-wedding_selection")
app.mount("/wedding/filter/static", StaticFiles(directory="wedding_filter/dist"), name="static-wedding_filter")
app.mount("/wedding/sihyeon/static", StaticFiles(directory="wedding_sihyeon/dist"), name="static-wedding_sihyeon")
app.mount("/wedding/filter/result/static", StaticFiles(directory="wedding_filter_result/dist"), name="static-wedding_filter_result")
app.mount("/wedding/sihyeon/result/static", StaticFiles(directory="wedding_sihyeon_result/dist"), name="static-wedding_sihyeon_result")
app.mount("/daily/selection/static", StaticFiles(directory="daily_selection/dist"), name="static-daily_selection")
app.mount("/daily/filter/static", StaticFiles(directory="daily_filter/dist"), name="static-daily_filter")
app.mount("/daily/sihyeon/static", StaticFiles(directory="daily_sihyeon/dist"), name="static-daily_sihyeon")
app.mount("/daily/filter/result/static", StaticFiles(directory="daily_filter_result/dist"), name="static-daily_filter_result")
app.mount("/daily/sihyeon/result/static", StaticFiles(directory="daily_sihyeon_result/dist"), name="static-daily_sihyeon_result")
app.mount("/graduation/selection/static", StaticFiles(directory="graduation_selection/dist"), name="static-graduation_selection")
app.mount("/graduation/filter/static", StaticFiles(directory="graduation_filter/dist"), name="static-graduation_filter")
app.mount("/graduation/sihyeon/static", StaticFiles(directory="graduation_sihyeon/dist"), name="static-graduation_sihyeon")
app.mount("/graduation/filter/result/static", StaticFiles(directory="graduation_filter_result/dist"), name="static-graduation_filter_result")
app.mount("/graduation/sihyeon/result/static", StaticFiles(directory="graduation_sihyeon_result/dist"), name="static-graduation_sihyeon_result")

# ----- 요청 데이터 모델 -----
class WeddingRequest(BaseModel):
    user_preferences: Dict[str, str]
    location: Optional[str] = None
    budget: Optional[int] = None

# 모델 초기화
filter_recommender = WeddingRecommender()
sihyeon_recommender = WeddingRecommendationSystem()
daily_filter_recommender = DailyRecommender()
daily_sihyeon_recommender = DailyRecommendationSystem()
graduation_filter_recommender = GraduationRecommender()
graduation_sihyeon_recommender = GraduationRecommendationSystem()

# ----- 정적 페이지 설정 -----
# ----- 웨딩 -----
@app.get("/", response_class=HTMLResponse)
async def read_main():
    with open("main/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/wedding/selection", response_class=HTMLResponse)
async def read_wedding_selection():
    with open("wedding_selection/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/wedding/filter", response_class=HTMLResponse)
async def read_wedding_filter():
    with open("wedding_filter/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/wedding/sihyeon", response_class=HTMLResponse)
async def read_wedding_sihyeon():
    with open("wedding_sihyeon/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/wedding/filter/result", response_class=HTMLResponse)
async def read_wedding_filter_result(request: Request):
    try:
        # 쿼리 파라미터를 디코딩
        query_params = request.query_params
        text = query_params.get("text")
        shooting_angle = query_params.get("shooting-angle")
        person_count = query_params.get("person-count")

        if not text or not shooting_angle or not person_count:
            raise HTTPException(status_code=400, detail="필수 입력값이 부족합니다.")

        # 추천 요청 데이터 생성
        options = {
            "촬영 구도": shooting_angle,
            "인물 수": person_count,
        }
        
        # 추천 실행
        recommendations = filter_recommender.recommend(
            text=text,
            options=options,
            top_k=3
        )
        
        # 추천 결과 HTML로 변환
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>MY SNAP</title>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <link rel="stylesheet" href="/wedding/filter/result/static/style.css">
        </head>
        <body>
        <div class="wrapper">
        <div class="slide__bg" style="--bg: url(https://raw.githubusercontent.com/yuujinnn/ai-service-snap/main/weddings.png); --dir: 0" data-current></div>
        """
        for idx, rec in recommendations.iterrows():
            html_content += f"""
            <div class="profile-card js-profile-card">
              <div class="profile-card__img">
                <img src="/wedding/filter/result/static/profile/{rec['filtered_image_filename']}.jpg" alt="{rec['filtered_image_filename']}'s profile photo" class="profile-photo">
              </div>
              <div class="profile-card__name">
                <span class="profile-name">{rec['filtered_image_filename']}</span>
                <a href="https://www.instagram.com/{rec['filtered_image_filename']}" class="profile-card-social__item instagram profile-card__social-icon" target="_blank">
                  <span class="icon-font">
                    <svg class="icon"><use xlink:href="#icon-instagram"></use></svg>
                  </span>
                </a>
              </div>
              <div class="profile-card-inf">
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로워수']}</div>
                  <div class="profile-card-inf__txt">Followers</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로잉수']}</div>
                  <div class="profile-card-inf__txt">Following</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['게시물수']}</div>
                  <div class="profile-card-inf__txt">Works</div>
                </div>
              </div>
              <div class="photo-gallery">
                <img src="/wedding/filter/result/static/wedding_image/{rec['image_filename']}" alt="Wedding photo" class="gallery-photo">
              </div>
            </div>
            """
        html_content += """
        </div>
          <svg hidden="hidden">
            <defs>
              <symbol id="icon-instagram" viewBox="0 0 32 32">
                <title>instagram</title>
                <path d="M16 2.881c4.275 0 4.781 0.019 6.462 0.094 1.563 0.069 2.406 0.331 2.969 0.55 0.744 0.288 1.281 0.638 1.837 1.194 0.563 0.563 0.906 1.094 1.2 1.838 0.219 0.563 0.481 1.412 0.55 2.969 0.075 1.688 0.094 2.194 0.094 6.463s-0.019 4.781-0.094 6.463c-0.069 1.563-0.331 2.406-0.55 2.969-0.288 0.744-0.637 1.281-1.194 1.837-0.563 0.563-1.094 0.906-1.837 1.2-0.563 0.219-1.413 0.481-2.969 0.55-1.688 0.075-2.194 0.094-6.463 0.094s-4.781-0.019-6.463-0.094c-1.563-0.069-2.406-0.331-2.969-0.55-0.744-0.288-1.281-0.637-1.838-1.194-0.563-0.563-0.906-1.094-1.2-1.837-0.219-0.563-0.481-1.413-0.55-2.969-0.075-1.688-0.094-2.194-0.094-6.463s0.019-4.781 0.094-6.463c0.069-1.563 0.331-2.406 0.55-2.969 0.288-0.744 0.638-1.281 1.194-1.838 0.563-0.563 1.094-0.906 1.838-1.2 0.563-0.219 1.412-0.481 2.969-0.55 1.681-0.075 2.188-0.094 6.463-0.094zM16 0c-4.344 0-4.887 0.019-6.594 0.094-1.7 0.075-2.869 0.35-3.881 0.744-1.056 0.412-1.95 0.956-2.837 1.85-0.894 0.888-1.438 1.781-1.85 2.831-0.394 1.019-0.669 2.181-0.744 3.881-0.075 1.713-0.094 2.256-0.094 6.6s0.019 4.887 0.094 6.594c0.075 1.7 0.35 2.869 0.744 3.881 0.413 1.056 0.956 1.95 1.85 2.837 0.887 0.887 1.781 1.438 2.831 1.844 1.019 0.394 2.181 0.669 3.881 0.744 1.706 0.075 2.25 0.094 6.594 0.094s4.888-0.019 6.594-0.094c1.7-0.075 2.869-0.35 3.881-0.744 1.050-0.406 1.944-0.956 2.831-1.844s1.438-1.781 1.844-2.831c0.394-1.019 0.669-2.181 0.744-3.881 0.075-1.706 0.094-2.25 0.094-6.594s-0.019-4.887-0.094-6.594c-0.075-1.7-0.35-2.869-0.744-3.881-0.394-1.063-0.938-1.956-1.831-2.844-0.887-0.887-1.781-1.438-2.831-1.844-1.019-0.394-2.181-0.669-3.881-0.744-1.712-0.081-2.256-0.1-6.6-0.1v0z"></path>
                <path d="M16 7.781c-4.537 0-8.219 3.681-8.219 8.219s3.681 8.219 8.219 8.219 8.219-3.681 8.219-8.219c0-4.537-3.681-8.219-8.219-8.219zM16 21.331c-2.944 0-5.331-2.387-5.331-5.331s2.387-5.331 5.331-5.331c2.944 0 5.331 2.387 5.331 5.331s-2.387 5.331-5.331 5.331z"></path>
                <path d="M26.462 7.456c0 1.060-0.859 1.919-1.919 1.919s-1.919-0.859-1.919-1.919c0-1.060 0.859-1.919 1.919-1.919s1.919 0.859 1.919 1.919z"></path>
              </symbol>
            </defs>
          </svg>
        <script src="/wedding/filter/result/static/script.js"></script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과를 처리하는 데 실패했습니다: {str(e)}")


@app.get("/wedding/sihyeon/result", response_class=HTMLResponse)
async def read_wedding_sihyeon_result(request: Request):
    try:
        # 쿼리 파라미터를 디코딩
        query_params = request.query_params
        text = query_params.get("text")
        mood = query_params.get("mood")

        if not mood:
            raise HTTPException(status_code=400, detail="필수 입력값이 부족합니다.")

        # 추천 요청 데이터 생성
        options = {
            "색감_분위기_통합": mood,
        }
        
        # 추천 실행
        recommendations = sihyeon_recommender.get_recommendations(
            text=text,
            options=options,
            top_k=3
        )
        
        # 추천 결과 HTML로 변환
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>MY SNAP</title>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <link rel="stylesheet" href="/wedding/sihyeon/result/static/style.css">
        </head>
        <body>
        <div class="wrapper">
        <div class="slide__bg" style="--bg: url(https://raw.githubusercontent.com/yuujinnn/ai-service-snap/main/weddings.png); --dir: 0" data-current></div>
        """
        for idx, rec in recommendations.iterrows():
            html_content += f"""
            <div class="profile-card js-profile-card">
              <div class="profile-card__img">
                <img src="/wedding/sihyeon/result/static/profile/{rec['filtered_image_filename']}.jpg" alt="{rec['filtered_image_filename']}'s profile photo" class="profile-photo">
              </div>
              <div class="profile-card__name">
                <span class="profile-name">{rec['filtered_image_filename']}</span>
                <a href="https://www.instagram.com/{rec['filtered_image_filename']}" class="profile-card-social__item instagram profile-card__social-icon" target="_blank">
                  <span class="icon-font">
                    <svg class="icon"><use xlink:href="#icon-instagram"></use></svg>
                  </span>
                </a>
              </div>
              <div class="profile-card-inf">
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로워수']}</div>
                  <div class="profile-card-inf__txt">Followers</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로잉수']}</div>
                  <div class="profile-card-inf__txt">Following</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['게시물수']}</div>
                  <div class="profile-card-inf__txt">Works</div>
                </div>
              </div>
              <div class="photo-gallery">
                <img src="/wedding/sihyeon/result/static/wedding_image/{rec['image_filename']}" alt="Wedding photo" class="gallery-photo">
              </div>
            </div>
            """
        html_content += """
        </div>
          <svg hidden="hidden">
            <defs>
              <symbol id="icon-instagram" viewBox="0 0 32 32">
                <title>instagram</title>
                <path d="M16 2.881c4.275 0 4.781 0.019 6.462 0.094 1.563 0.069 2.406 0.331 2.969 0.55 0.744 0.288 1.281 0.638 1.837 1.194 0.563 0.563 0.906 1.094 1.2 1.838 0.219 0.563 0.481 1.412 0.55 2.969 0.075 1.688 0.094 2.194 0.094 6.463s-0.019 4.781-0.094 6.463c-0.069 1.563-0.331 2.406-0.55 2.969-0.288 0.744-0.637 1.281-1.194 1.837-0.563 0.563-1.094 0.906-1.837 1.2-0.563 0.219-1.413 0.481-2.969 0.55-1.688 0.075-2.194 0.094-6.463 0.094s-4.781-0.019-6.463-0.094c-1.563-0.069-2.406-0.331-2.969-0.55-0.744-0.288-1.281-0.637-1.838-1.194-0.563-0.563-0.906-1.094-1.2-1.837-0.219-0.563-0.481-1.413-0.55-2.969-0.075-1.688-0.094-2.194-0.094-6.463s0.019-4.781 0.094-6.463c0.069-1.563 0.331-2.406 0.55-2.969 0.288-0.744 0.638-1.281 1.194-1.838 0.563-0.563 1.094-0.906 1.838-1.2 0.563-0.219 1.412-0.481 2.969-0.55 1.681-0.075 2.188-0.094 6.463-0.094zM16 0c-4.344 0-4.887 0.019-6.594 0.094-1.7 0.075-2.869 0.35-3.881 0.744-1.056 0.412-1.95 0.956-2.837 1.85-0.894 0.888-1.438 1.781-1.85 2.831-0.394 1.019-0.669 2.181-0.744 3.881-0.075 1.713-0.094 2.256-0.094 6.6s0.019 4.887 0.094 6.594c0.075 1.7 0.35 2.869 0.744 3.881 0.413 1.056 0.956 1.95 1.85 2.837 0.887 0.887 1.781 1.438 2.831 1.844 1.019 0.394 2.181 0.669 3.881 0.744 1.706 0.075 2.25 0.094 6.594 0.094s4.888-0.019 6.594-0.094c1.7-0.075 2.869-0.35 3.881-0.744 1.050-0.406 1.944-0.956 2.831-1.844s1.438-1.781 1.844-2.831c0.394-1.019 0.669-2.181 0.744-3.881 0.075-1.706 0.094-2.25 0.094-6.594s-0.019-4.887-0.094-6.594c-0.075-1.7-0.35-2.869-0.744-3.881-0.394-1.063-0.938-1.956-1.831-2.844-0.887-0.887-1.781-1.438-2.831-1.844-1.019-0.394-2.181-0.669-3.881-0.744-1.712-0.081-2.256-0.1-6.6-0.1v0z"></path>
                <path d="M16 7.781c-4.537 0-8.219 3.681-8.219 8.219s3.681 8.219 8.219 8.219 8.219-3.681 8.219-8.219c0-4.537-3.681-8.219-8.219-8.219zM16 21.331c-2.944 0-5.331-2.387-5.331-5.331s2.387-5.331 5.331-5.331c2.944 0 5.331 2.387 5.331 5.331s-2.387 5.331-5.331 5.331z"></path>
                <path d="M26.462 7.456c0 1.060-0.859 1.919-1.919 1.919s-1.919-0.859-1.919-1.919c0-1.060 0.859-1.919 1.919-1.919s1.919 0.859 1.919 1.919z"></path>
              </symbol>
            </defs>
          </svg>
        <script src="/wedding/sihyeon/result/static/script.js"></script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과를 처리하는 데 실패했습니다: {str(e)}")


# ----- 일상 -----
@app.get("/daily/selection", response_class=HTMLResponse)
async def read_daily_selection():
    with open("daily_selection/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/daily/filter", response_class=HTMLResponse)
async def read_daily_filter():
    with open("daily_filter/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/daily/sihyeon", response_class=HTMLResponse)
async def read_daily_sihyeon():
    with open("daily_sihyeon/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/daily/filter/result", response_class=HTMLResponse)
async def read_daily_filter_result(request: Request):
    try:
        # 쿼리 파라미터를 디코딩
        query_params = request.query_params
        text = query_params.get("text")
        shooting_angle = query_params.get("shooting-angle")
        person_count = query_params.get("person-count")

        if not text or not shooting_angle or not person_count:
            raise HTTPException(status_code=400, detail="필수 입력값이 부족합니다.")

        # 추천 요청 데이터 생성
        options = {
            "촬영 구도": shooting_angle,
            "사진 종류": person_count,
        }
        
        # 추천 실행
        recommendations = daily_filter_recommender.recommend(
            text=text,
            options=options,
            top_k=3
        )
        
        # 추천 결과 HTML로 변환
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>MY SNAP</title>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <link rel="stylesheet" href="/daily/filter/result/static/style.css">
        </head>
        <body>
        <div class="wrapper">
        <div class="slide__bg" style="--bg: url(https://raw.githubusercontent.com/yuujinnn/ai-service-snap/main/life.png); --dir: 0" data-current></div>
        """
        for idx, rec in recommendations.iterrows():
            html_content += f"""
            <div class="profile-card js-profile-card">
              <div class="profile-card__img">
                <img src="/daily/filter/result/static/profile/{rec['filtered_image_filename']}.jpg" alt="{rec['filtered_image_filename']}'s profile photo" class="profile-photo">
              </div>
              <div class="profile-card__name">
                <span class="profile-name">{rec['filtered_image_filename']}</span>
                <a href="https://www.instagram.com/{rec['filtered_image_filename']}" class="profile-card-social__item instagram profile-card__social-icon" target="_blank">
                  <span class="icon-font">
                    <svg class="icon"><use xlink:href="#icon-instagram"></use></svg>
                  </span>
                </a>
              </div>
              <div class="profile-card-inf">
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로워수']}</div>
                  <div class="profile-card-inf__txt">Followers</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로잉수']}</div>
                  <div class="profile-card-inf__txt">Following</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['게시물수']}</div>
                  <div class="profile-card-inf__txt">Works</div>
                </div>
              </div>
              <div class="photo-gallery">
                <img src="/daily/filter/result/static/daily_image/{rec['image_filename']}" alt="Daily photo" class="gallery-photo">
              </div>
            </div>
            """
        html_content += """
        </div>
          <svg hidden="hidden">
            <defs>
              <symbol id="icon-instagram" viewBox="0 0 32 32">
                <title>instagram</title>
                <path d="M16 2.881c4.275 0 4.781 0.019 6.462 0.094 1.563 0.069 2.406 0.331 2.969 0.55 0.744 0.288 1.281 0.638 1.837 1.194 0.563 0.563 0.906 1.094 1.2 1.838 0.219 0.563 0.481 1.412 0.55 2.969 0.075 1.688 0.094 2.194 0.094 6.463s-0.019 4.781-0.094 6.463c-0.069 1.563-0.331 2.406-0.55 2.969-0.288 0.744-0.637 1.281-1.194 1.837-0.563 0.563-1.094 0.906-1.837 1.2-0.563 0.219-1.413 0.481-2.969 0.55-1.688 0.075-2.194 0.094-6.463 0.094s-4.781-0.019-6.463-0.094c-1.563-0.069-2.406-0.331-2.969-0.55-0.744-0.288-1.281-0.637-1.838-1.194-0.563-0.563-0.906-1.094-1.2-1.837-0.219-0.563-0.481-1.413-0.55-2.969-0.075-1.688-0.094-2.194-0.094-6.463s0.019-4.781 0.094-6.463c0.069-1.563 0.331-2.406 0.55-2.969 0.288-0.744 0.638-1.281 1.194-1.838 0.563-0.563 1.094-0.906 1.838-1.2 0.563-0.219 1.412-0.481 2.969-0.55 1.681-0.075 2.188-0.094 6.463-0.094zM16 0c-4.344 0-4.887 0.019-6.594 0.094-1.7 0.075-2.869 0.35-3.881 0.744-1.056 0.412-1.95 0.956-2.837 1.85-0.894 0.888-1.438 1.781-1.85 2.831-0.394 1.019-0.669 2.181-0.744 3.881-0.075 1.713-0.094 2.256-0.094 6.6s0.019 4.887 0.094 6.594c0.075 1.7 0.35 2.869 0.744 3.881 0.413 1.056 0.956 1.95 1.85 2.837 0.887 0.887 1.781 1.438 2.831 1.844 1.019 0.394 2.181 0.669 3.881 0.744 1.706 0.075 2.25 0.094 6.594 0.094s4.888-0.019 6.594-0.094c1.7-0.075 2.869-0.35 3.881-0.744 1.050-0.406 1.944-0.956 2.831-1.844s1.438-1.781 1.844-2.831c0.394-1.019 0.669-2.181 0.744-3.881 0.075-1.706 0.094-2.25 0.094-6.594s-0.019-4.887-0.094-6.594c-0.075-1.7-0.35-2.869-0.744-3.881-0.394-1.063-0.938-1.956-1.831-2.844-0.887-0.887-1.781-1.438-2.831-1.844-1.019-0.394-2.181-0.669-3.881-0.744-1.712-0.081-2.256-0.1-6.6-0.1v0z"></path>
                <path d="M16 7.781c-4.537 0-8.219 3.681-8.219 8.219s3.681 8.219 8.219 8.219 8.219-3.681 8.219-8.219c0-4.537-3.681-8.219-8.219-8.219zM16 21.331c-2.944 0-5.331-2.387-5.331-5.331s2.387-5.331 5.331-5.331c2.944 0 5.331 2.387 5.331 5.331s-2.387 5.331-5.331 5.331z"></path>
                <path d="M26.462 7.456c0 1.060-0.859 1.919-1.919 1.919s-1.919-0.859-1.919-1.919c0-1.060 0.859-1.919 1.919-1.919s1.919 0.859 1.919 1.919z"></path>
              </symbol>
            </defs>
          </svg>
        <script src="/daily/filter/result/static/script.js"></script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과를 처리하는 데 실패했습니다: {str(e)}")


@app.get("/daily/sihyeon/result", response_class=HTMLResponse)
async def read_daily_sihyeon_result(request: Request):
    try:
        # 쿼리 파라미터를 디코딩
        query_params = request.query_params
        text = query_params.get("text")
        mood = query_params.get("mood")

        if not mood:
            raise HTTPException(status_code=400, detail="필수 입력값이 부족합니다.")

        # 추천 요청 데이터 생성
        options = {
            "색감_분위기_통합": mood,
        }
        
        # 추천 실행
        recommendations = daily_sihyeon_recommender.get_recommendations(
            text=text,
            options=options,
            top_k=3
        )
        
        # 추천 결과 HTML로 변환
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>MY SNAP</title>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <link rel="stylesheet" href="/daily/sihyeon/result/static/style.css">
        </head>
        <body>
        <div class="wrapper">
        <div class="slide__bg" style="--bg: url(https://raw.githubusercontent.com/yuujinnn/ai-service-snap/main/life.png); --dir: 0" data-current></div>
        """
        for idx, rec in recommendations.iterrows():
            html_content += f"""
            <div class="profile-card js-profile-card">
              <div class="profile-card__img">
                <img src="/daily/sihyeon/result/static/profile/{rec['filtered_image_filename']}.jpg" alt="{rec['filtered_image_filename']}'s profile photo" class="profile-photo">
              </div>
              <div class="profile-card__name">
                <span class="profile-name">{rec['filtered_image_filename']}</span>
                <a href="https://www.instagram.com/{rec['filtered_image_filename']}" class="profile-card-social__item instagram profile-card__social-icon" target="_blank">
                  <span class="icon-font">
                    <svg class="icon"><use xlink:href="#icon-instagram"></use></svg>
                  </span>
                </a>
              </div>
              <div class="profile-card-inf">
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로워수']}</div>
                  <div class="profile-card-inf__txt">Followers</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로잉수']}</div>
                  <div class="profile-card-inf__txt">Following</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['게시물수']}</div>
                  <div class="profile-card-inf__txt">Works</div>
                </div>
              </div>
              <div class="photo-gallery">
                <img src="/daily/sihyeon/result/static/daily_image/{rec['image_filename']}" alt="Daily photo" class="gallery-photo">
              </div>
            </div>
            """
        html_content += """
        </div>
          <svg hidden="hidden">
            <defs>
              <symbol id="icon-instagram" viewBox="0 0 32 32">
                <title>instagram</title>
                <path d="M16 2.881c4.275 0 4.781 0.019 6.462 0.094 1.563 0.069 2.406 0.331 2.969 0.55 0.744 0.288 1.281 0.638 1.837 1.194 0.563 0.563 0.906 1.094 1.2 1.838 0.219 0.563 0.481 1.412 0.55 2.969 0.075 1.688 0.094 2.194 0.094 6.463s-0.019 4.781-0.094 6.463c-0.069 1.563-0.331 2.406-0.55 2.969-0.288 0.744-0.637 1.281-1.194 1.837-0.563 0.563-1.094 0.906-1.837 1.2-0.563 0.219-1.413 0.481-2.969 0.55-1.688 0.075-2.194 0.094-6.463 0.094s-4.781-0.019-6.463-0.094c-1.563-0.069-2.406-0.331-2.969-0.55-0.744-0.288-1.281-0.637-1.838-1.194-0.563-0.563-0.906-1.094-1.2-1.837-0.219-0.563-0.481-1.413-0.55-2.969-0.075-1.688-0.094-2.194-0.094-6.463s0.019-4.781 0.094-6.463c0.069-1.563 0.331-2.406 0.55-2.969 0.288-0.744 0.638-1.281 1.194-1.838 0.563-0.563 1.094-0.906 1.838-1.2 0.563-0.219 1.412-0.481 2.969-0.55 1.681-0.075 2.188-0.094 6.463-0.094zM16 0c-4.344 0-4.887 0.019-6.594 0.094-1.7 0.075-2.869 0.35-3.881 0.744-1.056 0.412-1.95 0.956-2.837 1.85-0.894 0.888-1.438 1.781-1.85 2.831-0.394 1.019-0.669 2.181-0.744 3.881-0.075 1.713-0.094 2.256-0.094 6.6s0.019 4.887 0.094 6.594c0.075 1.7 0.35 2.869 0.744 3.881 0.413 1.056 0.956 1.95 1.85 2.837 0.887 0.887 1.781 1.438 2.831 1.844 1.019 0.394 2.181 0.669 3.881 0.744 1.706 0.075 2.25 0.094 6.594 0.094s4.888-0.019 6.594-0.094c1.7-0.075 2.869-0.35 3.881-0.744 1.050-0.406 1.944-0.956 2.831-1.844s1.438-1.781 1.844-2.831c0.394-1.019 0.669-2.181 0.744-3.881 0.075-1.706 0.094-2.25 0.094-6.594s-0.019-4.887-0.094-6.594c-0.075-1.7-0.35-2.869-0.744-3.881-0.394-1.063-0.938-1.956-1.831-2.844-0.887-0.887-1.781-1.438-2.831-1.844-1.019-0.394-2.181-0.669-3.881-0.744-1.712-0.081-2.256-0.1-6.6-0.1v0z"></path>
                <path d="M16 7.781c-4.537 0-8.219 3.681-8.219 8.219s3.681 8.219 8.219 8.219 8.219-3.681 8.219-8.219c0-4.537-3.681-8.219-8.219-8.219zM16 21.331c-2.944 0-5.331-2.387-5.331-5.331s2.387-5.331 5.331-5.331c2.944 0 5.331 2.387 5.331 5.331s-2.387 5.331-5.331 5.331z"></path>
                <path d="M26.462 7.456c0 1.060-0.859 1.919-1.919 1.919s-1.919-0.859-1.919-1.919c0-1.060 0.859-1.919 1.919-1.919s1.919 0.859 1.919 1.919z"></path>
              </symbol>
            </defs>
          </svg>
        <script src="/daily/sihyeon/result/static/script.js"></script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과를 처리하는 데 실패했습니다: {str(e)}")


# ----- 졸업 -----
@app.get("/graduation/selection", response_class=HTMLResponse)
async def read_graduation_selection():
    with open("graduation_selection/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/graduation/filter", response_class=HTMLResponse)
async def read_graduation_filter():
    with open("graduation_filter/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/graduation/sihyeon", response_class=HTMLResponse)
async def read_graduation_sihyeon():
    with open("graduation_sihyeon/dist/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/graduation/filter/result", response_class=HTMLResponse)
async def read_graduation_filter_result(request: Request):
    try:
        # 쿼리 파라미터를 디코딩
        query_params = request.query_params
        text = query_params.get("text")
        shooting_angle = query_params.get("shooting-angle")
        person_count = query_params.get("person-count")

        if not text or not shooting_angle or not person_count:
            raise HTTPException(status_code=400, detail="필수 입력값이 부족합니다.")

        # 추천 요청 데이터 생성
        options = {
            "촬영 구도": shooting_angle,
            "사진 종류": person_count,
        }
        
        # 추천 실행
        recommendations = graduation_filter_recommender.recommend(
            text=text,
            options=options,
            top_k=3
        )
        
        # 추천 결과 HTML로 변환
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>MY SNAP</title>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <link rel="stylesheet" href="/graduation/filter/result/static/style.css">
        </head>
        <body>
        <div class="wrapper">
        <div class="slide__bg" style="--bg: url(https://raw.githubusercontent.com/yuujinnn/ai-service-snap/main/graduate.png); --dir: 0" data-current></div>
        """
        for idx, rec in recommendations.iterrows():
            html_content += f"""
            <div class="profile-card js-profile-card">
              <div class="profile-card__img">
                <img src="/graduation/filter/result/static/profile/{rec['filtered_image_filename']}.jpg" alt="{rec['filtered_image_filename']}'s profile photo" class="profile-photo">
              </div>
              <div class="profile-card__name">
                <span class="profile-name">{rec['filtered_image_filename']}</span>
                <a href="https://www.instagram.com/{rec['filtered_image_filename']}" class="profile-card-social__item instagram profile-card__social-icon" target="_blank">
                  <span class="icon-font">
                    <svg class="icon"><use xlink:href="#icon-instagram"></use></svg>
                  </span>
                </a>
              </div>
              <div class="profile-card-inf">
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로워수']}</div>
                  <div class="profile-card-inf__txt">Followers</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로잉수']}</div>
                  <div class="profile-card-inf__txt">Following</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['게시물수']}</div>
                  <div class="profile-card-inf__txt">Works</div>
                </div>
              </div>
              <div class="photo-gallery">
                <img src="/graduation/filter/result/static/graduation_image/{rec['image_filename']}" alt="Graduation photo" class="gallery-photo">
              </div>
            </div>
            """
        html_content += """
        </div>
          <svg hidden="hidden">
            <defs>
              <symbol id="icon-instagram" viewBox="0 0 32 32">
                <title>instagram</title>
                <path d="M16 2.881c4.275 0 4.781 0.019 6.462 0.094 1.563 0.069 2.406 0.331 2.969 0.55 0.744 0.288 1.281 0.638 1.837 1.194 0.563 0.563 0.906 1.094 1.2 1.838 0.219 0.563 0.481 1.412 0.55 2.969 0.075 1.688 0.094 2.194 0.094 6.463s-0.019 4.781-0.094 6.463c-0.069 1.563-0.331 2.406-0.55 2.969-0.288 0.744-0.637 1.281-1.194 1.837-0.563 0.563-1.094 0.906-1.837 1.2-0.563 0.219-1.413 0.481-2.969 0.55-1.688 0.075-2.194 0.094-6.463 0.094s-4.781-0.019-6.463-0.094c-1.563-0.069-2.406-0.331-2.969-0.55-0.744-0.288-1.281-0.637-1.838-1.194-0.563-0.563-0.906-1.094-1.2-1.837-0.219-0.563-0.481-1.413-0.55-2.969-0.075-1.688-0.094-2.194-0.094-6.463s0.019-4.781 0.094-6.463c0.069-1.563 0.331-2.406 0.55-2.969 0.288-0.744 0.638-1.281 1.194-1.838 0.563-0.563 1.094-0.906 1.838-1.2 0.563-0.219 1.412-0.481 2.969-0.55 1.681-0.075 2.188-0.094 6.463-0.094zM16 0c-4.344 0-4.887 0.019-6.594 0.094-1.7 0.075-2.869 0.35-3.881 0.744-1.056 0.412-1.95 0.956-2.837 1.85-0.894 0.888-1.438 1.781-1.85 2.831-0.394 1.019-0.669 2.181-0.744 3.881-0.075 1.713-0.094 2.256-0.094 6.6s0.019 4.887 0.094 6.594c0.075 1.7 0.35 2.869 0.744 3.881 0.413 1.056 0.956 1.95 1.85 2.837 0.887 0.887 1.781 1.438 2.831 1.844 1.019 0.394 2.181 0.669 3.881 0.744 1.706 0.075 2.25 0.094 6.594 0.094s4.888-0.019 6.594-0.094c1.7-0.075 2.869-0.35 3.881-0.744 1.050-0.406 1.944-0.956 2.831-1.844s1.438-1.781 1.844-2.831c0.394-1.019 0.669-2.181 0.744-3.881 0.075-1.706 0.094-2.25 0.094-6.594s-0.019-4.887-0.094-6.594c-0.075-1.7-0.35-2.869-0.744-3.881-0.394-1.063-0.938-1.956-1.831-2.844-0.887-0.887-1.781-1.438-2.831-1.844-1.019-0.394-2.181-0.669-3.881-0.744-1.712-0.081-2.256-0.1-6.6-0.1v0z"></path>
                <path d="M16 7.781c-4.537 0-8.219 3.681-8.219 8.219s3.681 8.219 8.219 8.219 8.219-3.681 8.219-8.219c0-4.537-3.681-8.219-8.219-8.219zM16 21.331c-2.944 0-5.331-2.387-5.331-5.331s2.387-5.331 5.331-5.331c2.944 0 5.331 2.387 5.331 5.331s-2.387 5.331-5.331 5.331z"></path>
                <path d="M26.462 7.456c0 1.060-0.859 1.919-1.919 1.919s-1.919-0.859-1.919-1.919c0-1.060 0.859-1.919 1.919-1.919s1.919 0.859 1.919 1.919z"></path>
              </symbol>
            </defs>
          </svg>
        <script src="/graduation/filter/result/static/script.js"></script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과를 처리하는 데 실패했습니다: {str(e)}")


@app.get("/graduation/sihyeon/result", response_class=HTMLResponse)
async def read_graduation_sihyeon_result(request: Request):
    try:
        # 쿼리 파라미터를 디코딩
        query_params = request.query_params
        text = query_params.get("text")
        mood = query_params.get("mood")

        if not mood:
            raise HTTPException(status_code=400, detail="필수 입력값이 부족합니다.")

        # 추천 요청 데이터 생성
        options = {
            "색감_분위기_통합": mood,
        }
        
        # 추천 실행
        recommendations = graduation_sihyeon_recommender.get_recommendations(
            text=text,
            options=options,
            top_k=3
        )
        
        # 추천 결과 HTML로 변환
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>MY SNAP</title>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <link rel="stylesheet" href="/graduation/sihyeon/result/static/style.css">
        </head>
        <body>
        <div class="wrapper">
        <div class="slide__bg" style="--bg: url(https://raw.githubusercontent.com/yuujinnn/ai-service-snap/main/graduate.png); --dir: 0" data-current></div>
        """
        for idx, rec in recommendations.iterrows():
            html_content += f"""
            <div class="profile-card js-profile-card">
              <div class="profile-card__img">
                <img src="/graduation/sihyeon/result/static/profile/{rec['filtered_image_filename']}.jpg" alt="{rec['filtered_image_filename']}'s profile photo" class="profile-photo">
              </div>
              <div class="profile-card__name">
                <span class="profile-name">{rec['filtered_image_filename']}</span>
                <a href="https://www.instagram.com/{rec['filtered_image_filename']}" class="profile-card-social__item instagram profile-card__social-icon" target="_blank">
                  <span class="icon-font">
                    <svg class="icon"><use xlink:href="#icon-instagram"></use></svg>
                  </span>
                </a>
              </div>
              <div class="profile-card-inf">
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로워수']}</div>
                  <div class="profile-card-inf__txt">Followers</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['팔로잉수']}</div>
                  <div class="profile-card-inf__txt">Following</div>
                </div>
                <div class="profile-card-inf__item">
                  <div class="profile-card-inf__title">{rec['게시물수']}</div>
                  <div class="profile-card-inf__txt">Works</div>
                </div>
              </div>
              <div class="photo-gallery">
                <img src="/graduation/sihyeon/result/static/graduation_image/{rec['image_filename']}" alt="Graduation photo" class="gallery-photo">
              </div>
            </div>
            """
        html_content += """
        </div>
          <svg hidden="hidden">
            <defs>
              <symbol id="icon-instagram" viewBox="0 0 32 32">
                <title>instagram</title>
                <path d="M16 2.881c4.275 0 4.781 0.019 6.462 0.094 1.563 0.069 2.406 0.331 2.969 0.55 0.744 0.288 1.281 0.638 1.837 1.194 0.563 0.563 0.906 1.094 1.2 1.838 0.219 0.563 0.481 1.412 0.55 2.969 0.075 1.688 0.094 2.194 0.094 6.463s-0.019 4.781-0.094 6.463c-0.069 1.563-0.331 2.406-0.55 2.969-0.288 0.744-0.637 1.281-1.194 1.837-0.563 0.563-1.094 0.906-1.837 1.2-0.563 0.219-1.413 0.481-2.969 0.55-1.688 0.075-2.194 0.094-6.463 0.094s-4.781-0.019-6.463-0.094c-1.563-0.069-2.406-0.331-2.969-0.55-0.744-0.288-1.281-0.637-1.838-1.194-0.563-0.563-0.906-1.094-1.2-1.837-0.219-0.563-0.481-1.413-0.55-2.969-0.075-1.688-0.094-2.194-0.094-6.463s0.019-4.781 0.094-6.463c0.069-1.563 0.331-2.406 0.55-2.969 0.288-0.744 0.638-1.281 1.194-1.838 0.563-0.563 1.094-0.906 1.838-1.2 0.563-0.219 1.412-0.481 2.969-0.55 1.681-0.075 2.188-0.094 6.463-0.094zM16 0c-4.344 0-4.887 0.019-6.594 0.094-1.7 0.075-2.869 0.35-3.881 0.744-1.056 0.412-1.95 0.956-2.837 1.85-0.894 0.888-1.438 1.781-1.85 2.831-0.394 1.019-0.669 2.181-0.744 3.881-0.075 1.713-0.094 2.256-0.094 6.6s0.019 4.887 0.094 6.594c0.075 1.7 0.35 2.869 0.744 3.881 0.413 1.056 0.956 1.95 1.85 2.837 0.887 0.887 1.781 1.438 2.831 1.844 1.019 0.394 2.181 0.669 3.881 0.744 1.706 0.075 2.25 0.094 6.594 0.094s4.888-0.019 6.594-0.094c1.7-0.075 2.869-0.35 3.881-0.744 1.050-0.406 1.944-0.956 2.831-1.844s1.438-1.781 1.844-2.831c0.394-1.019 0.669-2.181 0.744-3.881 0.075-1.706 0.094-2.25 0.094-6.594s-0.019-4.887-0.094-6.594c-0.075-1.7-0.35-2.869-0.744-3.881-0.394-1.063-0.938-1.956-1.831-2.844-0.887-0.887-1.781-1.438-2.831-1.844-1.019-0.394-2.181-0.669-3.881-0.744-1.712-0.081-2.256-0.1-6.6-0.1v0z"></path>
                <path d="M16 7.781c-4.537 0-8.219 3.681-8.219 8.219s3.681 8.219 8.219 8.219 8.219-3.681 8.219-8.219c0-4.537-3.681-8.219-8.219-8.219zM16 21.331c-2.944 0-5.331-2.387-5.331-5.331s2.387-5.331 5.331-5.331c2.944 0 5.331 2.387 5.331 5.331s-2.387 5.331-5.331 5.331z"></path>
                <path d="M26.462 7.456c0 1.060-0.859 1.919-1.919 1.919s-1.919-0.859-1.919-1.919c0-1.060 0.859-1.919 1.919-1.919s1.919 0.859 1.919 1.919z"></path>
              </symbol>
            </defs>
          </svg>
        <script src="/graduation/sihyeon/result/static/script.js"></script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"결과를 처리하는 데 실패했습니다: {str(e)}")
