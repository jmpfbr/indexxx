import os
import time
import tkinter as tk
from tkinter import ttk, messagebox

from motor_busca import MotorBusca, formatar_tempo
from autocomplete import carregar_trie

BG = "#f4f4f5"
SIDEBAR = "#111111"
SIDEBAR_HOVER = "#262626"
SIDEBAR_SEL = "#f97316"
CARD = "#ffffff"
BORDA = "#e4e4e7"
ACCENT = "#f97316"
ACCENT_HOT = "#ea580c"
TEXTO = "#18181b"
MUTED = "#71717a"
CAMPO = "#fafafa"
SEL_LINHA = "#ffedd5"


class App(tk.Tk):
    def __init__(self, pasta, stopwords):
        super().__init__()
        self.title("Mini Mecanismo de Busca - Trie + Índice Invertido + Hash")
        self.geometry("1040x720")
        self.minsize(900, 600)
        self.configure(bg=BG)

        self.motor = MotorBusca(pasta, stopwords)
        self.trie_auto = carregar_trie()
        self.historico = []
        self.nav_botoes = {}
        self.paginas = {}
        self.pagina_atual = "palavra"

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self._estilo()
        self._topbar()
        self._sidebar()
        self._conteudo()
        self._barra_status()

        self.mostrar("palavra")
        self.recarregar()

    def _estilo(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("Modern.Treeview", background=CARD, fieldbackground=CARD, foreground=TEXTO,
                    rowheight=30, borderwidth=0, font=("Segoe UI", 10))
        s.configure("Modern.Treeview.Heading", background="#f1f5f9", foreground="#334155",
                    font=("Segoe UI", 10, "bold"), relief="flat", padding=(10, 9))
        s.map("Modern.Treeview", background=[("selected", SEL_LINHA)], foreground=[("selected", "#1e293b")])
        s.map("Modern.Treeview.Heading", background=[("active", "#e2e8f0")])
        s.configure("Modern.Vertical.TScrollbar", background="#cbd5e1", troughcolor=CARD,
                    bordercolor=CARD, arrowcolor="#64748b", relief="flat")

    def _topbar(self):
        bar = tk.Frame(self, bg=SIDEBAR, height=66)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)
        tk.Label(bar, text="Mini Mecanismo de Busca", bg=SIDEBAR, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=22)
        tk.Label(bar, text="Trie · Índice Invertido · Hash · KMP", bg=SIDEBAR, fg="#94a3b8",
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))

    def _sidebar(self):
        lateral = tk.Frame(self, bg=SIDEBAR, width=218)
        lateral.grid(row=1, column=0, sticky="ns")
        lateral.grid_propagate(False)
        tk.Label(lateral, text="NAVEGAÇÃO", bg=SIDEBAR, fg="#64748b",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22, pady=(20, 8))
        itens = [
            ("palavra", "Palavra"),
            ("prefixo", "Prefixo"),
            ("kmp", "KMP"),
            ("docs", "Documentos"),
            ("stats", "Estatísticas"),
            ("auto", "Autocomplete"),
            ("sobre", "Sobre"),
        ]
        for nome, rotulo in itens:
            self._nav(lateral, nome, rotulo)

    def _nav(self, parent, nome, rotulo):
        b = tk.Button(parent, text=rotulo, anchor="w", font=("Segoe UI", 11),
                      bg=SIDEBAR, fg="#cbd5e1", activebackground=SIDEBAR_SEL, activeforeground="white",
                      relief="flat", bd=0, padx=20, pady=11, cursor="hand2",
                      command=lambda: self.mostrar(nome))
        b.pack(fill="x", padx=10, pady=2)
        b.bind("<Enter>", lambda e: b.config(bg=SIDEBAR_HOVER) if self.pagina_atual != nome else None)
        b.bind("<Leave>", lambda e: b.config(bg=SIDEBAR if self.pagina_atual != nome else SIDEBAR_SEL))
        self.nav_botoes[nome] = b

    def mostrar(self, nome):
        self.pagina_atual = nome
        self.paginas[nome].tkraise()
        for n, b in self.nav_botoes.items():
            if n == nome:
                b.config(bg=SIDEBAR_SEL, fg="white")
            else:
                b.config(bg=SIDEBAR, fg="#cbd5e1")

    def _conteudo(self):
        area = tk.Frame(self, bg=BG)
        area.grid(row=1, column=1, sticky="nsew")
        self.lbl_resumo = tk.Label(area, bg=BG, fg=MUTED, font=("Segoe UI", 9), anchor="w")
        self.lbl_resumo.pack(fill="x", padx=24, pady=(14, 0))
        self.container = tk.Frame(area, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self._pagina_busca(
            "palavra", "Buscar palavra",
            "Consulta exata no índice invertido (tabela Hash) — custo médio O(1).",
            self.buscar_palavra, ("Arquivo",), (720,), "e_palavra", "lbl_res_palavra", "tv_palavra")
        self._pagina_busca(
            "prefixo", "Buscar por prefixo",
            "A Trie recupera as palavras do vocabulário; o índice invertido informa os documentos de cada uma.",
            self.buscar_prefixo, ("Palavra", "Documentos"), (230, 600),
            "e_prefixo", "lbl_res_prefixo", "tv_prefixo")
        self._pagina_busca(
            "kmp", "Buscar sequência (KMP)",
            "Bônus: algoritmo KMP no texto original, O(n + m). Encontra trechos que atravessam várias palavras.",
            self.buscar_sequencia, ("Documento", "Ocorrências", "Trecho (1ª ocorrência)"), (200, 100, 520),
            "e_kmp", "lbl_res_kmp", "tv_kmp")
        self._pagina_docs()
        self._pagina_stats()
        self._pagina_autocomplete()
        self._pagina_sobre()

    def _card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightbackground=BORDA, highlightthickness=1, bd=0)

    def _entry(self, parent, big=False):
        return tk.Entry(parent, font=("Segoe UI", 12 if big else 11), bg=CAMPO, fg=TEXTO,
                        relief="flat", highlightthickness=1, highlightbackground=BORDA,
                        highlightcolor=ACCENT, insertbackground=TEXTO)

    def _botao(self, parent, texto, comando, primary=False):
        if primary:
            bg, fg, hot = ACCENT, "white", ACCENT_HOT
        else:
            bg, fg, hot = "#f1f5f9", ACCENT, SEL_LINHA
        b = tk.Button(parent, text=texto, command=comando, font=("Segoe UI", 10, "bold"),
                      bg=bg, fg=fg, activebackground=hot, activeforeground=fg,
                      relief="flat", bd=0, padx=20, pady=9, cursor="hand2")
        b.bind("<Enter>", lambda e: b.config(bg=hot))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _pagina(self):
        pg = tk.Frame(self.container, bg=BG)
        pg.grid(row=0, column=0, sticky="nsew")
        return pg

    def _tabela(self, parent, colunas, larguras):
        card = self._card(parent)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        tv = ttk.Treeview(card, columns=colunas, show="headings", style="Modern.Treeview")
        for c, w in zip(colunas, larguras):
            tv.heading(c, text=c)
            tv.column(c, width=w, anchor="w")
        sb = ttk.Scrollbar(card, orient="vertical", command=tv.yview, style="Modern.Vertical.TScrollbar")
        tv.configure(yscrollcommand=sb.set)
        tv.tag_configure("par", background=CARD)
        tv.tag_configure("impar", background=CAMPO)
        tv.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        sb.pack(side="right", fill="y", pady=6, padx=(0, 6))
        return tv

    def _listrar(self, tv):
        for i, item in enumerate(tv.get_children()):
            tv.item(item, tags=("impar",) if i % 2 else ("par",))

    def _pagina_busca(self, nome, titulo, dica, comando, colunas, larguras, ae, al, atv):
        pg = self._pagina()
        card = self._card(pg)
        card.pack(fill="x", padx=24, pady=(16, 10))
        tk.Label(card, text=titulo, bg=CARD, fg=TEXTO,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=(14, 2))
        tk.Label(card, text=dica, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=18)
        linha = tk.Frame(card, bg=CARD)
        linha.pack(fill="x", padx=18, pady=16)
        entrada = self._entry(linha)
        entrada.pack(side="left", fill="x", expand=True, ipady=7)
        entrada.bind("<Return>", lambda e: comando())
        self._botao(linha, "Buscar", comando, primary=True).pack(side="left", padx=(10, 0))
        lbl = tk.Label(pg, text="", bg=BG, fg=TEXTO, font=("Segoe UI", 11, "bold"))
        lbl.pack(anchor="w", padx=26, pady=(0, 8))
        tv = self._tabela(pg, colunas, larguras)
        setattr(self, ae, entrada)
        setattr(self, al, lbl)
        setattr(self, atv, tv)
        self.paginas[nome] = pg

    def _pagina_docs(self):
        pg = self._pagina()
        card = self._card(pg)
        card.pack(fill="x", padx=24, pady=(16, 10))
        tk.Label(card, text="Documentos processados", bg=CARD, fg=TEXTO,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=14)
        self.tv_docs = self._tabela(pg, ("Arquivo", "Palavras (tokens)", "Termos distintos", "Caracteres"),
                                    (320, 160, 160, 130))
        self.paginas["docs"] = pg

    def _pagina_stats(self):
        pg = self._pagina()
        card = self._card(pg)
        card.pack(fill="x", padx=24, pady=(16, 10))
        tk.Label(card, text="Estatísticas", bg=CARD, fg=TEXTO,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=14)
        self.tv_stats = self._tabela(pg, ("Métrica", "Valor"), (430, 320))
        tk.Label(pg, text="Histórico de consultas (tempo de cada uma)", bg=BG, fg=TEXTO,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=26, pady=(0, 6))
        card2 = self._card(pg)
        card2.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self.lb_hist = tk.Listbox(card2, height=6, font=("Consolas", 10), bg=CARD, fg=TEXTO,
                                  relief="flat", bd=0, highlightthickness=0,
                                  selectbackground=SEL_LINHA, selectforeground="#1e293b")
        self.lb_hist.pack(fill="both", expand=True, padx=8, pady=8)
        self.paginas["stats"] = pg

    def _pagina_autocomplete(self):
        pg = self._pagina()
        card = self._card(pg)
        card.pack(fill="x", padx=24, pady=(16, 10))
        tk.Label(card, text="Autocomplete (Parte I — Trie própria)", bg=CARD, fg=TEXTO,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=(14, 2))
        tk.Label(card, text="As sugestões aparecem enquanto você digita. Duplo clique para escolher.",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=18)
        linha = tk.Frame(card, bg=CARD)
        linha.pack(fill="x", padx=18, pady=16)
        self.e_auto = self._entry(linha, big=True)
        self.e_auto.pack(side="left", fill="x", expand=True, ipady=8)
        self.e_auto.bind("<KeyRelease>", lambda e: self.atualizar_sugestoes())
        self._botao(linha, "Existe?", self.auto_buscar).pack(side="left", padx=(10, 0))
        self._botao(linha, "Inserir palavra", self.auto_inserir, primary=True).pack(side="left", padx=(8, 0))
        self.lbl_auto = tk.Label(pg, text="", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.lbl_auto.pack(anchor="w", padx=26, pady=(0, 6))
        card2 = self._card(pg)
        card2.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self.lb_auto = tk.Listbox(card2, font=("Segoe UI", 11), bg=CARD, fg=TEXTO, relief="flat", bd=0,
                                  highlightthickness=0, selectbackground=SEL_LINHA,
                                  selectforeground="#1e293b", activestyle="none")
        sb = ttk.Scrollbar(card2, orient="vertical", command=self.lb_auto.yview,
                           style="Modern.Vertical.TScrollbar")
        self.lb_auto.configure(yscrollcommand=sb.set)
        self.lb_auto.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 8))
        self.lb_auto.bind("<Double-Button-1>", self._escolher_sugestao)
        self.atualizar_sugestoes()
        self.paginas["auto"] = pg

    def _pagina_sobre(self):
        pg = self._pagina()
        card = self._card(pg)
        card.pack(fill="x", padx=24, pady=(16, 10))
        tk.Label(card, text="Sobre", bg=CARD, fg=TEXTO,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18, pady=(14, 2))
        tk.Label(card, text="Equipe que desenvolveu o projeto.", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(0, 14))

        equipe = [
            ("João Marcos Fierro", "JF"),
            ("Geovanna Melo", "GM"),
            ("Danielle Carvalho", "DC"),
        ]
        linha = tk.Frame(pg, bg=BG)
        linha.pack(fill="x", padx=24, pady=(0, 20))
        for i, (nome, iniciais) in enumerate(equipe):
            self._membro(linha, nome, iniciais).pack(
                side="left", fill="x", expand=True, padx=(0 if i == 0 else 12, 0))
        self.paginas["sobre"] = pg

    def _membro(self, parent, nome, iniciais):
        card = self._card(parent)
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="x", padx=14, pady=14)
        d = 46
        av = tk.Canvas(inner, width=d, height=d, bg=CARD, highlightthickness=0, bd=0)
        av.create_oval(2, 2, d - 2, d - 2, fill=ACCENT, outline="")
        av.create_text(d / 2, d / 2, text=iniciais, fill="white",
                       font=("Segoe UI", 12, "bold"))
        av.pack(side="left")
        tk.Label(inner, text=nome, bg=CARD, fg=TEXTO, font=("Segoe UI", 10, "bold"),
                 anchor="w", justify="left", wraplength=120).pack(
            side="left", fill="x", expand=True, padx=(12, 0))
        return card

    def _barra_status(self):
        self.status = tk.StringVar(value="Pronto.")
        rodape = tk.Frame(self, bg=BORDA, height=1)
        rodape.grid(row=2, column=0, columnspan=2, sticky="ew")
        tk.Label(self, textvariable=self.status, bg=CARD, fg=MUTED, anchor="w",
                 font=("Segoe UI", 9), padx=14, pady=6).grid(row=3, column=0, columnspan=2, sticky="ew")

    def _registrar(self, rotulo, dt):
        texto = f"{time.strftime('%H:%M:%S')}  {rotulo:<38} {formatar_tempo(dt)}"
        self.historico.append(texto)
        self.lb_hist.insert(0, texto)
        self.status.set(f"Última consulta: {rotulo} — {formatar_tempo(dt)}")

    def recarregar(self):
        if not os.path.isdir(self.motor.pasta_docs):
            messagebox.showwarning("Pasta não encontrada", f"A pasta '{self.motor.pasta_docs}' não existe.")
        self.motor.construir()
        e = self.motor.estatisticas()
        self.lbl_resumo.config(text=f"Pasta: {self.motor.pasta_docs}")
        for tv in (self.tv_docs, self.tv_stats):
            tv.delete(*tv.get_children())
        for nome, i in self.motor.info_docs.items():
            self.tv_docs.insert("", "end", values=(nome, i["palavras"], i["distintas"], i["caracteres"]))
        for k, v in e.items():
            self.tv_stats.insert("", "end", values=(k, v))
        self._listrar(self.tv_docs)
        self._listrar(self.tv_stats)
        self.status.set(f"{e['Documentos processados']} documento(s) processado(s).")

    def buscar_palavra(self):
        termo = self.e_palavra.get().strip()
        if not termo:
            return
        docs, dt = self.motor.buscar_palavra(termo)
        self.tv_palavra.delete(*self.tv_palavra.get_children())
        if docs:
            self.lbl_res_palavra.config(text=f"'{termo.lower()}' encontrada em {len(docs)} arquivo(s):")
            for d in docs:
                self.tv_palavra.insert("", "end", values=(d,))
        else:
            self.lbl_res_palavra.config(text=f"'{termo.lower()}' não foi encontrada.")
            sug, _ = self.motor.buscar_prefixo(termo.lower()[:4], limite=8)
            for p, _d in sug:
                self.tv_palavra.insert("", "end", values=(f"Você quis dizer: {p}?",))
        self._listrar(self.tv_palavra)
        self._registrar(f"palavra '{termo}'", dt)

    def buscar_prefixo(self):
        termo = self.e_prefixo.get().strip()
        if not termo:
            return
        res, dt = self.motor.buscar_prefixo(termo)
        self.tv_prefixo.delete(*self.tv_prefixo.get_children())
        for palavra, docs in res:
            self.tv_prefixo.insert("", "end", values=(palavra, ", ".join(docs)))
        self.lbl_res_prefixo.config(
            text=f"{len(res)} palavra(s) começam com '{termo.lower()}'" if res
            else f"Nenhuma palavra começa com '{termo.lower()}'.")
        self._listrar(self.tv_prefixo)
        self._registrar(f"prefixo '{termo}'", dt)

    def buscar_sequencia(self):
        termo = self.e_kmp.get()
        if not termo.strip():
            return
        res, dt = self.motor.buscar_sequencia(termo)
        self.tv_kmp.delete(*self.tv_kmp.get_children())
        for nome, qtd, trecho in res:
            self.tv_kmp.insert("", "end", values=(nome, qtd, "..." + trecho + "..."))
        self.lbl_res_kmp.config(
            text=f"Sequência encontrada em {len(res)} arquivo(s)." if res else "Sequência não encontrada.")
        self._listrar(self.tv_kmp)
        self._registrar(f"sequência '{termo}'", dt)

    def atualizar_sugestoes(self):
        prefixo = self.e_auto.get().strip().lower()
        t0 = time.perf_counter()
        palavras = self.trie_auto.buscar_prefixo(prefixo, limite=200)
        dt = time.perf_counter() - t0
        self.lb_auto.delete(0, "end")
        for p in palavras:
            self.lb_auto.insert("end", p)
        self.lbl_auto.config(
            text=f"Palavras cadastradas: {len(self.trie_auto)}   |   "
                 f"{len(palavras)} sugestão(ões) em {formatar_tempo(dt)}   |   duplo clique para escolher")

    def _escolher_sugestao(self, _e):
        sel = self.lb_auto.curselection()
        if sel:
            self.e_auto.delete(0, "end")
            self.e_auto.insert(0, self.lb_auto.get(sel[0]))
            self.atualizar_sugestoes()

    def auto_buscar(self):
        p = self.e_auto.get().strip().lower()
        if p:
            achou = self.trie_auto.buscar(p)
            messagebox.showinfo("Busca exata", f"'{p}' {'EXISTE' if achou else 'NÃO existe'} na Trie.")

    def auto_inserir(self):
        p = self.e_auto.get().strip().lower()
        if not p:
            return
        if self.trie_auto.inserir(p):
            self.status.set(f"'{p}' inserida na Trie.")
        else:
            messagebox.showinfo("Inserir", f"'{p}' já estava cadastrada.")
        self.atualizar_sugestoes()


def executar(pasta="documentos", stopwords="stopwords.txt"):
    App(pasta, stopwords).mainloop()


if __name__ == "__main__":
    executar()
