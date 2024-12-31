class ChatBot {
  constructor() {
      this.sendButton = document.getElementById('sendBtn');
      this.textbox = document.getElementById('textbox');
      this.chatContainer = document.getElementById('chatContainer');
      this.typingIndicator = document.querySelector('.typing-indicator');
      this.sessionId = this.generateSessionId(); // 세션 ID 생성
      this.activeBookIds = [];
      
      this.initializeEventListeners();
      this.loadHistory(); // 이전 대화 기록 로드
      this.addRecomends(books);
  }

  generateSessionId() {
      return 'session_' + Math.random().toString(36).slice(2, 11);
  }

  initializeEventListeners() {
      this.sendButton.addEventListener('click', () => this.sendMessage());
      this.textbox.addEventListener('keypress', (e) => {
          if (e.key === 'Enter') {
              e.preventDefault();
              this.sendMessage();
          }
      });
      this.textbox.addEventListener('input', () => {
          this.sendButton.disabled = !this.textbox.value.trim();
      });

      // 새 대화 시작 버튼 이벤트 리스너
      const newChatBtn = document.getElementById('newChatBtn');
      if (newChatBtn) {
          newChatBtn.addEventListener('click', () => this.startNewChat());
      }
  }

  async loadHistory() {
      try {
          const response = await fetch(`http://3.24.242.112:81/history/${this.sessionId}`);
          const data = await response.json();
          
          // 이전 대화 기록 표시
          // this.chatContainer.innerHTML = ''; // 기존 내용 비우기
          data.history.forEach(message => {
              this.addMessage(message.content, message.role === 'human' ? 'user' : 'bot');
          });
      } catch (error) {
          console.error('Error loading history:', error);
      }
  }

  async startNewChat() {
      try {
          // 현재 세션의 대화 기록 삭제
          await fetch(`http://3.24.242.112:81/history/${this.sessionId}`, {
              method: 'DELETE'
          });

          // 새 세션 ID 생성
          this.sessionId = this.generateSessionId();
          
          // 채팅 컨테이너 비우기
          this.chatContainer.innerHTML = '';
          
          // 입력창 초기화
          this.textbox.value = '';
          this.sendButton.disabled = true;
      } catch (error) {
          console.error('Error starting new chat:', error);
      }
  }

  async sendMessage() {
      const message = this.textbox.value.trim();
      if (!message) return;

      // 사용자 메시지 표시
      this.addMessage(message, 'user');
      this.textbox.value = '';
      this.sendButton.disabled = true;

      // 타이핑 표시 보이기
      this.showTypingIndicator();

      try {
          // FastAPI 서버로 메시지 전송
          const response = await fetch('http://3.24.242.112:81/chat', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 
                  content: message,
                  session_id: this.sessionId
              })
          });

          if (!response.ok) {
              throw new Error('Network response was not ok');
          }

          const data = await response.json();
          this.addMessage(data.response, 'bot');

      } catch (error) {
          console.error('Error:', error);
          this.addMessage('죄송합니다. 오류가 발생했습니다.', 'bot');
      } finally {
          this.hideTypingIndicator();
      }
  }

  addMessage(text, sender) {
      const messageDiv = document.createElement('div');
      messageDiv.classList.add('message', sender);
      
      const timestamp = new Date().toLocaleTimeString('ko-KR', { 
          hour: '2-digit', 
          minute: '2-digit' 
      });
      
      messageDiv.innerHTML = `
          <div class="message-content">${text}</div>
          <div class="message-timestamp">${timestamp}</div>
      `;

      this.chatContainer.appendChild(messageDiv);
      this.scrollToBottom();
  }
    addRecomends(bookList, sender='bot') {
        // 활성화된 책들의 ID를 저장할 배열 형태의 local 변수

        bookList.forEach(book => {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', sender);
            
            const timestamp = new Date().toLocaleTimeString('ko-KR', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            messageDiv.innerHTML = `
                <div class="message-content book-recommendation" data-book-id="${book.id}">
                    <h3>${book.title}</h3>
                    <div class="book-info">
                        <img src="${book.cover}" alt="${book.title}" class="book-cover">
                        <p class="book-description">${book.desc}</p>
                    </div>
                </div>
                <div class="message-timestamp">${timestamp}</div>
            `;

            // 책 정보 Div 클릭 이벤트 추가
            const bookRecommendationDiv = messageDiv.querySelector('.book-recommendation');
            bookRecommendationDiv.addEventListener('click', () => {
                // 현재 클릭된 책의 ID
                const currentBookId = book.id;

                // 이미 활성화된 상태라면 비활성화, 그렇지 않으면 활성화
                if (bookRecommendationDiv.classList.contains('active')) {
                    bookRecommendationDiv.classList.remove('active');
                    // activeBookIds에서 현재 책 ID 제거
                    this.activeBookIds = this.activeBookIds.filter(id => id !== currentBookId);
                } else {
                    bookRecommendationDiv.classList.add('active');
                    // activeBookIds에 현재 책 ID 추가 (중복 방지)
                    if (!this.activeBookIds.includes(currentBookId)) {
                        this.activeBookIds.push(currentBookId);
                    }
                }

                console.log('Activated Book IDs:', activeBookIds);
            });

            this.chatContainer.appendChild(messageDiv);
        });

        // 스크롤을 아래로 이동
        this.scrollToBottom();

        // return activeBookIds;
    }


  scrollToBottom() {
      this.chatContainer.scrollTo({
          top: this.chatContainer.scrollHeight,
          behavior: 'smooth'
      });
  }

  showTypingIndicator() {
      this.typingIndicator.style.display = 'flex';
  }

  hideTypingIndicator() {
      this.typingIndicator.style.display = 'none';
  }
}

const books = [
    { id:0, title: "책1", cover: "https://shopping-phinf.pstatic.net/main_3249140/32491401626.20231004072435.jpg?type=w300", desc: "이 책은 ...에 관한 책입니다." },
    { id:1, title: "책2", cover: "https://shopping-phinf.pstatic.net/main_5153378/51533784655.20241122092412.jpg?type=w300", desc: "흥미로운 ...에 대한 설명입니다." },
    { id:2, title: "책3", cover: "https://shopping-phinf.pstatic.net/main_3248204/32482041666.20230725121007.jpg?type=w300", desc: "이 책은 ... 이야기입니다." },
    { id:3, title: "책4", cover: "https://shopping-phinf.pstatic.net/main_3243636/32436366634.20231124160335.jpg?type=w300", desc: "흥미진진한 ... 모험입니다." },
    { id:4, title: "책5", cover: "https://shopping-phinf.pstatic.net/main_5018758/50187581619.20240926090927.jpg?type=w300", desc: "이 책은 ...에 관한 책입니다." }
];


// 채팅봇 인스턴스 생성
document.addEventListener('DOMContentLoaded', () => {
  const chatbot = new ChatBot();
});

export default ChatBot;