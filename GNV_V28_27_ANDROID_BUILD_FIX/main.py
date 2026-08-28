# V28.34 - Android startup seguro
#
# O aplicativo Python funciona no Windows, mas o APK fechava logo apos
# "Loading...". O ponto critico identificado no codigo era a inicializacao
# sincrona do SQLite dentro de build(). Em Android, qualquer excecao nesse
# ponto mata a Activity antes de a interface ficar visivel.
#
# Esta entrada faz duas coisas:
# 1) durante a montagem inicial da UI, o BancoGNV usa SQLite :memory:;
# 2) depois que o Kivy ja colocou a interface na tela, o banco real e aberto
#    no diretorio privado gravavel de user_data_dir.
#
# Assim, se houver qualquer problema de armazenamento, o aplicativo NAO some:
# o erro fica visivel na propria tela e tambem e gravado em startup_error.log.

import sqlite3
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

import GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z as app_module
from GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z import MobileGNVApp


class AndroidGNVApp(MobileGNVApp):
    """MobileGNVApp com inicializacao Android tolerante a falhas."""

    def _write_startup_error(self, exc):
        text = "\n".join([
            "ERRO AO INICIAR O SISTEMA GNV",
            "",
            f"Tipo: {type(exc).__name__}",
            f"Mensagem: {exc}",
            "",
            traceback.format_exc(),
        ])
        try:
            p = Path(getattr(self, "user_data_dir", "."))
            p.mkdir(parents=True, exist_ok=True)
            (p / "startup_error.log").write_text(text, encoding="utf-8")
        except Exception:
            pass
        return text

    def _show_startup_error(self, text):
        try:
            root = BoxLayout(orientation="vertical", padding=24, spacing=16)
            root.add_widget(Label(text=text, halign="left", valign="top"))
            self.root = root
        except Exception:
            pass

    def _finish_database_initialization(self, _dt):
        """Troca o banco temporario pelo SQLite persistente do Android."""
        try:
            base = Path(self.user_data_dir)
            base.mkdir(parents=True, exist_ok=True)

            # Teste real de escrita no diretorio privado do aplicativo.
            teste = base / ".storage_test"
            teste.write_text("ok", encoding="utf-8")
            teste.unlink(missing_ok=True)

            db_path = base / "gnv_dados.db"
            self.db_path = str(db_path)
            self.config_path = base / "configuracoes.json"
            self.banco.nome_banco = str(db_path)

            if getattr(self.banco, "conexao", None) is not None:
                try:
                    self.banco.conexao.close()
                except Exception:
                    pass

            # Conexao persistente no armazenamento privado do app.
            self.banco.conectar()
            self.banco.criar_tabela()
            self.banco.criar_indices()

            # Atualiza as telas que consultam o banco.
            for method_name in ("_refresh_history", "_refresh_sqlite", "_refresh_total", "_refresh_chart"):
                method = getattr(self, method_name, None)
                if callable(method):
                    try:
                        method()
                    except Exception:
                        pass

            return True
        except Exception as exc:
            text = self._write_startup_error(exc)
            self._show_startup_error(text)
            return False

    def build(self):
        # O build original abre o SQLite imediatamente. Para impedir que uma
        # falha Android mate a Activity durante o splash, isolamos somente
        # essa conexao durante a construcao da interface.
        banco_cls = app_module.BancoGNV
        original_conectar = banco_cls.conectar

        def conectar_temporario(banco):
            banco.conexao = sqlite3.connect(":memory:")
            banco.cursor = banco.conexao.cursor()

        banco_cls.conectar = conectar_temporario
        try:
            root = super().build()
        except BaseException as exc:
            text = self._write_startup_error(exc)
            self.title = "GNV - Erro de inicializacao"
            error_root = BoxLayout(orientation="vertical", padding=24, spacing=16)
            error_root.add_widget(Label(text=text, halign="left", valign="top"))
            return error_root
        finally:
            banco_cls.conectar = original_conectar

        # O Kivy ja recebeu a raiz. So agora acessamos o armazenamento real.
        Clock.schedule_once(self._finish_database_initialization, 0)
        return root


if __name__ == "__main__":
    AndroidGNVApp().run()
