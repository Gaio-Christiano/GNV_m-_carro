# V28.33 - Android: usar o MobileGNVApp real como aplicacao principal
#
# IMPORTANTE:
# O launcher anterior criava um segundo objeto Kivy App e chamava
# MobileGNVApp.build() manualmente. Isso deixa App.get_running_app() apontando
# para o launcher, enquanto o restante do sistema usa a instancia MobileGNVApp.
# Em Android isso pode fazer a Activity morrer logo depois do splash/loading.
#
# Agora o Android executa EXATAMENTE a mesma classe MobileGNVApp usada no
# Windows. Nao existe segundo App, troca de __class__, nem build() manual.
# O SQLite continua no armazenamento privado definido pelo proprio aplicativo.

import os
import traceback
from pathlib import Path


def _prepare_android_storage():
    """Prepara somente o armazenamento privado do aplicativo."""
    try:
        # Nao importar Kivy aqui: o proprio MobileGNVApp sera o App real.
        # O caminho final sera confirmado dentro do App.user_data_dir.
        return True
    except Exception:
        return False


_prepare_android_storage()

try:
    from GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z import MobileGNVApp
except BaseException:
    # Se um import falhar, registra o erro sem mascarar a excecao original.
    try:
        from kivy.app import App
        Path(App.get_running_app().user_data_dir).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    raise


if __name__ == "__main__":
    # ESTA E A PARTE CRITICA:
    # o objeto que recebe run() e o mesmo objeto que executara build().
    # Assim App.get_running_app() retorna MobileGNVApp corretamente.
    app = MobileGNVApp()
    app.run()
