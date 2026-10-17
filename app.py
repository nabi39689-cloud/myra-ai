import json
import os
import ssl
import urllib.request
import urllib.error

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

SETTINGS_PATH = os.path.join(
    os.environ.get("ANDROID_PRIVATE") or os.path.expanduser("~"),
    "myra_settings.json",
)

DEFAULT_MODEL = "gemini-3.8-flash"

SYSTEM_TEXT = (
    "You are Myra, a friendly smart assistant. "
    "Reply in the same language and script the user writes in "
    "(Hindi, Urdu, Sindhi, Roman Hindi or English). "
    "Keep answers short, warm and clear."
)


def load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(data):
    folder = os.path.dirname(SETTINGS_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


def make_ctx():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def call_gemini(api_key, model, contents):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent"
        % model
    )
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM_TEXT}]},
        "contents": contents,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
    )
    with urllib.request.urlopen(req, timeout=45, context=make_ctx()) as r:
        data = json.loads(r.read().decode("utf-8"))
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts).strip() or "(khali jawab aaya)"


def friendly_error(e):
    if isinstance(e, urllib.error.HTTPError):
        try:
            info = json.loads(e.read().decode("utf-8"))
            return "%s: %s" % (e.code, info.get("error", {}).get("message", "unknown"))
        except Exception:
            return "HTTP %s" % e.code
    return "%s: %s" % (type(e).__name__, e)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    msg = str(data.get("msg", "")).strip()
    if not msg:
        return jsonify(ok=False, reply="Kuch likhiye.")
    s = load_settings()
    key = s.get("api_key", "")
    if not key:
        return jsonify(ok=False, reply="Pehle menu mein Settings kholkar API key daalein.")
    model = (s.get("model") or DEFAULT_MODEL).strip()
    contents = []
    for h in (data.get("history") or [])[-12:]:
        if not isinstance(h, dict):
            continue
        role = "model" if h.get("role") == "model" else "user"
        contents.append(
            {"role": role, "parts": [{"text": str(h.get("text", ""))[:4000]}]}
        )
    contents.append({"role": "user", "parts": [{"text": msg[:4000]}]})
    try:
        return jsonify(ok=True, reply=call_gemini(key, model, contents))
    except Exception as e:
        return jsonify(ok=False, reply="Error " + friendly_error(e))


@app.route("/save", methods=["POST"])
def save():
    data = request.get_json(silent=True) or {}
    s = load_settings()
    new_key = str(data.get("api_key", "")).strip()
    if new_key:
        s["api_key"] = new_key
    model = str(data.get("model", "")).strip()
    s["model"] = model or DEFAULT_MODEL
    save_settings(s)
    return jsonify(ok=True)


@app.route("/logo")
def logo():
    here = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(here, "icon.png")


SETTINGS_STYLE = """
<style>
  body { margin:0; padding:20px; background:#0a0f24; color:#fff;
         font-family:Roboto,Arial,sans-serif; text-align:center; }
  h1 { color:#b36bff; font-size:38px; margin:10px 0 4px; }
  a.top { color:#8fa6ff; text-decoration:none; font-size:18px; }
  input { width:84%; max-width:420px; padding:14px 16px; font-size:17px;
          border-radius:20px; border:2px solid #4f7cff; margin:6px 0; }
  button { background:#4f7cff; color:#fff; font-size:18px; padding:12px 26px;
           margin:10px 6px; border:0; border-radius:16px; }
  .note { color:#a5a5c0; font-size:14px; }
</style>
"""

SETTINGS_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Settings</title>""" + SETTINGS_STYLE + """</head>
<body>
  <div style="text-align:left"><a class="top" href="/">&larr; Wapas</a></div>
  <h1>Settings</h1>
  <div class="note" id="status">STATUS_TEXT</div>
  <p>Gemini API key</p>
  <input id="key" type="password" placeholder="Yahan key paste karein">
  <p>Model naam</p>
  <input id="model" value="MODEL_VALUE">
  <div><button onclick="save()">Save</button></div>
  <div class="note" id="out"></div>
<script>
async function save() {
  const r = await fetch('/save', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      api_key: document.getElementById('key').value,
      model: document.getElementById('model').value
    })
  });
  const d = await r.json();
  document.getElementById('out').textContent = d.ok ? 'Save ho gaya.' : 'Save nahi hua.';
  document.getElementById('key').value = '';
}
</script>
</body></html>
"""

HOME_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Myra AI</title>
<style>
  :root { --card:#121a38; --line:#24305e; --mut:#8f9bc7; --acc:#4f7cff; }
  * { box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
  html, body { margin:0; height:100%; color:#e9edff;
    background:radial-gradient(120% 80% at 50% 15%, #16245a 0%, #0a0f24 60%);
    font-family:Roboto,Arial,sans-serif; }
  #app { height:100%; display:flex; flex-direction:column; max-width:520px; margin:0 auto; }
  header { display:flex; align-items:center; justify-content:space-between; padding:14px 18px; position:relative; }
  header .t { font-size:22px; font-weight:600; }
  .ib { background:none; border:0; color:#e9edff; font-size:28px; padding:4px 8px; }
  .av { width:42px; height:42px; border-radius:12px; border:1px solid var(--line); object-fit:cover; }
  .menu { display:none; position:absolute; top:62px; left:14px; background:#121a38;
    border:1px solid var(--line); border-radius:14px; padding:6px; z-index:5; }
  .menu a { display:block; color:#e9edff; text-decoration:none; padding:12px 18px; font-size:17px; }
  main { flex:1; overflow-y:auto; padding:0 18px 10px; }
  .view { display:none; }
  .view.on { display:block; }
  .hi { color:var(--mut); font-size:30px; margin:6px 0 0; }
  .hi b { display:block; color:#fff; font-size:40px; }
  .sub { color:var(--mut); margin:8px 0 6px; }
  .orb { position:relative; width:250px; height:250px; margin:8px auto; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    background:radial-gradient(circle, #101a44 58%, transparent 59%);
    box-shadow:0 0 50px rgba(79,124,255,.25); }
  .orb::before { content:""; position:absolute; inset:0; border-radius:50%;
    border:6px solid transparent;
    border-top-color:#8fa6ff; border-right-color:#b36bff;
    animation:spin 6s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } }
  .orb .n { font-size:38px; font-weight:700; letter-spacing:4px;
    background:linear-gradient(90deg,#8fa6ff,#ffffff,#d36bff);
    -webkit-background-clip:text; background-clip:text; color:transparent; }
  .orb small { position:absolute; top:78px; color:var(--mut); letter-spacing:3px; font-size:11px; }
  .row { display:flex; gap:10px; margin:10px 0; }
  .chip, .card { flex:1; background:rgba(18,26,56,.85); border:1px solid var(--line);
    border-radius:18px; color:#e9edff; font-size:16px; padding:14px 8px; text-align:center; }
  .card { text-align:left; padding:12px 14px; }
  .card small { color:var(--mut); display:block; }
  .card b { font-size:22px; }
  .bar { display:flex; align-items:center; gap:8px; margin:6px 18px 10px;
    background:rgba(18,26,56,.95); border:1px solid var(--line);
    border-radius:28px; padding:5px 6px 5px 18px; }
  .bar input { flex:1; min-width:0; background:none; border:0; outline:0; color:#fff;
    font-size:17px; padding:10px 0; }
  .send { background:#1c2a5c; border:0; color:#fff; width:44px; height:44px;
    border-radius:50%; font-size:20px; }
  nav { display:flex; justify-content:space-around; align-items:flex-end;
    padding:8px 6px calc(10px + env(safe-area-inset-bottom, 0px));
    background:#0d1330; border-top:1px solid var(--line); }
  nav button { background:none; border:0; color:var(--mut); font-size:13px; padding:6px 10px; }
  nav button span { display:block; font-size:22px; }
  nav button.on { color:var(--acc); }
  nav .mic { width:66px; height:66px; border-radius:50%; background:var(--acc);
    border:4px solid #0d1330; color:#fff; font-size:28px; margin-top:-34px; padding:0; }
  .msg { padding:10px 14px; border-radius:16px; margin:8px 0; max-width:90%; white-space:pre-wrap; }
  .you { background:#1c2a5c; margin-left:auto; }
  .myra { background:#2a1a5e; }
  .soon { color:var(--mut); text-align:center; margin-top:60px; font-size:18px; }
</style></head>
<body>
<div id="app">
  <header>
    <button class="ib" onclick="toggleMenu()">&#9776;</button>
    <div class="t">Myra</div>
    <img class="av" src="/logo" onerror="this.style.visibility='hidden'">
    <div class="menu" id="menu">
      <a href="/settings">&#9881; Settings</a>
      <a href="#" onclick="show('home');toggleMenu();return false;">&#127968; Home</a>
      <a href="#" id="spk" onclick="toggleSpeak();return false;">&#128266; Awaaz: ON</a>
    </div>
  </header>

  <main>
    <div class="view on" id="v-home">
      <div class="hi"><span id="greet">Namaste,</span><b>dost</b></div>
      <div class="sub">Myra aapki madad ke liye tayyar hai.</div>
      <div class="orb"><small>AI ASSISTANT</small><div class="n">M.Y.R.A</div></div>
      <div class="row">
        <button class="chip" onclick="starter('Mujhe achhe gaane suggest karo')">&#127925; Music</button>
        <button class="chip" onclick="starter('Mujhe padhai mein madad chahiye: ')">&#128214; Study</button>
        <button class="chip" onclick="starter('Aaj mera din aisa raha: ')">&#9998; Journal</button>
      </div>
      <div class="row">
        <div class="card"><small>&#9729; Weather</small><b>&mdash;</b><small>Jald aayega</small></div>
        <div class="card"><small>&#128197; Today</small><b id="day">--</b><small id="dm">--</small></div>
        <div class="card"><small>&#10084; Mood</small><b>Warm</b><small>All good</small></div>
      </div>
    </div>

    <div class="view" id="v-chat"><div id="log"></div></div>
    <div class="view" id="v-scan"><div class="soon">Scan abhi nahi bana.<br>Jald aayega.</div></div>
    <div class="view" id="v-mem"><div class="soon">Memories abhi nahi bani.<br>Jald aayengi.</div></div>
  </main>

  <div class="bar">
    <input id="msg" placeholder="Myra se kuch bhi puchhein...">
    <button class="send" onclick="sendMsg()">&#10148;</button>
  </div>

  <nav>
    <button id="n-home" class="on" onclick="show('home')"><span>&#127968;</span>Home</button>
    <button id="n-scan" onclick="show('scan')"><span>&#128247;</span>Scan</button>
    <button class="mic" onclick="voice()">&#127908;</button>
    <button id="n-mem" onclick="show('mem')"><span>&#129504;</span>Memories</button>
    <button id="n-chat" onclick="show('chat')"><span>&#128172;</span>Chat</button>
  </nav>
</div>

<script>
var chatHistory = [];
var names = ['home', 'chat', 'scan', 'mem'];

function show(name) {
  for (var i = 0; i < names.length; i++) {
    document.getElementById('v-' + names[i]).className = 'view' + (names[i] === name ? ' on' : '');
    document.getElementById('n-' + names[i]).className = (names[i] === name ? 'on' : '');
  }
}
function toggleMenu() {
  var m = document.getElementById('menu');
  m.style.display = (m.style.display === 'block') ? 'none' : 'block';
}
function starter(t) {
  var box = document.getElementById('msg');
  box.value = t;
  box.focus();
}
function add(cls, text) {
  var d = document.createElement('div');
  d.className = 'msg ' + cls;
  d.textContent = text;
  document.getElementById('log').appendChild(d);
  d.scrollIntoView();
  return d;
}
async function sendMsg() {
  var box = document.getElementById('msg');
  var text = box.value.trim();
  if (!text) return;
  show('chat');
  add('you', text);
  box.value = '';
  var wait = add('myra', '...');
  try {
    var r = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({history: chatHistory, msg: text})
    });
    var d = await r.json();
    wait.textContent = d.reply;
    if (d.ok) {
      chatHistory.push({role: 'user', text: text});
      chatHistory.push({role: 'model', text: d.reply});
      speak(d.reply);
    }
  } catch (e) {
    wait.textContent = 'Error ' + e;
  }
}
document.getElementById('msg').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') sendMsg();
});
var speakOn = true;
function toggleSpeak() {
  speakOn = !speakOn;
  document.getElementById('spk').innerHTML = speakOn ? '&#128266; Awaaz: ON' : '&#128263; Awaaz: OFF';
  if (!speakOn && window.speechSynthesis) window.speechSynthesis.cancel();
  toggleMenu();
}
function speak(text) {
  if (!speakOn || !window.speechSynthesis) return;
  try {
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.lang = /[\u0900-\u097F]/.test(text) ? 'hi-IN' : 'en-IN';
    window.speechSynthesis.speak(u);
  } catch (e) {}
}
function voice() {
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    var box = document.getElementById('msg');
    box.focus();
    alert('Is app mein mic abhi seedha nahi chalta. Keyboard ka mic (\ud83c\udfa4) dabakar bolein, phir Send dabayein.');
    return;
  }
  var r = new SR();
  r.lang = 'hi-IN';
  r.onresult = function(e) {
    document.getElementById('msg').value = e.results[0][0].transcript;
  };
  r.start();
}
(function() {
  var now = new Date();
  var h = now.getHours();
  var g = h < 5 ? 'Raat ke jaag rahe ho,' : h < 12 ? 'Shubh prabhat,' : h < 17 ? 'Namaste,' : 'Shubh sandhya,';
  document.getElementById('greet').textContent = g;
  var mons = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  document.getElementById('day').textContent = now.getDate();
  document.getElementById('dm').textContent = days[now.getDay()] + ', ' + mons[now.getMonth()];
})();
</script>
</body></html>
"""


@app.route("/")
def home():
    return HOME_PAGE


@app.route("/settings")
def settings():
    s = load_settings()
    status = "API key save hai." if s.get("api_key") else "Abhi koi API key save nahi hai."
    model = s.get("model") or DEFAULT_MODEL
    return SETTINGS_PAGE.replace("STATUS_TEXT", status).replace("MODEL_VALUE", model)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
