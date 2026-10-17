import socket, threading, time
from kivy.app import App
from kivy.uix.label import Label
from android.runnable import run_on_ui_thread
from jnius import autoclass

PORT = 5000

def run_server():
    import app as myra
    myra.app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

def wait_server():
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", PORT), 0.3).close()
            return True
        except OSError:
            time.sleep(0.2)
    return False

@run_on_ui_thread
def open_webview():
    WebView = autoclass("android.webkit.WebView")
    WebViewClient = autoclass("android.webkit.WebViewClient")
    activity = autoclass("org.kivy.android.PythonActivity").mActivity
    wv = WebView(activity)
    s = wv.getSettings()
    s.setJavaScriptEnabled(True)
    s.setDomStorageEnabled(True)
    wv.setWebViewClient(WebViewClient())
    activity.setContentView(wv)
    wv.loadUrl("http://127.0.0.1:%d" % PORT)

def starter():
    threading.Thread(target=run_server, daemon=True).start()
    if wait_server():
        open_webview()

class MyraApp(App):
    def build(self):
        return Label(text="Myra AI")
    def on_start(self):
        threading.Thread(target=starter, daemon=True).start()

MyraApp().run()
