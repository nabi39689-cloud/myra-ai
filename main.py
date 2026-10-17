import threading, time, socket, traceback
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock

PORT = 5000
LOG = ["Myra AI shuru ho raha hai..."]

def add(msg):
    LOG.append(str(msg))

def run_server():
    try:
        import app as myra
        add("app.py import ho gaya")
        myra.app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)
    except Exception:
        add("SERVER ERROR:\n" + traceback.format_exc())

def wait_server():
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", PORT), 0.3).close()
            return True
        except OSError:
            time.sleep(0.2)
    return False

def open_webview():
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        url = "http://127.0.0.1:%d" % PORT
        intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        PythonActivity.mActivity.startActivity(intent)
        add("browser khul gaya")
    except Exception:
        add("BROWSER ERROR:\n" + traceback.format_exc())

def starter():
    threading.Thread(target=run_server, daemon=True).start()
    if wait_server():
        add("server chal gaya")
        open_webview()
    else:
        add("server 20 second me nahi chala")

class MyraApp(App):
    def build(self):
        self.lbl = Label(text="", halign="left", valign="top")
        self.lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        Clock.schedule_interval(self.refresh, 0.5)
        return self.lbl

    def refresh(self, dt):
        self.lbl.text = "\n".join(LOG)

    def on_start(self):
        threading.Thread(target=starter, daemon=True).start()

MyraApp().run()
