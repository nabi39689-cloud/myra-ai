import json
import os
import ssl
import urllib.request
import urllib.error

from flask import Flask, request, jsonify

app = Flask(__name__)

SETTINGS_PATH = os.path.join(
    os.environ.get("ANDROID_PRIVATE") or os.path.expanduser("~"),
    "myra_settings.json",
)

DEFAULT_MODEL = "gemini-2.5-flash"

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
        return jsonify(ok=False, reply="Pehle upar Settings mein API key daalein.")
    model = s.get("model") or DEFAULT_MODEL
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


STYLE = """
<style>
  body { margin:0; padding:20px; background:#070812; color:#fff;
         font-family:Roboto,Arial,sans-serif; text-align:center; }
  h1 { color:#b36bff; font-size:42px; margin:10px 0 4px; }
  .sub { margin-bottom:18px; }
  a.top { color:#b36bff; text-decoration:none; font-size:18px; }
  input { width:84%; max-width:420px; padding:14px 16px; font-size:17px;
          border-radius:20px; border:2px solid #7c3aed; margin:6px 0; }
  button { background:#6d28d9; color:#fff; font-size:18px; padding:12px 22px;
           margin:8px 6px; border:1px solid #8b5cf6; border-radius:16px; }
  #log { margin-top:18px; text-align:left; max-width:460px; margin-left:auto;
         margin-right:auto; }
  .you { background:#1e1b4b; padding:10px 14px; border-radius:14px; margin:8px 0; }
  .myra { background:#2e1065; padding:10px 14px; border-radius:14px; margin:8px 0; }
  .note { color:#a5a5c0; font-size:14px; }
</style>
"""

CHAT_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Myra AI</title>""" + STYLE + """</head>
<body>
  <div style="text-align:right"><a class="top" href="/settings">&#9881; Settings</a></div>
  <h1>Myra AI</h1>
  <div class="sub">Your Smart AI Assistant</div>
  <input id="msg" placeholder="Apna message likhein">
  <div>
    <button onclick="send()">Send</button>
    <button onclick="voice()">&#127908; Voice</button>
  </div>
  <div id="log"></div>
<script>
let history = [];
function add(cls, text) {
  const d = document.createElement('div');
  d.className = cls;
  d.textContent = text;
  document.getElementById('log').prepend(d);
  return d;
}
async function send() {
  const box = document.getElementById('msg');
  const text = box.value.trim();
  if (!text) return;
  add('you', 'Aap: ' + text);
  box.value = '';
  const wait = add('myra', 'Myra AI: ...');
  try {
    const r = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({history: history, msg: text})
    });
    const d = await r.json();
    wait.textContent = 'Myra AI: ' + d.reply;
    if (d.ok) {
      history.push({role: 'user', text: text});
      history.push({role: 'model', text: d.reply});
    }
  } catch (e) {
    wait.textContent = 'Myra AI: Error ' + e;
  }
}
document.getElementById('msg').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') send();
});
function voice() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    alert('Is ek jagah voice abhi kaam nahi karta.');
    return;
  }
  const r = new SR();
  r.lang = 'hi-IN';
  r.onresult = function(e) {
    document.getElementById('msg').value = e.results[0][0].transcript;
  };
  r.start();
}
</script>
</body></html>
"""

SETTINGS_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Settings</title>""" + STYLE + """</head>
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


@app.route("/")
def home():
    return CHAT_PAGE


@app.route("/settings")
def settings():
    s = load_settings()
    status = "API key save hai." if s.get("api_key") else "Abhi koi API key save nahi hai."
    model = s.get("model") or DEFAULT_MODEL
    page = SETTINGS_PAGE.replace("STATUS_TEXT", status).replace("MODEL_VALUE", model)
    return page


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
