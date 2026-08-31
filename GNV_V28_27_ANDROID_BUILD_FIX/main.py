# V28.37 - Android: inicializacao segura, UI primeiro e abas sob demanda
#
# Objetivo desta versao:
# 1) Mostrar a interface imediatamente.
# 2) Nao construir as 12 abas durante o primeiro frame.
# 3) Usar SQLite em memoria durante a subida da interface.
# 4) Abrir o SQLite persistente somente depois que a UI estiver visivel.
# 5) Carregar cada aba somente quando o usuario a selecionar.
# 6) Registrar etapas de inicializacao em startup_android.log.
#
# O codigo do sistema original continua em
# GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z.py.

import os
import sqlite3
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


IMPORT_ERROR = None
APP_MODULE = None
MobileGNVApp = None


def _safe_storage(app=None):
    """Retorna um diretorio privado e gravavel do aplicativo."""
    try:
        if app is not None and getattr(app, "user_data_dir", None):
            base = Path(app.user_data_dir)
        else:
            base = Path.cwd() / "data"
        base.mkdir(parents=True, exist_ok=True)
        return base
    except Exception:
        return Path.cwd()


class AndroidLauncher(App):
    """Bootstrap Android: interface primeiro, sistema depois."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = None
        self.details = None
        self.log_path = None
        self._base = None
        self._real_db_ready = False
        self._built_tabs = set()

    def _log(self, message):
        """Atualiza a tela e grava o mesmo passo em log persistente."""
        text = str(message)
        print(text, flush=True)
        try:
            if self.status is not None:
                self.status.text = text
            if self.log_path is not None:
                with self.log_path.open("a", encoding="utf-8") as fh:
                    fh.write(text + "\n")
        except Exception:
            pass

    def _error(self, etapa, exc):
        """Mantem o APK aberto ao ocorrer uma excecao Python."""
        bloco = (
            f"\nERRO NA ETAPA: {etapa}\n"
            f"TIPO: {type(exc).__name__}\n"
            f"MENSAGEM: {exc}\n\n"
            f"{traceback.format_exc()}"
        )
        self._log(bloco)
        try:
            if self.details is not None:
                self.details.text = bloco
        except Exception:
            pass

    def build(self):
        self.title = "Sistema de Cálculos e Análise da Capacidade do Cilindro de GNV"

        # A primeira coisa que o usuario recebe e uma tela Kivy real.
        root = BoxLayout(orientation="vertical", padding=20, spacing=14)
        title = Label(
            text="SISTEMA DE CÁLCULOS DE GNV",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height="60dp",
        )
        self.status = Label(
            text="Loading...",
            font_size="18sp",
            size_hint_y=None,
            height="50dp",
        )
        self.details = Label(
            text="Iniciando o sistema...",
            font_size="13sp",
            halign="left",
            valign="top",
        )
        self.details.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        root.add_widget(title)
        root.add_widget(self.status)
        root.add_widget(self.details)

        self._base = _safe_storage(self)
        self.log_path = self._base / "startup_android.log"
        try:
            self.log_path.write_text("V28.37\n", encoding="utf-8")
        except Exception:
            pass

        # So agora, com a UI entregue ao Kivy, comecamos a inicializacao.
        Clock.schedule_once(self._initialize_after_ui, 0.20)
        return root

    def _initialize_after_ui(self, _dt):
        try:
            self._log("ETAPA 1/8 - Interface Kivy carregada")

            # Importar o modulo original somente depois da UI estar visivel.
            self._log("ETAPA 2/8 - Carregando modulo principal")
            global APP_MODULE, MobileGNVApp
            try:
                import GNV14_REPARADO_V28_27_CORRIGIDO_CARD_FISICO_ANP_Z as APP_MODULE
                MobileGNVApp = APP_MODULE.MobileGNVApp
            except BaseException as exc:
                global IMPORT_ERROR
                IMPORT_ERROR = exc
                raise

            self._log("ETAPA 3/8 - Modulo principal carregado")

            # Banco temporario em memoria para permitir que a UI seja montada
            # sem depender de qualquer arquivo externo.
            self._log("ETAPA 4/8 - Inicializando SQLite temporario")
            self.banco = APP_MODULE.BancoGNV(":memory:")
            self.banco.conectar()
            self.banco.criar_tabela()
            self.banco.criar_indices()
            self._real_db_ready = False

            self._log("ETAPA 5/8 - Construindo somente a aba Cálculos")
            self._create_shell_for_gnv()
            self._ensure_tab(0)

            self._log("ETAPA 6/8 - Interface principal visível")
            Clock.schedule_once(self._initialize_real_database, 0.50)
            Clock.schedule_once(self._apply_first_visuals, 0.60)

        except BaseException as exc:
            self._error("inicializacao", exc)

    def _create_shell_for_gnv(self):
        """Replica somente a infraestrutura leve do build original."""
        base_class = APP_MODULE.MobileGNVApp
        # Inicializa apenas atributos necessários às telas existentes.
        self.idioma = "pt-BR"
        self.base_dir = self._base
        self.db_path = str(self._base / "gnv_dados.db")
        self.config_path = self._base / "configuracoes.json"
        self.formula_pt = base_class._load_formula_pt(self)
        self.colors = base_class._default_colors(self)
        self._colors_personalizadas = False
        self._visual_ready = False

        self.sm = APP_MODULE.ScreenManager()
        self.screen_names = []
        keys = APP_MODULE.MOBILE_TABS.get(self.idioma, APP_MODULE.MOBILE_TABS["pt-BR"])
        for i, key in enumerate(keys):
            name = f"screen_{i}"
            self.screen_names.append(name)
            self.sm.add_widget(APP_MODULE.MobileScreen(key, name=name))

        root = BoxLayout(orientation="vertical", spacing=APP_MODULE.dp(4), padding=APP_MODULE.dp(5))
        self.header = Label(
            text=APP_MODULE.APP_TITLE,
            size_hint_y=None,
            height=APP_MODULE.dp(42),
            font_size=APP_MODULE.sp(15),
            bold=True,
        )
        root.add_widget(self.header)

        nav = BoxLayout(size_hint_y=None, height=APP_MODULE.dp(46), spacing=APP_MODULE.dp(4))
        self.tab_spinner = APP_MODULE.Spinner(
            text="Cálculos",
            values=tuple(self.screen_names_for_language()),
            size_hint_x=0.78,
        )
        self.tab_spinner.bind(text=self._go_from_spinner)
        nav.add_widget(self.tab_spinner)
        self.lang_spinner = APP_MODULE.Spinner(
            text="pt-BR",
            values=APP_MODULE.IDIOMAS_DISPONIVEIS,
            size_hint_x=0.22,
        )
        self.lang_spinner.bind(text=self.change_language)
        nav.add_widget(self.lang_spinner)
        root.add_widget(nav)
        root.add_widget(self.sm)

        self.footer = Label(
            text="Analista de Sistemas e Pesquisador - Christiano T.Gaio - Desenvolvedor | Projeto iniciado o Desenvolvimento em 06/2026",
            size_hint_y=None,
            height=APP_MODULE.dp(34),
            font_size=APP_MODULE.sp(9),
            halign="center",
            valign="middle",
        )
        self.footer.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        root.add_widget(self.footer)

        self.root = root

    def screen_names_for_language(self):
        return APP_MODULE.MOBILE_TABS.get(self.idioma, APP_MODULE.MOBILE_TABS["pt-BR"])

    def _ensure_tab(self, idx):
        """Constroi uma aba somente na primeira vez que for acessada."""
        if idx in self._built_tabs:
            return True
        methods = (
            "_build_calculos",
            "_build_abastecimentos",
            "_build_anp",
            "_build_compressao",
            "_build_historico",
            "_build_sqlite",
            "_build_excel",
            "_build_graficos",
            "_build_config",
            "_build_formulas",
            "_build_total",
            "_build_creditos",
        )
        if idx < 0 or idx >= len(methods):
            raise IndexError(f"Aba inválida: {idx}")
        self._log(f"ABRINDO ABA {idx + 1}/12 - {self.screen_names_for_language()[idx]}")
        getattr(self, methods[idx])()
        self._built_tabs.add(idx)
        try:
            self._apply_result_styles_to_all_tabs()
        except Exception:
            pass
        return True

    def _go_from_spinner(self, _spinner, text):
        try:
            names = self.screen_names_for_language()
            idx = names.index(text)
            self._ensure_tab(idx)
            self.sm.current = self.screen_names[idx]
            try:
                self._apply_language()
            except Exception:
                pass
        except BaseException as exc:
            self._error(f"abrir aba {text}", exc)

    def change_language(self, _spinner, idioma):
        try:
            self.idioma = idioma
            current = self.sm.current
            self.tab_spinner.values = tuple(self.screen_names_for_language())
            idx = self.screen_names.index(current)
            self._ensure_tab(idx)
            self.tab_spinner.text = self.screen_names_for_language()[idx]
            self._apply_language()
            Clock.schedule_once(lambda _dt: self._apply_colors(), 0)
            try:
                self._save_config()
            except Exception:
                pass
        except BaseException as exc:
            self._error("troca de idioma", exc)

    def _apply_first_visuals(self, _dt):
        try:
            self._apply_language()
            self._mark_visual_ready()
            self._log("ETAPA 7/8 - Visual aplicado")
        except BaseException as exc:
            self._error("aplicacao visual", exc)

    def _initialize_real_database(self, _dt):
        try:
            self._log("ETAPA 8/8 - Abrindo SQLite persistente")
            real_path = Path(self.db_path)
            real_path.parent.mkdir(parents=True, exist_ok=True)

            test_file = real_path.parent / ".storage_test"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)

            real_db = APP_MODULE.BancoGNV(str(real_path))
            real_db.conectar()
            real_db.criar_tabela()
            real_db.criar_indices()

            old = getattr(self, "banco", None)
            self.banco = real_db
            self._real_db_ready = True
            if old is not None:
                try:
                    old.conexao.close()
                except Exception:
                    pass

            # Atualiza somente as abas que ja foram criadas.
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

            self._log("SISTEMA PRONTO - SQLite persistente ativo")
            if self.details is not None:
                self.details.text = "Sistema pronto. A aba Cálculos foi carregada. As demais abas serão carregadas quando selecionadas."
        except BaseException as exc:
            # SQLite/storage nao pode encerrar o aplicativo.
            self._error("SQLite persistente", exc)
            if self.details is not None:
                self.details.text = "A interface continua funcionando, mas o banco persistente apresentou erro. Veja startup_android.log."

    # Encaminhamento dos metodos de instancia para o modulo original.
    def __getattr__(self, name):
        # Evita duplicar centenas de metodos do sistema original.
        if APP_MODULE is not None:
            cls = getattr(APP_MODULE, "MobileGNVApp", None)
            if cls is not None and hasattr(cls, name):
                return getattr(cls, name).__get__(self, type(self))
        raise AttributeError(name)


if __name__ == "__main__":
    AndroidLauncher().run()
