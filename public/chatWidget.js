// Floating Chat Widget for UniGuide
(function() {
  // Don't show on the dedicated chat page
  if (window.location.pathname.includes('chat.html')) {
    return;
  }

  // Create chat widget HTML
  const widgetHTML = `
    <div id="uniguide-chat-widget" style="
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      z-index: 9999;
      font-family: 'Inter', sans-serif;
    ">
      <!-- Chat Button -->
      <button id="chat-toggle-btn" style="
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border: none;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
      ">
        <span id="chat-icon" style="position: relative; z-index: 2;">💬</span>
        <div style="
          position: absolute;
          inset: 0;
          background: linear-gradient(135deg, #2563eb, #7c3aed);
          opacity: 0;
          transition: opacity 0.3s;
        " id="chat-btn-hover"></div>
      </button>

      <!-- Chat Popup -->
      <div id="chat-popup" style="
        position: absolute;
        bottom: 80px;
        right: 0;
        width: 400px;
        max-width: calc(100vw - 4rem);
        height: 600px;
        max-height: calc(100vh - 12rem);
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        display: none;
        flex-direction: column;
        overflow: hidden;
        transform: scale(0.9);
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      ">
        <!-- Chat Header -->
        <div style="
          background: linear-gradient(135deg, #3b82f6, #8b5cf6);
          padding: 1.2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          color: white;
        ">
          <div>
            <div style="font-weight: 700; font-size: 1.1rem;">🤖 UniGuide AI</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">Ask me anything!</div>
          </div>
          <button id="chat-close-btn" style="
            background: rgba(255, 255, 255, 0.2);
            border: none;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
          ">✕</button>
        </div>

        <!-- Chat iFrame -->
        <iframe 
          src="https://app.rubikchat.com/chat/ZEWmLt8NsJw5kUIvD58ArwLH"
          style="
            flex: 1;
            border: none;
            width: 100%;
            background: #f8fafc;
          "
          allow="microphone; clipboard-write"
          title="UniGuide Chat Assistant"
        ></iframe>

        <!-- View Full Chat Link -->
        <div style="
          padding: 0.8rem;
          background: #f8fafc;
          border-top: 1px solid #e2e8f0;
          text-align: center;
        ">
          <a href="chat.html" style="
            color: #3b82f6;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            transition: color 0.2s;
          " onmouseover="this.style.color='#2563eb'" onmouseout="this.style.color='#3b82f6'">
            Open Full Chat →
          </a>
        </div>
      </div>

      <!-- Notification Badge (optional) -->
      <div id="chat-badge" style="
        position: absolute;
        top: -5px;
        right: -5px;
        width: 24px;
        height: 24px;
        background: #ef4444;
        border-radius: 50%;
        display: none;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        border: 3px solid white;
        animation: pulse 2s infinite;
      ">!</div>
    </div>

    <style>
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }

      #chat-toggle-btn:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 12px 32px rgba(59, 130, 246, 0.5);
      }

      #chat-toggle-btn:hover #chat-btn-hover {
        opacity: 1;
      }

      #chat-close-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: rotate(90deg);
      }

      @media (max-width: 768px) {
        #uniguide-chat-widget {
          bottom: 1rem;
          right: 1rem;
        }

        #chat-toggle-btn {
          width: 56px;
          height: 56px;
          font-size: 1.6rem;
        }

        #chat-popup {
          width: calc(100vw - 2rem);
          height: calc(100vh - 10rem);
          bottom: 70px;
          right: -1rem;
        }
      }
    </style>
  `;

  // Insert widget into page
  document.body.insertAdjacentHTML('beforeend', widgetHTML);

  // Get elements
  const toggleBtn = document.getElementById('chat-toggle-btn');
  const closeBtn = document.getElementById('chat-close-btn');
  const popup = document.getElementById('chat-popup');
  const icon = document.getElementById('chat-icon');
  const badge = document.getElementById('chat-badge');

  let isOpen = false;

  // Toggle chat popup
  function toggleChat() {
    isOpen = !isOpen;
    
    if (isOpen) {
      popup.style.display = 'flex';
      setTimeout(() => {
        popup.style.transform = 'scale(1)';
        popup.style.opacity = '1';
      }, 10);
      icon.textContent = '✕';
      badge.style.display = 'none';
    } else {
      popup.style.transform = 'scale(0.9)';
      popup.style.opacity = '0';
      setTimeout(() => {
        popup.style.display = 'none';
      }, 300);
      icon.textContent = '💬';
    }
  }

  // Event listeners
  toggleBtn.addEventListener('click', toggleChat);
  closeBtn.addEventListener('click', toggleChat);

  // Close on escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
      toggleChat();
    }
  });

  // Optional: Show badge after 5 seconds to encourage interaction
  setTimeout(() => {
    if (!isOpen) {
      badge.style.display = 'flex';
    }
  }, 5000);

  // Hide badge when chat is opened
  toggleBtn.addEventListener('click', () => {
    badge.style.display = 'none';
  });
})();