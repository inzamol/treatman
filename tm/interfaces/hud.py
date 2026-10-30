"""
TM Futuristic Floating HUD Desktop Widget
"""

import sys
import threading
import json
from typing import Optional
from tm.config import get_config
from tm.core.agent import TMAgent
from tm.voice.ear import Ear
from tm.voice.speaker import Speaker

try:
    import webview
except ImportError:
    webview = None


HUD_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TM HUD</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
    body {
      background: rgba(10, 15, 25, 0.88);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(0, 220, 255, 0.4);
      border-radius: 16px;
      color: #e0f7fa;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 0 30px rgba(0, 220, 255, 0.25);
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      background: rgba(0, 220, 255, 0.08);
      border-bottom: 1px solid rgba(0, 220, 255, 0.2);
      -webkit-app-region: drag;
    }
    .title {
      font-weight: 700;
      letter-spacing: 2px;
      font-size: 14px;
      color: #00e5ff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .arc {
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: #00e5ff;
      box-shadow: 0 0 10px #00e5ff, 0 0 20px #00e5ff;
      animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
      0%, 100% { opacity: 0.6; transform: scale(0.9); }
      50% { opacity: 1; transform: scale(1.1); }
    }
    .close-btn {
      cursor: pointer;
      font-size: 16px;
      color: rgba(255,255,255,0.6);
      -webkit-app-region: no-drag;
      transition: color 0.2s;
    }
    .close-btn:hover { color: #ff5252; }
    .chat-area {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .msg {
      padding: 10px 14px;
      border-radius: 10px;
      font-size: 13px;
      line-height: 1.5;
      max-width: 90%;
      word-wrap: break-word;
    }
    .msg.user {
      align-self: flex-end;
      background: rgba(0, 220, 255, 0.2);
      border: 1px solid rgba(0, 220, 255, 0.4);
      color: #ffffff;
    }
    .msg.agent {
      align-self: flex-start;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #b2ebf2;
    }
    .status-bar {
      padding: 6px 16px;
      font-size: 11px;
      color: #00e5ff;
      background: rgba(0, 0, 0, 0.3);
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .input-area {
      padding: 12px 16px;
      background: rgba(0, 0, 0, 0.4);
      border-top: 1px solid rgba(0, 220, 255, 0.2);
      display: flex;
      gap: 8px;
    }
    input {
      flex: 1;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(0, 220, 255, 0.3);
      border-radius: 8px;
      padding: 8px 12px;
      color: #ffffff;
      outline: none;
      font-size: 13px;
    }
    input:focus { border-color: #00e5ff; box-shadow: 0 0 8px rgba(0, 220, 255, 0.4); }
    button {
      background: #00e5ff;
      color: #001e26;
      border: none;
      border-radius: 8px;
      padding: 8px 14px;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.2s, transform 0.1s;
    }
    button:hover { background: #18ffff; }
    button:active { transform: scale(0.96); }
    .mic-btn {
      background: rgba(0, 220, 255, 0.2);
      color: #00e5ff;
      border: 1px solid rgba(0, 220, 255, 0.4);
    }
    .mic-btn:hover { background: rgba(0, 220, 255, 0.35); }
  </style>
</head>
<body>
  <div class="header">
    <div class="title">
      <div class="arc"></div>
      TM OPERATING SYSTEM
    </div>
    <div class="close-btn" onclick="pywebview.api.close_window()">✕</div>
  </div>

  <div class="chat-area" id="chat">
    <div class="msg agent">Systems online, Sir. How may I assist you?</div>
  </div>

  <div class="status-bar" id="status">
    <span>●</span> Ready for commands
  </div>

  <div class="input-area">
    <input type="text" id="userInput" placeholder="Ask TM or enter command..." onkeydown="if(event.key==='Enter') sendMsg()">
    <button onclick="sendMsg()">Send</button>
    <button class="mic-btn" onclick="triggerMic()">🎙️</button>
  </div>

  <script>
    function addMsg(text, type) {
      const chat = document.getElementById('chat');
      const div = document.createElement('div');
      div.className = 'msg ' + type;
      div.innerText = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    function setStatus(text) {
      document.getElementById('status').innerHTML = '<span>●</span> ' + text;
    }

    function sendMsg() {
      const input = document.getElementById('userInput');
      const val = input.value.trim();
      if (!val) return;
      addMsg(val, 'user');
      input.value = '';
      setStatus('Thinking...');
      pywebview.api.process_query(val).then(res => {
        addMsg(res, 'agent');
        setStatus('Ready for commands');
      });
    }

    function triggerMic() {
      setStatus('Listening to microphone...');
      pywebview.api.listen_voice().then(text => {
        if (text) {
          addMsg(text, 'user');
          setStatus('Reasoning...');
          pywebview.api.process_query(text).then(res => {
            addMsg(res, 'agent');
            setStatus('Ready for commands');
          });
        } else {
          setStatus('Ready for commands');
        }
      });
    }
  </script>
</body>
</html>
"""


class HUDApi:
    def __init__(self, agent: TMAgent, ear: Ear, speaker: Speaker, window_holder: dict):
        self.agent = agent
        self.ear = ear
        self.speaker = speaker
        self.window_holder = window_holder

    def process_query(self, query: str) -> str:
        res = self.agent.execute_turn(query)
        reply = res.get("response", "Done, Sir.")
        # Speak response asynchronously
        threading.Thread(target=lambda: self.speaker.speak(reply), daemon=True).start()
        return reply

    def listen_voice(self) -> str:
        text = self.ear.listen_phrase()
        return text or ""

    def close_window(self):
        win = self.window_holder.get("win")
        if win:
            win.destroy()
        sys.exit(0)


def run_hud():
    """Launches the floating HUD desktop widget."""
    if webview is None:
        print("pywebview is required for HUD mode. Install via 'pip install pywebview'.")
        return

    config = get_config()
    agent = TMAgent(config)
    ear = Ear(config)
    speaker = Speaker(config)

    holder = {}
    api = HUDApi(agent, ear, speaker, holder)

    # Create frameless, transparent, on-top window
    window = webview.create_window(
        title="TM HUD",
        html=HUD_HTML,
        js_api=api,
        width=440,
        height=580,
        frameless=True,
        on_top=True,
        transparent=True,
        resizable=True,
    )
    holder["win"] = window

    webview.start()

