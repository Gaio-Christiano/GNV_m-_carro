# V28.35 - Android startup seguro e armazenamento privado
#
# O APK anterior ainda podia morrer antes de AndroidGNVApp.build() porque o
# modulo principal do sistema era importado no topo do arquivo. Qualquer
# excecao durante esse import encerrava a Activity antes de nosso tratamento.
#
# Tambem havia um segundo risco: qualquer arquivo criado por caminho relativo
# poderia apontar para o diretorio de instalacao do APK, que e somente leitura.
# No Android, o armazenamento privado do aplicativo e gravavel sem permissao
# de armazenamento externo. O bootstrap abaixo muda o diretorio de trabalho
# para esse armazenamento ANTES de importar o programa principal.

import os
import sqlite3
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout


# ---------------------------------------------------------------------------
# Android: estabelecer um diretorio de trabalho gravavel ANTES de qualquer
# importacao do programa principal.
# ---------------------------------------------------------------------------
_ANDROID_STORAGE = None
_ANDROID_STORAGE_ERROR = None

try:
    from android.storage import app_storage_path
    _ANDROID_STORAGE = Path(app_storage_path())
    _ANDROID_STORAGE.mkdir(parents=True, exist_ok=True)
    os.chdir(_ANDROID_STORAGE)
    os.environ["HOME"] = str(_ANDROID_STORAGE)
    os.environ["XDG_CONFIG_HOME"] = str(_ANDROID_STORAGE / ".config")
    os.environ["XDG_DATA_HOME"] = str(_ANDROID_STORAGE / ".local" / "share")
    Path(os.environ["XDG_CONFIG_HOME"]).mkdir(parents=True, exist_ok=True)
    Path(os.environ["XDG_DATA_HOME"]).mkdir(parents=True, exist_ok=True)
except Exception as exc:
    _ANDROID_STORAGE_ERROR = exc


# ---------------------------------------------------------------------------
# Importacao protegida.
# Se houver uma biblioteca ou import incompatível com Android, o APK agora
# permanece aberto e mostra o traceback em vez de simplesmente desaparecer.
# ---------------------------------------------------------------------------
_IMPORT_ERROR = None
app_module = None
MobileGNVApp = None

try:
    import GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z as app_module
    from GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z import MobileGNVApp
except BaseException as exc:
    _IMPORT_ERROR = exc


def _error_text(prefix, exc):
    lines = [
        prefix,
        "",
        f"Tipo: {type(exc).__name__}",
        f"Mensagem: {exc}",
        "",
        traceback.format_exc(),
    ]
    if _ANDROID_STORAGE is not None:
        lines.extend(["", f"Android app storage: {_ANDROID_STORAGE}"])
    if _ANDROID_STORAGE_ERROR is not None:
        lines.extend([
            "",
            "Falha ao preparar armazenamento Android:",
            f"{type(_ANDROID_STORAGE_ERROR).__name__}: {_ANDROID_STORAGE_ERROR}",
        ])
    return "\n".join(lines)


if _IMPORT_ERROR is not None:

    class AndroidGNVApp(App):
        """Tela de diagnóstico para falhas ocorridas antes do build do app."""

        def build(self):
            self.title = "GNV - Erro de inicializacao"
            text = _error_text("ERRO AO IMPORTAR O SISTEMA GNV", _IMPORT_ERROR)
            try:
                base = _ANDROID_STORAGE or Path(self.user_data_dir)
                base.mkdir(parents=True, exist_ok=True)
                (base / "startup_error.log").write_text(text, encoding="utf-8")
            except Exception:
                pass
            root = BoxLayout(orientation="vertical", padding=24, spacing=16)
            root.add_widget(Label(text=text, halign="left", valign="top"))
            return root

else:

    class AndroidGNVApp(MobileGNVApp):
        """MobileGNVApp com inicializacao Android tolerante a falhas."""

        def _write_startup_error(self, exc):
            text = _error_text("ERRO AO INICIAR O SISTEMA GNV", exc)
            try:
                p = _ANDROID_STORAGE or Path(getattr(self, "user_data_dir", "."))
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
            """Abre o SQLite persistente somente depois da UI estar visivel."""
            try:
                # Preferimos explicitamente o armazenamento privado Android.
                # Isso elimina qualquer dependencia de /sdcard ou pasta publica.
                base = _ANDROID_STORAGE or Path(self.user_data_dir)
                base.mkdir(parents=True, exist_ok=True)

                teste = base / ".storage_test"
                teste.write_text("ok", encoding="utf-8")
                teste.unlink(missing_ok=True)

                db_path = base / "gnv_dados.db"
                self.db_path = str(db_path)
                self.config_path = base / "configuracoes.json"
                self.base_dir = base
                self.banco.nome_banco = str(db_path)

                if getattr(self.banco, "conexao", None) is not None:
                    try:
                        self.banco.conexao.close()
                    except Exception:
                        pass

                self.banco.conectar()
                self.banco.criar_tabela()
                self.banco.criar_indices()

                # Atualiza somente telas que existem nesta versao.
                for method_name in (
                    "_refresh_history",
                    "_refresh_sqlite",
                    "_refresh_total",
                    "_refresh_chart",
                ):
                    method = getattr(self, method_name, None)
                    if callable(method):
                        try:
                            method()
                        except Exception:
                            pass

                return True
            except BaseException as exc:
                text = self._write_startup_error(exc)
                self._show_startup_error(text)
                return False

        def build(self):
            # O build original abre o SQLite durante a construcao da UI.
            # Durante essa fase usamos memoria para que armazenamento nao
            # consiga derrubar a Activity no splash.
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
                error_root = BoxLayout(
                    orientation="vertical", padding=24, spacing=16
                )
                error_root.add_widget(
                    Label(text=text, halign="left", valign="top")
                )
                return error_root
            finally:
                banco_cls.conectar = original_conectar

            # O Kivy ja recebeu a raiz; agora abrimos o arquivo SQLite real.
            Clock.schedule_once(self._finish_database_initialization, 0)
            return root


if __name__ == "__main__":
    AndroidGNVApp().run()
