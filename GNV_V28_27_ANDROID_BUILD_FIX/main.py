# V28.39 - Android: startup minimo, import tardio e teste de armazenamento
#
# Nova abordagem de diagnostico:
# - a GUI Python sobe antes do modulo GNV grande;
# - armazenamento interno e externo sao testados separadamente;
# - permissoes externas sao solicitadas em runtime;
# - somente depois o modulo GNV e importado;
# - se o import falhar, o erro fica visivel na propria tela;
# - SQLite real continua sendo aberto somente depois da GUI.

import os
import sqlite3
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

APP_MODULE_NAME = "GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z"


def safe_text(exc):
    return "\n".join([f"{type(exc).__name__}: {exc}", "", traceback.format_exc()])


def write_log(base, lines):
    try:
        base.mkdir(parents=True, exist_ok=True)
        (base / "startup_android.log").write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass


class AndroidBootstrapApp(App):
    def build(self):
        self.title = "GNV V28.39"
        self.status = Label(text="INICIANDO...", halign="left", valign="top")
        self.status.bind(size=lambda w, *_: setattr(w, "text_size", (w.width - 30, None)))
        root = BoxLayout(orientation="vertical", padding=15, spacing=10)
        root.add_widget(self.status)
        self.btn = Button(text="Continuar para o sistema GNV", size_hint_y=None, height=50, disabled=True)
        self.btn.bind(on_release=self._load_real_app)
        root.add_widget(self.btn)
        Clock.schedule_once(self._startup_stage_1, 0.30)
        return root

    def _startup_stage_1(self, _dt):
        lines = ["GNV V28.39 - diagnostico Android", ""]
        self._log_lines = lines
        self._set("ETAPA 1/5\nInicializando Kivy... OK\n\nETAPA 2/5\nTestando armazenamento interno...")

        try:
            from android.storage import app_storage_path
            self.internal = Path(app_storage_path())
        except Exception:
            self.internal = Path(self.user_data_dir)

        try:
            self.internal.mkdir(parents=True, exist_ok=True)
            p = self.internal / ".startup_internal_test"
            p.write_text("OK", encoding="utf-8")
            interno = p.read_text(encoding="utf-8")
            p.unlink(missing_ok=True)
            lines.append(f"ETAPA 1 KIVY: OK")
            lines.append(f"ETAPA 2 INTERNO: OK ({interno})")
        except Exception as exc:
            lines.append("ETAPA 2 INTERNO: FALHOU")
            lines.append(safe_text(exc))

        # Teste EXPLICITO solicitado: tenta o armazenamento publico primario.
        try:
            from android.permissions import request_permissions, Permission
            try:
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            except Exception as exc:
                lines.append(f"PEDIDO DE PERMISSAO EXTERNA: {type(exc).__name__}: {exc}")
        except Exception as exc:
            lines.append(f"API DE PERMISSAO: {type(exc).__name__}: {exc}")

        try:
            from android.storage import primary_external_storage_path
            self.external = Path(primary_external_storage_path())
            test_dir = self.external / "GNV_m-_carro_test"
            test_dir.mkdir(parents=True, exist_ok=True)
            p = test_dir / ".startup_external_test"
            p.write_text("OK", encoding="utf-8")
            externo = p.read_text(encoding="utf-8")
            p.unlink(missing_ok=True)
            lines.append(f"ETAPA 3 EXTERNO: OK ({externo}) - {self.external}")
        except Exception as exc:
            self.external = None
            lines.append("ETAPA 3 EXTERNO: FALHOU/NEGADO")
            lines.append(safe_text(exc))

        write_log(self.internal, lines)
        Clock.schedule_once(lambda _dt: self._startup_stage_2(lines), 0.50)

    def _startup_stage_2(self, lines):
        external = "OK" if self.external else "NEGADO/INDISPONIVEL"
        self._set(
            "ETAPA 1/5 - Kivy: OK\n"
            "ETAPA 2/5 - armazenamento interno: OK\n"
            f"ETAPA 3/5 - armazenamento externo: {external}\n\n"
            "ETAPA 4/5 - SQLite de teste..."
        )
        try:
            db = self.internal / "startup_test.db"
            con = sqlite3.connect(str(db))
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS teste (id INTEGER PRIMARY KEY, texto TEXT)")
            cur.execute("DELETE FROM teste")
            cur.execute("INSERT INTO teste(texto) VALUES (?)", ("OK",))
            con.commit()
            cur.execute("SELECT texto FROM teste LIMIT 1")
            result = cur.fetchone()[0]
            con.close()
            db.unlink(missing_ok=True)
            lines.append(f"ETAPA 4 SQLITE: OK ({result})")
        except Exception as exc:
            lines.append("ETAPA 4 SQLITE: FALHOU")
            lines.append(safe_text(exc))
        write_log(self.internal, lines)
        Clock.schedule_once(lambda _dt: self._startup_stage_3(lines), 0.50)

    def _startup_stage_3(self, lines):
        self._set(
            "ETAPA 1/5 - Kivy: OK\n"
            "ETAPA 2/5 - armazenamento interno: OK\n"
            f"ETAPA 3/5 - armazenamento externo: {'OK' if self.external else 'NEGADO/INDISPONIVEL'}\n"
            "ETAPA 4/5 - SQLite: OK\n\n"
            "ETAPA 5/5 - importando o sistema GNV..."
        )
        Clock.schedule_once(lambda _dt: self._import_system(lines), 0.50)

    def _import_system(self, lines):
        try:
            # O import pesado ocorre somente depois da GUI Python estar visivel.
            import importlib
            self.app_module = importlib.import_module(APP_MODULE_NAME)
            self.MobileGNVApp = self.app_module.MobileGNVApp
            lines.append("ETAPA 5 IMPORT GNV: OK")
            write_log(self.internal, lines)
            self._set("\n".join(lines) + "\n\nIMPORTAÇÃO DO SISTEMA CONCLUÍDA.\nPressione o botão para abrir a aplicação completa.")
            self.btn.disabled = False
        except BaseException as exc:
            lines.append("ETAPA 5 IMPORT GNV: FALHOU")
            lines.append(safe_text(exc))
            write_log(self.internal, lines)
            self._set("\n".join(lines) + "\n\nO aplicativo foi mantido aberto. O erro acima é o ponto real da falha.")

    def _load_real_app(self, *_args):
        try:
            real_cls = self.MobileGNVApp
            self.__class__ = type("AndroidGNVApp", (real_cls,), {})
            banco_cls = self.app_module.BancoGNV
            original_conectar = banco_cls.conectar

            def conectar_temporario(banco):
                banco.conexao = sqlite3.connect(":memory:")
                banco.cursor = banco.conexao.cursor()

            banco_cls.conectar = conectar_temporario
            try:
                new_root = real_cls.build(self)
            finally:
                banco_cls.conectar = original_conectar

            self.root.clear_widgets()
            self.root.add_widget(new_root)
            Clock.schedule_once(self._open_real_database, 0.5)
        except BaseException as exc:
            text = "ERRO AO ABRIR O SISTEMA GNV\n\n" + safe_text(exc)
            write_log(self.internal, self._log_lines + [text])
            self.root.clear_widgets()
            self.root.add_widget(Label(text=text))

    def _open_real_database(self, _dt):
        try:
            base = self.internal
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
        except BaseException as exc:
            text = "ERRO AO ABRIR BANCO SQLITE REAL\n\n" + safe_text(exc)
            write_log(self.internal, self._log_lines + [text])


if __name__ == "__main__":
    AndroidBootstrapApp().run()
