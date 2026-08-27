# V28.29 - Android startup fix
#
# O problema das versões anteriores é que o módulo principal importava
# `kivy.core.window.Window` durante o carregamento do módulo. No Android,
# uma falha nativa do provider SDL2 nesse momento pode encerrar o processo
# antes que um try/except Python consiga mostrar o erro.
#
# Este launcher inicia primeiro uma aplicação Kivy mínima. Assim a Window/SDL2
# já está criada pelo Activity antes de o módulo grande do sistema GNV ser
# importado. Depois disso, o launcher muda dinamicamente para a classe
# MobileGNVApp original e executa o build normal dela.

import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp


class AndroidLauncher(App):
    """Inicializa o runtime Kivy antes de carregar o aplicativo GNV."""

    def build(self):
        root = BoxLayout(orientation="vertical", padding=dp(18))
        self.status = Label(
            text="Inicializando o Sistema de Cálculos de GNV...",
            halign="center",
            valign="middle",
            font_size=dp(18),
        )
        self.status.bind(size=lambda widget, size: setattr(widget, "text_size", size))
        root.add_widget(self.status)

        # O primeiro ciclo do Kivy já terá criado Window/SDL2. Só então
        # carregamos o módulo grande, evitando a importação prematura.
        Clock.schedule_once(self._load_gnv, 0.25)
        return root

    def _write_error(self, text):
        try:
            from pathlib import Path
            import os
            base = os.environ.get("ANDROID_PRIVATE") or self.user_data_dir
            path = Path(base) / "gnv_startup_error.log"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        except Exception:
            pass

    def _load_gnv(self, _dt):
        try:
            self.status.text = "Carregando o sistema GNV..."

            import GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z as module

            original_class = module.MobileGNVApp

            # O objeto que já está registrado como App em execução passa a ser
            # a classe original. Isso mantém App.get_running_app() apontando
            # para o MobileGNVApp e evita um segundo App.run() aninhado.
            self.__class__ = original_class

            # build() do aplicativo original cria todas as abas, banco,
            # configurações e interface. O Window já foi inicializado.
            root = original_class.build(self)
            self.root = root

        except Exception:
            error = traceback.format_exc()
            self._write_error(error)
            self._show_python_error(error)

    def _show_python_error(self, error):
        # Mantém o aplicativo aberto e mostra o traceback em vez de simplesmente
        # desaparecer quando o problema for uma exceção Python.
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
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
            font_size=dp(11),
        )
        message.bind(size=lambda widget, size: setattr(widget, "text_size", size))
        root.add_widget(message)
        self.root = root


if __name__ == "__main__":
    AndroidLauncher().run()
