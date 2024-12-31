class ChatBot {
  constructor() {
      this.sendButton = document.getElementById('sendBtn');
      this.textbox = document.getElementById('textbox');
      this.chatContainer = document.getElementById('chatContainer');
      this.typingIndicator = document.querySelector('.typing-indicator');
      this.sessionId = this.generateSessionId(); // 세션 ID 생성
      
      this.initializeEventListeners();
      this.loadHistory(); // 이전 대화 기록 로드
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