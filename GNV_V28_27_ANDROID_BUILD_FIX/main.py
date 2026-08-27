# V28.30 - Android startup/runtime fix
#
# Objetivo: impedir que o aplicativo desapareça durante a inicializacao.
# O Android/Kivy usa um diretorio privado para dados do aplicativo. Antes de
# importar o sistema GNV, mudamos o diretorio de trabalho para esse local;
# assim SQLite, JSON, configuracoes e demais arquivos com caminhos relativos
# nao tentam gravar em uma pasta externa ou somente-leitura.
#
# Tambem inicializamos a classe original MobileGNVApp corretamente. A versao
# anterior trocava __class__ mas nao executava o __init__ da classe original,
# deixando o objeto parcialmente inicializado.

import os
import sys
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp


class AndroidLauncher(App):
    """Bootstrap Android que prepara armazenamento e captura erros de startup."""

    def build(self):
        root = BoxLayout(orientation="vertical", padding=dp(18))
        self.status = Label(
            text="Inicializando o Sistema de Cálculos de GNV...",
            halign="center",
            valign="middle",
            font_size=dp(18),
        )
        self.status.bind(
            size=lambda widget, size: setattr(widget, "text_size", size)
        )
        root.add_widget(self.status)

        # Espera a primeira passagem do event loop para que Window/SDL2 esteja
        # totalmente inicializada antes do modulo grande do sistema GNV.
        Clock.schedule_once(self._load_gnv, 0.25)
        return root

    def _write_error(self, text):
        """Grava o traceback no armazenamento privado do aplicativo."""
        try:
            base = Path(self.user_data_dir)
            base.mkdir(parents=True, exist_ok=True)
            path = base / "gnv_startup_error.log"
            path.write_text(text, encoding="utf-8")
        except Exception:
            pass

    def _prepare_android_storage(self):
        """Faz todos os caminhos relativos apontarem para a area privada Android."""
        base = Path(self.user_data_dir)
        base.mkdir(parents=True, exist_ok=True)
        os.environ["GNV_APP_DATA_DIR"] = str(base)
        os.environ["HOME"] = str(base)
        os.environ["XDG_CONFIG_HOME"] = str(base / "config")
        os.environ["XDG_DATA_HOME"] = str(base / "data")
        (base / "config").mkdir(parents=True, exist_ok=True)
        (base / "data").mkdir(parents=True, exist_ok=True)
        # SQLite e arquivos relativos do programa passam a ser criados aqui.
        os.chdir(base)

    def _load_gnv(self, _dt):
        try:
            self.status.text = "Preparando armazenamento do aplicativo..."
            self._prepare_android_storage()

            self.status.text = "Carregando o sistema GNV..."
            import GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z as module

            original_class = module.MobileGNVApp

            # O objeto App ja esta rodando. Troca para a classe original e,
            # principalmente, executa o __init__ dela antes de build().
            # Sem isso, atributos criados no construtor original podem faltar.
            self.__class__ = original_class
            original_class.__init__(self)
            root = original_class.build(self)
            self.root = root

        except BaseException:
            error = traceback.format_exc()
            self._write_error(error)
            self._show_python_error(error)

    def _show_python_error(self, error):
        root = BoxLayout(
            orientation="vertical", padding=dp(12), spacing=dp(8)
        )
        title = Label(
            text="ERRO AO INICIAR O SISTEMA GNV",
            size_hint_y=None,
            height=dp(55),
            bold=True,
            font_size=dp(18),
        )
        root.add_widget(title)
        message = Label(
            text=error,
            halign="left",
            valign="top",
            font_size=dp(10),
        )
        message.bind(
            size=lambda widget, size: setattr(widget, "text_size", size)
        )
        root.add_widget(message)
        self.root = root


if __name__ == "__main__":
    AndroidLauncher().run()
