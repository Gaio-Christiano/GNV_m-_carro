# V28.32 - Android runtime fix
#
# Corrige a arquitetura do launcher Android.
# A versao anterior transformava dinamicamente AndroidLauncher em
# MobileGNVApp com self.__class__ = original_class. Isso mistura o estado
# interno de dois objetos Kivy App e pode encerrar a Activity durante a
# inicializacao.
#
# Agora o launcher continua sendo o App que executa o event loop. Ele cria
# uma instancia NORMAL de MobileGNVApp, chama o build() dela e usa a arvore
# retornada como root. Os callbacks continuam ligados ao objeto real do GNV.
# O armazenamento e preparado antes do import do sistema principal.

import os
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp


class AndroidLauncher(App):
    """Launcher Android sem troca dinamica de classe Kivy."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gnv_app = None
        self.status = None

    def build(self):
        root = BoxLayout(orientation="vertical", padding=dp(18))
        self.status = Label(
            text="Inicializando o Sistema de Calculos de GNV...",
            halign="center",
            valign="middle",
            font_size=dp(18),
        )
        self.status.bind(
            size=lambda widget, size: setattr(widget, "text_size", size)
        )
        root.add_widget(self.status)

        # Primeiro cria a Window/SDL2. Depois carrega o aplicativo grande.
        Clock.schedule_once(self._start_gnv, 0.50)
        return root

    def _app_dir(self):
        base = Path(self.user_data_dir)
        base.mkdir(parents=True, exist_ok=True)
        return base

    def _write_error(self, title, text):
        try:
            base = self._app_dir()
            path = base / "gnv_startup_error.log"
            path.write_text(title + "\n\n" + text, encoding="utf-8")
        except Exception:
            pass

    def _show_error(self, title, text):
        root = BoxLayout(
            orientation="vertical", padding=dp(12), spacing=dp(8)
        )
        root.add_widget(
            Label(
                text=title,
                size_hint_y=None,
                height=dp(60),
                bold=True,
                font_size=dp(17),
            )
        )
        msg = Label(text=text, halign="left", valign="top", font_size=dp(10))
        msg.bind(size=lambda widget, size: setattr(widget, "text_size", size))
        root.add_widget(msg)
        self.root = root

    def _start_gnv(self, _dt):
        try:
            self.status.text = "Preparando armazenamento..."
            base = self._app_dir()

            # Todo caminho relativo usado pelo sistema passa a apontar para
            # o armazenamento privado do aplicativo.
            os.chdir(base)
            os.environ["GNV_APP_DATA_DIR"] = str(base)

            self.status.text = "Carregando sistema GNV..."

            # Import tardio: o modulo principal importa Window/SDL2 e somente
            # deve ser carregado depois que o primeiro ciclo Kivy ja iniciou.
            import importlib
            module = importlib.import_module(
                "GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z"
            )

            # INSTANCIA REAL: nao usamos __class__ para transformar o launcher.
            gnv = module.MobileGNVApp()
            self.gnv_app = gnv
            module.MobileGNVApp.instance = gnv

            self.status.text = "Inicializando banco e interface..."

            # O build original ja usa App.user_data_dir para criar:
            #   gnv_dados.db
            #   configuracoes.json
            # Portanto nao e necessaria permissao de armazenamento externo.
            root = gnv.build()
            if root is None:
                raise RuntimeError("MobileGNVApp.build() retornou None")

            self.root = root

            # Mantem a instancia real disponivel para eventuais callbacks.
            self.gnv_app.root = root

        except BaseException:
            error = traceback.format_exc()
            self._write_error("ERRO AO INICIAR SISTEMA GNV", error)
            self._show_error("ERRO AO INICIAR O SISTEMA GNV", error)


if __name__ == "__main__":
    AndroidLauncher().run()
