    // APIRouter.js
    export class APIRouter {
        constructor() {
            this.apiMapping = {
                0: "chatbot_database_api",
                1: "user_database_api"
            };
        }
        
        async routeQuery(query) {
            try {
                const response = await fetch("http://3.24.242.112:81/router", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        messages: [
                            {
                                role: "system",
                                content: `
                                쿼리의 성격을 분석하여 다음과 같이 분류하세요:
                                0 - 책과 관련 없는 쿼리 또는 그 외의 일반적인 질문
                                1 - 책을 추천해주기를 원하는 쿼리 (예: 특정 장르나 주제에 맞는 책 추천 요청)
                                
                                답변은 반드시 0 또는 1로만 응답하세요.
                                `
                            },
                            {
                                role: "user",
                                content: query
                            }
                        ],
                        max_tokens: 1
                    })
                });

                const data = await response.json();
                const classification = parseInt(data.choices[0].message.content.trim(), 10);
                console.log(this.apiMapping[classification]);
                return this.apiMapping[classification];
            } catch (error) {
                console.error(`라우팅 중 오류 발생: ${error.message}`);
                return this.apiMapping[0];
            }
        }
    }
