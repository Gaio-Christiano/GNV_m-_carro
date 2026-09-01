# V28.42 - entrada Android pelo ciclo normal do Kivy
#
# PRINCIPIO:
# O aplicativo GNV precisa ser uma instancia REAL de kivy.app.App durante
# todo o ciclo de vida. Nao chamamos MobileGNVApp.build() manualmente.
#
# O launcher abaixo apenas importa a classe principal, cria uma subclasse
# fina e chama .run(). Isso permite que o Kivy configure corretamente
# App.get_running_app(), Clock, Window, root e o ciclo de eventos.

import importlib
import traceback

from kivy.app import App

APP_MODULE_NAME = "GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z"


def _importar_app():
    modulo = importlib.import_module(APP_MODULE_NAME)
    classe = getattr(modulo, "MobileGNVApp")
    if not issubclass(classe, App):
        raise TypeError("MobileGNVApp nao herda de kivy.app.App")
    return classe


MobileGNVApp = _importar_app()


class AndroidGNVApp(MobileGNVApp):
    """Ponto de entrada Android real do aplicativo GNV."""

    pass


if __name__ == "__main__":
    try:
        AndroidGNVApp().run()
    except BaseException:
        # O bootstrap do p4a tambem envia stderr para logcat.
        # Mantemos uma excecao completa em vez de esconder a causa real.
        traceback.print_exc()
        raise
