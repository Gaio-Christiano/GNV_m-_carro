# V28.31 - Android startup fix: SQLite late initialization
#
# O aplicativo era encerrado logo depois do splash. O sistema GNV cria o
# SQLite durante build(), antes da primeira tela ficar disponível. No Android,
# qualquer problema nessa operação pode matar a Activity antes de o usuario
# enxergar o erro.
#
# Esta versao faz a inicializacao visual primeiro e inicializa o SQLite somente
# depois que a janela Kivy esta rodando. O banco fica sempre em user_data_dir,
# que e o armazenamento privado do aplicativo e nao exige permissao externa.

import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp


class AndroidLauncher(App):
    """Bootstrap Android seguro para a inicializacao do sistema GNV."""

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
        Clock.schedule_once(self._load_gnv, 0.25)
        return root

    def _write_error(self, text):
        try:
            base = Path(self.user_data_dir)
            base.mkdir(parents=True, exist_ok=True)
            (base / "gnv_startup_error.log").write_text(text, encoding="utf-8")
        except Exception:
            pass

    def _load_gnv(self, _dt):
        try:
            self.status.text = "Carregando o sistema GNV..."
            import GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z as module

            original_class = module.MobileGNVApp
            banco_class = module.BancoGNV
            original_build = original_class.build

            # -------------------------------------------------------------
            # IMPORTANTE: a classe original cria/conecta o SQLite no inicio
            # do build(). No Android, fazemos essa parte depois da primeira
            # tela para que um problema no banco nao derrube a Activity.
            # -------------------------------------------------------------
            original_connect = banco_class.conectar
            original_create_table = banco_class.criar_tabela
            original_create_indexes = banco_class.criar_indices

            banco_class.conectar = lambda self: None
            banco_class.criar_tabela = lambda self: None
            banco_class.criar_indices = lambda self: None

            # O App ja esta rodando. Trocar a classe exige executar o
            # construtor original; a versao anterior nao fazia isso.
            self.__class__ = original_class
            original_class.__init__(self)
            root = original_build(self)
            self.root = root

            # Restaura os metodos originais antes da inicializacao real.
            banco_class.conectar = original_connect
            banco_class.criar_tabela = original_create_table
            banco_class.criar_indices = original_create_indexes

            # Inicializa o SQLite somente agora, com a janela ja ativa.
            Clock.schedule_once(self._init_database_after_ui, 0.10)

        except BaseException:
            error = traceback.format_exc()
            self._write_error(error)
            self._show_error(error)

    def _init_database_after_ui(self, _dt):
        try:
            self.status.text = "Inicializando banco de dados..."

            # MobileGNVApp.build() ja criou base_dir/db_path e BancoGNV.
            self.banco.conectar()
            self.banco.criar_tabela()
            self.banco.criar_indices()

            # Atualiza as telas que dependem do banco depois da conexao.
            if hasattr(self, "_refresh_all"):
                self._refresh_all()

            if hasattr(self, "_apply_all_visual_now"):
                Clock.schedule_once(lambda __dt: self._apply_all_visual_now(), 0)

        except BaseException:
            error = traceback.format_exc()
            self._write_error("ERRO SQLITE / ARMAZENAMENTO ANDROID\n\n" + error)

            # Mantem o aplicativo aberto para mostrar o erro em vez de fechar.
            try:
                if hasattr(self, "sqlite_result"):
                    self.sqlite_result.set_text(
                        "ERRO AO INICIALIZAR O BANCO SQLITE NO ANDROID:\n\n" + error
                    )
                self.status.text = "ERRO NO BANCO SQLITE - aplicativo mantido aberto para diagnostico"
            except Exception:
                self._show_error(error)

    def _show_error(self, error):
        root = BoxLayout(
            orientation="vertical", padding=dp(12), spacing=dp(8)
        )
        root.add_widget(
            Label(
                text="ERRO AO INICIAR O SISTEMA GNV",
                size_hint_y=None,
                height=dp(55),
                bold=True,
                font_size=dp(18),
            )
        )
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
