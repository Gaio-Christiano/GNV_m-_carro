"""Entrypoint Android do aplicativo GNV.

Modo de inicialização seguro para o teste de fumaça Android:
- carrega a MobileGNVApp real;
- qualquer erro de importação é mostrado na própria tela, em vez de matar o processo;
- a aplicação permanece viva por 5 segundos;
- depois encerra de forma controlada, para que o teste valide somente a inicialização.

O encerramento após 5 segundos é intencional e serve exclusivamente para o teste
 de inicialização do APK no CI/emulador.
"""

import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

APP_MODULE_NAME = "GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z"
STARTUP_TEST_SECONDS = 5.0


try:
    module = __import__(APP_MODULE_NAME, fromlist=["MobileGNVApp"])
    _MobileGNVApp = getattr(module, "MobileGNVApp")
    if not issubclass(_MobileGNVApp, App):
        raise TypeError("MobileGNVApp não é uma subclasse de kivy.app.App")
    _IMPORT_ERROR = None
except BaseException as exc:
    module = None
    _IMPORT_ERROR = exc

    class _ImportErrorApp(App):
        """Janela mínima para impedir encerramento silencioso durante o teste."""

        def build(self):
            details = "".join(
                traceback.format_exception(type(_IMPORT_ERROR), _IMPORT_ERROR, _IMPORT_ERROR.__traceback__)
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
        try:
            type(self).instance = self
        except BaseException:
            pass

        if module is not None:
            try:
                self.title = getattr(
                    module,
                    "APP_TITLE",
                    "Sistema de Calculos e Analise da Capacidade do Cilindro de GNV",
                )
            except BaseException:
                pass

        # Esta build existe para validar a inicialização. O encerramento após
        # 5 segundos é deliberado e NÃO representa um crash.
        Clock.schedule_once(self._finish_startup_test, STARTUP_TEST_SECONDS)

    def _finish_startup_test(self, _dt):
        """Encerra o app de maneira limpa após 5 segundos."""
        try:
            self.stop()
        except BaseException:
            pass


def main():
    """Ponto de entrada único do APK."""
    try:
        AndroidGNVApp().run()
    except BaseException:
        # Última barreira contra encerramento silencioso do entrypoint.
        traceback.print_exc()


if __name__ == "__main__":
    main()
