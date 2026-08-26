# V28.28 - Android bootstrap seguro
#
# O aplicativo principal permanece no arquivo original
# GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z.py.
# Este bootstrap existe para impedir que uma exceção Python de inicialização
# simplesmente feche o aplicativo no Android sem mostrar a causa.
#
# Se a inicialização falhar, o traceback é gravado em gnv_startup_error.log
# dentro do diretório privado do aplicativo e uma tela de erro permanece
# aberta no aparelho. Se a inicialização for normal, o comportamento do
# aplicativo original permanece inalterado.

import os
import traceback
from pathlib import Path


def _error_path():
    base = os.environ.get("ANDROID_PRIVATE") or os.getcwd()
    return Path(base) / "gnv_startup_error.log"


def _write_error(title, text):
    try:
        path = _error_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"{title}\n\n{text}",
            encoding="utf-8",
        )
    except Exception:
        pass


def _show_error(title, text):
    _write_error(title, text)

    try:
        from kivy.app import App
        from kivy.metrics import dp
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.scrollview import ScrollView

        class StartupErrorApp(App):
            def build(self):
                root = BoxLayout(
                    orientation="vertical",
                    padding=dp(12),
                    spacing=dp(8),
                )

                root.add_widget(
                    Label(
                        text="ERRO AO INICIAR O SISTEMA GNV",
                        size_hint_y=None,
                        height=dp(52),
                        bold=True,
                        font_size=dp(17),
                    )
                )

                scroll = ScrollView()
                message = Label(
                    text=text,
                    size_hint_y=None,
                    text_size=(dp(350), None),
                    halign="left",
                    valign="top",
                    font_size=dp(12),
                )
                message.bind(texture_size=lambda w, size: setattr(w, "height", size[1] + dp(20)))
                scroll.add_widget(message)
                root.add_widget(scroll)

                root.add_widget(
                    Button(
                        text="Fechar",
                        size_hint_y=None,
                        height=dp(50),
                        on_release=lambda *_: self.stop(),
                    )
                )
                return root

        StartupErrorApp().run()
    except Exception:
        pass


def main():
    try:
        import GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z as app_module
        app = app_module.MobileGNVApp()
        app.run()
    except Exception:
        text = traceback.format_exc()
        _show_error("Falha na inicialização do aplicativo GNV V28.28", text)


if __name__ == "__main__":
    main()
