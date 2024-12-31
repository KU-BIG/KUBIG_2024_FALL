function getSessionId() {
    let sessionId = localStorage.getItem('readme_generator_session');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
        localStorage.setItem('readme_generator_session', sessionId);
    }
    return sessionId;
}

function trackButtonClick(buttonName, documentId = null) {
    const formData = new FormData();
    formData.append('button_name', buttonName);
    formData.append('session_id', getSessionId());
    
    if (documentId) {
        formData.append('document_id', documentId);
    }

    fetch('/track-click/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    }).catch(console.error);
}


// myapp/tracking.js
function trackAIGeneratorAction(action, documentId = null) {
    gtag('event', 'ai_generator_interaction', {
        'event_category': 'user_action',
        'event_label': action,
        'document_id': documentId,
        'timestamp': new Date().toISOString()
    });
}