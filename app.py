
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Myra AI</title>
      <style>
        body {
          background: #080817;
          color: white;
          font-family: Arial;
          text-align: center;
          padding: 30px 15px;
        }
        h1 { color: #b66cff; font-size: 42px; }
        button, input {
          padding: 14px;
          border-radius: 15px;
          border: 1px solid #8650ff;
          margin: 8px;
        }
        button {
          background: #6d28d9;
          color: white;
          font-size: 16px;
        }
        input { width: 80%; }
        #reply { margin-top: 25px; }
      </style>
    </head>
    <body>
      <h1>Myra AI</h1>
      <p>Your Smart AI Assistant</p>
      <input id="msg" placeholder="Apna message likhein">
      <br>
      <button onclick="sendMsg()">Send</button>
      <button onclick="listen()">🎤 Voice</button>
      <div id="reply"></div>
      <script>
        async function sendMsg() {
          let m = document.getElementById('msg').value;
          document.getElementById('reply').innerText =
            'Myra AI: Aapka message mila: ' + m;
        }
        function listen() {
          const SR = window.SpeechRecognition ||
                     window.webkitSpeechRecognition;
          if (!SR) {
            alert('Voice recognition ke liye Chrome use karein.');
            return;
          }
          let r = new SR();
          r.lang = 'hi-IN';
          r.onresult = e => {
            document.getElementById('msg').value =
              e.results[0][0].transcript;
          };
          r.start();
        }
      </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

