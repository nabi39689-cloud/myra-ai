from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock

Window.clearcolor = (0.04, 0.05, 0.1, 1)
Window.softinput_mode = "below_target"

tts = None

def init_tts(dt=None):
    # Android ki apni awaaz (Hindi)
    global tts
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
        Locale = autoclass("java.util.Locale")
        tts = TextToSpeech(PythonActivity.mActivity, None)
        Clock.schedule_once(lambda d: tts.setLanguage(Locale("hi", "IN")), 2)
    except Exception as e:
        print("TTS error:", e)

def speak(text):
    try:
        if tts:
            tts.speak(text, 0, None, None)
    except Exception as e:
        print("Speak error:", e)

class JarvisApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        root.add_widget(Label(
            text="J.A.R.V.I.S AI ASSISTANT",
            size_hint_y=None, height=50, bold=True,
            color=(0.3, 0.8, 1, 1)))

        self.scroll = ScrollView()
        self.chat = Label(
            text="", size_hint_y=None, halign="left", valign="top",
            color=(1, 1, 1, 1))
        self.chat.bind(
            width=lambda w, v: setattr(w, "text_size", (v, None)),
            texture_size=lambda w, v: setattr(w, "height", v[1]))
        self.scroll.add_widget(self.chat)
        root.add_widget(self.scroll)

        row = BoxLayout(size_hint_y=None, height=60, spacing=8)
        self.box = TextInput(
            hint_text="Yahan likhein...", multiline=False,
            size_hint_x=0.75)
        self.box.bind(on_text_validate=self.send)
        btn = Button(text="Send", size_hint_x=0.25)
        btn.bind(on_release=self.send)
        row.add_widget(self.box)
        row.add_widget(btn)
        root.add_widget(row)

        Clock.schedule_once(init_tts, 0.5)
        Clock.schedule_once(self.greet, 3)
        return root

    def say(self, display_text, speak_text):
        self.chat.text += "JARVIS: " + display_text + "\n\n"
        Clock.schedule_once(lambda d: setattr(self.scroll, "scroll_y", 0), 0.1)
        speak(speak_text)

    def greet(self, dt):
        self.say("Namaste sir! System taiyaar hai.",
                 "नमस्ते सर! सिस्टम तैयार है।")

    def send(self, *args):
        text = self.box.text.strip()
        self.box.text = ""
        if not text:
            return
        self.chat.text += "Aap: " + text + "\n\n"
        if text.lower() == "exit":
            self.say("Alvida sir! Phir milte hain.",
                     "अलविदा सर! फिर मिलते हैं।")
            Clock.schedule_once(lambda d: self.stop(), 3)
        else:
            self.say("Aapne kaha: " + text, "आपने कहा: " + text)

JarvisApp().run()
