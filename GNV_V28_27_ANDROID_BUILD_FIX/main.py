# V28.36 - Android: GUI primeiro, diagnóstico por etapas e PDF sob demanda
#
# OBJETIVO:
# 1) A primeira coisa visível no celular é a interface "Loading...".
# 2) O programa principal só é importado DEPOIS que o Kivy já colocou essa tela.
# 3) O SQLite real só é aberto DEPOIS da interface principal estar visível.
# 4) Arquivos usam o armazenamento privado do aplicativo; não dependem de /sdcard.
# 5) Falhas de importação, armazenamento ou SQLite ficam visíveis na tela e
#    também são gravadas em startup_error.log.
# 6) fpdf2 NÃO é importado durante o startup. Um proxy carrega fpdf2 somente
#    quando o código realmente instancia FPDF para gerar um relatório PDF.
#
# Esta versão substitui o comportamento "abre e fecha" por um diagnóstico
# persistente. Se alguma etapa falhar, o APK permanece aberto mostrando o erro.

import os
import sys
import sqlite3
import traceback
import types
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout


APP_NAME = "Sistema GNV"
_STORAGE = None
_STORAGE_ERROR = None


# ---------------------------------------------------------------------------
# 1. Armazenamento privado Android
# ---------------------------------------------------------------------------
try:
    from android.storage import app_storage_path

    _STORAGE = Path(app_storage_path())
    _STORAGE.mkdir(parents=True, exist_ok=True)
    os.chdir(_STORAGE)
    os.environ["HOME"] = str(_STORAGE)
    os.environ["XDG_CONFIG_HOME"] = str(_STORAGE / ".config")
    os.environ["XDG_DATA_HOME"] = str(_STORAGE / ".local" / "share")
    Path(os.environ["XDG_CONFIG_HOME"]).mkdir(parents=True, exist_ok=True)
    Path(os.environ["XDG_DATA_HOME"]).mkdir(parents=True, exist_ok=True)
except BaseException as exc:
    _STORAGE_ERROR = exc


# ---------------------------------------------------------------------------
# 2. fpdf2 sob demanda
#
# O programa legado contém "from fpdf import FPDF" no topo. Para impedir que
# uma falha do fpdf2 mate o aplicativo durante o startup, instalamos aqui um
# módulo proxy. A biblioteca real só será importada quando FPDF(...) for
# executado, isto é, quando o usuário realmente gerar um PDF.
# ---------------------------------------------------------------------------
class _LazyFPDF:
    def __new__(cls, *args, **kwargs):
        proxy = sys.modules.pop("fpdf", None)
        try:
            from fpdf import FPDF as RealFPDF
            return RealFPDF(*args, **kwargs)
        finally:
            # Se o import real não deixou o pacote carregado, restaura o proxy
            # para que o erro seja apresentado pelo diagnóstico em vez de sumir.
            if "fpdf" not in sys.modules and proxy is not None:
                sys.modules["fpdf"] = proxy


_lazy_fpdf_module = types.ModuleType("fpdf")
_lazy_fpdf_module.FPDF = _LazyFPDF
_lazy_fpdf_module.__doc__ = "Lazy fpdf2 proxy used by the Android bootstrap."
sys.modules["fpdf"] = _lazy_fpdf_module


# ---------------------------------------------------------------------------
# 3. Tela inicial. Esta tela precisa aparecer ANTES do import do sistema GNV.
# ---------------------------------------------------------------------------
class AndroidBootstrap(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_label = None
        self.detail_label = None
        self.real_app = None
        self.original_conectar = None
        self.app_module = None

    def _set_status(self, text, detail=""):
        if self.status_label is not None:
            self.status_label.text = text
        if self.detail_label is not None:
            self.detail_label.text = detail

    def _write_log(self, text):
        try:
            base = _STORAGE or Path(self.user_data_dir)
            base.mkdir(parents=True, exist_ok=True)
            (base / "startup_error.log").write_text(text, encoding="utf-8")
        except BaseException:
            pass

    def _show_error(self, stage, exc):
        text = "\n".join([
            "ERRO DE INICIALIZAÇÃO DO SISTEMA GNV",
            "",
            f"ETAPA: {stage}",
            f"TIPO: {type(exc).__name__}",
            f"MENSAGEM: {exc}",
            "",
            "TRACEBACK:",
            traceback.format_exc(),
        ])
        if _STORAGE is not None:
            text += f"\n\nARMAZENAMENTO PRIVADO:\n{_STORAGE}"
        if _STORAGE_ERROR is not None:
            text += (
                "\n\nERRO AO PREPARAR ARMAZENAMENTO:\n"
                f"{type(_STORAGE_ERROR).__name__}: {_STORAGE_ERROR}"
            )
        self._write_log(text)
        self._set_status("ERRO - O aplicativo permaneceu aberto", text)

    def build(self):
        self.title = APP_NAME

        root = BoxLayout(
            orientation="vertical",
            padding=32,
            spacing=18,
        )

        root.add_widget(Label(
            text="SISTEMA DE CÁLCULOS DE GNV",
            font_size="24sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=70,
        ))

        self.status_label = Label(
            text="Loading...",
            font_size="28sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=70,
        )
        root.add_widget(self.status_label)

        self.detail_label = Label(
            text="Etapa 1/7 - Interface gráfica iniciada.\nAguarde...",
            font_size="16sp",
            halign="left",
            valign="top",
        )
        root.add_widget(self.detail_label)

        # O import pesado só acontece depois que esta tela já foi entregue ao
        # loop gráfico do Kivy.
        Clock.schedule_once(self._start_diagnostics, 0.20)
        return root

    def _start_diagnostics(self, _dt):
        try:
            self._set_status(
                "Loading...",
                "Etapa 2/7 - Testando armazenamento privado Android...",
            )
            if _STORAGE_ERROR is not None:
                raise RuntimeError(
                    f"Não foi possível preparar o armazenamento privado: {_STORAGE_ERROR}"
                )

            test_file = _STORAGE / ".gnv_storage_test"
            test_file.write_text("GNV Android OK", encoding="utf-8")
            if test_file.read_text(encoding="utf-8") != "GNV Android OK":
                raise IOError("Falha na leitura do arquivo de teste")
            test_file.unlink(missing_ok=True)

            self._set_status(
                "Loading...",
                "Etapa 3/7 - Armazenamento OK. Importando sistema GNV...",
            )
            Clock.schedule_once(self._import_main_program, 0.05)
        except BaseException as exc:
            self._show_error("2/7 - armazenamento privado", exc)

    def _import_main_program(self, _dt):
        try:
            # Importação tardia: o usuário já vê a GUI antes de qualquer
            # import pesado do programa principal, inclusive openpyxl/fpdf2.
            import importlib
            self.app_module = importlib.import_module(
                "GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z"
            )

            if not hasattr(self.app_module, "MobileGNVApp"):
                raise AttributeError("MobileGNVApp não foi encontrado no programa principal")

            self._set_status(
                "Loading...",
                "Etapa 4/7 - Programa principal carregado. Preparando SQLite em memória...",
            )
            Clock.schedule_once(self._build_main_interface, 0.05)
        except BaseException as exc:
            self._show_error("3/7 - importação do programa principal", exc)

    def _build_main_interface(self, _dt):
        banco_cls = None
        try:
            banco_cls = self.app_module.BancoGNV
            self.original_conectar = banco_cls.conectar

            def conectar_temporario(banco):
                banco.conexao = sqlite3.connect(":memory:")
                banco.cursor = banco.conexao.cursor()

            banco_cls.conectar = conectar_temporario

            self._set_status(
                "Loading...",
                "Etapa 5/7 - Construindo a interface gráfica (SQLite real ainda não foi aberto)...",
            )

            self.real_app = self.app_module.MobileGNVApp()
            root = self.real_app.build()

            # A interface principal agora substitui a tela de diagnóstico.
            self.root = root

            self._set_status(
                "Sistema carregado",
                "Etapa 6/7 - Interface gráfica pronta. Inicializando banco persistente...",
            )

            Clock.schedule_once(self._open_real_database, 0.20)
        except BaseException as exc:
            self._show_error("5/7 - construção da interface gráfica", exc)
        finally:
            if banco_cls is not None and self.original_conectar is not None:
                banco_cls.conectar = self.original_conectar

    def _open_real_database(self, _dt):
        try:
            app = self.real_app
            base = _STORAGE or Path(app.user_data_dir)
            base.mkdir(parents=True, exist_ok=True)

            self._set_status(
                "Sistema carregado",
                "Etapa 7/7 - Testando e abrindo banco SQLite persistente...",
            )

            db_path = base / "gnv_dados.db"
            config_path = base / "configuracoes.json"
            app.db_path = str(db_path)
            app.config_path = config_path
            app.base_dir = base

            if not hasattr(app, "banco"):
                raise AttributeError("A aplicação principal não criou o objeto BancoGNV")

            app.banco.nome_banco = str(db_path)
            if getattr(app.banco, "conexao", None) is not None:
                try:
                    app.banco.conexao.close()
                except BaseException:
                    pass

            app.banco.conectar()
            app.banco.criar_tabela()
            app.banco.criar_indices()

            # Atualizações opcionais das telas. Um erro visual em uma aba não
            # pode derrubar o aplicativo inteiro.
            for method_name in (
                "_refresh_history",
                "_refresh_sqlite",
                "_refresh_total",
                "_refresh_chart",
            ):
                method = getattr(app, method_name, None)
                if callable(method):
                    try:
                        method()
                    except BaseException:
                        pass

            self._set_status(
                "Sistema pronto",
                "Inicialização concluída. Banco SQLite em armazenamento privado do aplicativo.",
            )

        except BaseException as exc:
            self._show_error("7/7 - SQLite persistente", exc)


if __name__ == "__main__":
    AndroidBootstrap().run()
