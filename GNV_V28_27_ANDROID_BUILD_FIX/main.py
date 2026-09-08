"""Entrypoint Android do sistema GNV.

Esta versão NÃO encerra o aplicativo após alguns segundos.
O objetivo é executar a aplicação real e, caso o build() falhe no Android,
mostrar a exceção diretamente na tela em vez de deixar o Android voltar para
"Loading" e fechar silenciosamente.
"""

import os
import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

APP_MODULE_NAME = "GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z"


def _error_widget(title, exc):
    """Cria uma tela de diagnóstico que permanece aberta."""
    details = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    text = (
        title
        + "\n\n"
        + details
        + "\n\nO aplicativo foi mantido aberto para diagnóstico."
    )
    root = BoxLayout(orientation="vertical", padding=20)
    label = Label(text=text, halign="left", valign="top")
    label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
    root.add_widget(label)
    return root


try:
    module = __import__(APP_MODULE_NAME, fromlist=["MobileGNVApp"])
    _MobileGNVApp = getattr(module, "MobileGNVApp")
    if not issubclass(_MobileGNVApp, App):
        raise TypeError("MobileGNVApp não é uma subclasse de kivy.app.App")
    _IMPORT_ERROR = None
except BaseException as exc:
    module = None
    _MobileGNVApp = None
    _IMPORT_ERROR = exc


class AndroidGNVApp(App if _MobileGNVApp is None else _MobileGNVApp):
    """Executa o aplicativo GNV real sem encerramento artificial."""

    instance = None

    def build(self):
        AndroidGNVApp.instance = self

        if _IMPORT_ERROR is not None:
            return _error_widget("ERRO AO IMPORTAR O SISTEMA GNV", _IMPORT_ERROR)

        try:
            # Chama EXATAMENTE o build da aplicação original.
            root = super().build()
            return root
        except BaseException as exc:
            # O ponto mais importante desta correção: erros dentro de
            # MobileGNVApp.build() não podem resultar em fechamento silencioso.
            try:
                self.title = "ERRO DE INICIALIZAÇÃO - GNV"
                return _error_widget("ERRO DURANTE A INICIALIZAÇÃO DO SISTEMA GNV", exc)
            except BaseException:
                raise

    def on_start(self):
        """Mantém o aplicativo aberto normalmente."""
        try:
            AndroidGNVApp.instance = self
        except BaseException:
            pass

        # NÃO existe mais Clock.schedule_once(self.stop, 5).
        # O APK de demonstração deve permanecer aberto para uso normal.
        try:
            if module is not None:
                self.title = getattr(
                    module,
                    "APP_TITLE",
                    "Sistema de Calculos e Analise da Capacidade do Cilindro de GNV",
                )
        except BaseException:
            pass



def main():
    """Ponto de entrada único do APK."""
    AndroidGNVApp().run()


if __name__ == "__main__":
    main()
