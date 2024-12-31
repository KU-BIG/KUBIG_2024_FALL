import { APIRouter } from './APIRouter.js'

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
  }

  /* user DB에서 고유 ID 가져오는 코드로 변경 */
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
          this.chatContainer.innerHTML = ''; // 기존 내용 비우기
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
      await this.processQuery(message);
  }

  async processQuery(message) {
    const router = new APIRouter();
    const selectedApi = await router.routeQuery(message);

    if (selectedApi === 'chatbot_database_api') {
        await this.sendMessageToChat(message);  
    } else if (selectedApi === 'user_database_api') {
        await this.sendMessageToRecommend(message);  
    }
  }


  async sendMessageToChat(message) {
    try {
        // FastAPI 서버로 메시지 전송
        const response = await fetch('http://3.24.242.112:81/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                content: message,
                session_id: this.sessionId // 세션 아이디 포함
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

  async sendMessageToRecommend(message) {
    try { 
      // FastAPI 서버로 메시지 전송
      const response = await fetch('http://3.24.242.112:85/user', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
              indices: this.activeBookIds,
              query: message,
              user_id: this.sessionId // 세션 아이디 포함
          })
      }); 
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      console.log(data);      
      this.addRecomends(data);
      this.addMessage('요청사항에 맞는 책을 추천해드렸어요 :D <br>마음에 들거나 다음 질문에 반영하고 싶은 책들을 클릭해주세요!', 'bot');

    } catch (error) {
      console.error('Error:', error);
      this.addMessage('죄송합니다. 오류가 발생했습니다.', 'bot');
    } finally {
      this.hideTypingIndicator();
    }
  }

  addRecomends(bookList, sender='bot') {
    
    bookList.forEach(book => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender, 'book');
        
        const timestamp = new Date().toLocaleTimeString('ko-KR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
        <div class="message-content book-recommendation" data-book-id="${book.id}">
            <h3>${book.title}</h3>
            <div class="hashtags-container">
                ${book.hashtags.split(' ')
                    .slice(0, 5)
                    .map(tag => `<span class="hashtag-pill">#${tag.trim()}</span>`)
                    .join('')}
            </div>
            <div class="book-info">
                <img src="${book.cover ? book.cover : ""}" alt="${book.title}" class="book-cover">
                <p class="book-description">${book.description}</p>
            </div>
        </div>
        <div class="message-timestamp">${timestamp}</div>
     `;

        // 책 정보 Div 클릭 이벤트 추가
        const bookRecommendationDiv = messageDiv.querySelector('.book-recommendation');
        bookRecommendationDiv.addEventListener('click', (event) => {
            const parent = event.target.closest('.message.bot');
            parent.classList.toggle('active');
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

            console.log('Activated Book IDs:', this.activeBookIds);
        });

        this.chatContainer.appendChild(messageDiv);
    });

    this.scrollToBottom();
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


// 채팅봇 인스턴스 생성
document.addEventListener('DOMContentLoaded', () => {
  const chatbot = new ChatBot();
});

export default ChatBot;