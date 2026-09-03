"""Entrypoint Android do aplicativo GNV.

A versão anterior criava uma nova classe Kivy App e tentava chamar métodos que
pertenciam à MobileGNVApp sem herdá-los. Isso quebrava a arquitetura do app.
Aqui o entrypoint usa a própria MobileGNVApp como classe base, preservando todo
o código original da aplicação.
"""

import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

APP_MODULE_NAME = "GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z"


try:
    module = __import__(APP_MODULE_NAME, fromlist=["MobileGNVApp"])
    _MobileGNVApp = getattr(module, "MobileGNVApp")
    if not issubclass(_MobileGNVApp, App):
        raise TypeError("MobileGNVApp não é uma subclasse de kivy.app.App")
except BaseException as exc:
    _import_error = exc

    class _ImportErrorApp(App):
        """Mantém a janela aberta e exibe o erro real de importação."""

        def build(self):
            details = "".join(
                traceback.format_exception(type(_import_error), _import_error, _import_error.__traceback__)
            )
            root = BoxLayout(padding=20)
            label = Label(
                text="ERRO AO INICIAR O SISTEMA GNV\n\n" + details,
                halign="left",
                valign="top",
            )
            label.bind(size=lambda widget, *_: setattr(widget, "text_size", widget.size))
            root.add_widget(label)
            return root

    _MobileGNVApp = _ImportErrorApp


class AndroidGNVApp(_MobileGNVApp):
    """Aplicativo Android baseado diretamente na aplicação GNV real."""

    def on_start(self):
        # Preserva o padrão esperado por versões antigas do código.
        try:
            type(self).instance = self
        except BaseException:
            pass
        try:
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
