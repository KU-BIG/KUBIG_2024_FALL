class PopupGuide {
  constructor() {
    this.currentStep = 0;
    this.totalSteps = 3;
    this.images = [
      '/api/placeholder/600/400',
      '/api/placeholder/600/400',
      '/api/placeholder/600/400'
    ];
    // './info_img/1'

    // DOM 요소들
    this.container = document.getElementById('popupContainer');
    this.closeButton = document.getElementById('closeButton');
    this.prevButton = document.getElementById('prevButton');
    this.nextButton = document.getElementById('nextButton');
    this.stepImage = document.getElementById('stepImage');
    this.pagination = document.getElementById('pagination');

    // 이벤트 리스너 추가
    this.initializeEventListeners();
    
    // 초기 상태 설정
    this.updateDisplay();
  }

  initializeEventListeners() {
    this.closeButton.addEventListener('click', () => this.close());
    this.prevButton.addEventListener('click', () => this.navigate(-1));
    this.nextButton.addEventListener('click', () => this.navigate(1));
  }

  navigate(direction) {
    const newStep = this.currentStep + direction;
    if (newStep >= 0 && newStep < this.totalSteps) {
      this.currentStep = newStep;
      this.updateDisplay();
    }
  }

  updateDisplay() {
    // 이미지 업데이트
    this.stepImage.src = this.images[this.currentStep];
    
    // 페이지네이션 업데이트
    const dots = this.pagination.getElementsByClassName('dot');
    Array.from(dots).forEach((dot, index) => {
      dot.classList.toggle('active', index === this.currentStep);
    });

    // 네비게이션 버튼 상태 업데이트
    this.prevButton.style.visibility = this.currentStep === 0 ? 'hidden' : 'visible';
    this.nextButton.style.visibility = this.currentStep === this.totalSteps - 1 ? 'hidden' : 'visible';
  }

  close() {
    this.container.style.display = 'none';
  }
}

// 팝업 가이드 초기화
let popupGuideInstance = null;

function getPopupGuide() {
  if (!popupGuideInstance) {
    popupGuideInstance = new PopupGuide();
  }
  return popupGuideInstance;
}

// 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', () => {
  // 초기 인스턴스 생성
  getPopupGuide();
  document.querySelector('info-icon').addEventListener(
    'click', () => {
      getPopupGuide().open();
    });
});