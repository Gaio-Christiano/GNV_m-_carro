from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class SmokeTestApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=40)
        root.add_widget(Label(text='ANDROID SMOKE TEST\n\nKivy iniciou.\n\nSe esta tela permanecer aberta, o runtime Android funciona.'))
        return root

if __name__ == '__main__':
    SmokeTestApp().run()
