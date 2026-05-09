import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from data_structures import NoteManager, seed
from themes import THEMES


class NoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.nm = NoteManager()
        self.current_theme = "light"
        self.T = THEMES[self.current_theme]
        self.selected_note = None
        self.view_mode = "chrono"
        self.active_tag_filter = None
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        self._edit_mode = False
        self._unsaved = False

        self.title("NoteApp")
        self.geometry("1200x720")
        self.minsize(900, 600)
        self.configure(bg=self.T["bg_primary"])

        self._load_fonts()
        self._build_ui()
        self._ask_seed()

    def _load_fonts(self):
        self.FONT_TITLE_BIG = ("Segoe UI", 18, "bold")
        self.FONT_TITLE = ("Segoe UI", 13, "bold")
        self.FONT_SUBTITLE = ("Segoe UI", 11, "bold")
        self.FONT_BODY = ("Segoe UI", 10)
        self.FONT_SMALL = ("Segoe UI", 9)
        self.FONT_TINY = ("Segoe UI", 8)
        self.FONT_MONO = ("Consolas", 11)
        self.FONT_SIDEBAR = ("Segoe UI", 10)
        self.FONT_SIDEBAR_LABEL = ("Segoe UI", 8, "bold")
        self.FONT_ICON = ("Segoe UI Emoji", 14)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_note_list()
        self._build_editor()

    def _build_sidebar(self):
        T = self.T
        self.sidebar = tk.Frame(self, bg=T["bg_sidebar"], width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(8, weight=1)

        header_frame = tk.Frame(self.sidebar, bg=T["bg_sidebar"], pady=16)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0)

        user_frame = tk.Frame(header_frame, bg=T["bg_sidebar"])
        user_frame.pack(fill="x", padx=14)

        avatar = tk.Label(user_frame, text="📝", font=("Segoe UI Emoji", 22),
                          bg="#2563EB", fg="white", width=2, height=1,
                          relief="flat")
        avatar.pack(side="left")

        name_frame = tk.Frame(user_frame, bg=T["bg_sidebar"])
        name_frame.pack(side="left", padx=8, fill="x", expand=True)
        tk.Label(name_frame, text="NoteApp", font=self.FONT_SUBTITLE,
                 bg=T["bg_sidebar"], fg="white").pack(anchor="w")
        tk.Label(name_frame, text="Struktur Data", font=self.FONT_TINY,
                 bg=T["bg_sidebar"], fg=T["fg_sidebar"]).pack(anchor="w")

        self._theme_btn = tk.Label(user_frame, text="🌙", font=self.FONT_ICON,
                                   bg=T["bg_sidebar"], fg=T["fg_sidebar"],
                                   cursor="hand2")
        self._theme_btn.pack(side="right")
        self._theme_btn.bind("<Button-1>", lambda e: self.toggle_theme())

        sep = tk.Frame(self.sidebar, bg="#2D5BA0", height=1)
        sep.grid(row=1, column=0, sticky="ew", padx=14, pady=4)

        self._sidebar_section("TAMPILAN", 2)

        self.view_btns = {}
        views = [("📅  Kronologis", "chrono"), ("🔤  Alfabetis", "alpha")]
        for i, (label, mode) in enumerate(views):
            btn = self._sidebar_btn(label, 3 + i, lambda m=mode: self._set_view(m))
            self.view_btns[mode] = btn

        self._sidebar_section("KATEGORI TAG", 5)

        tag_header = tk.Frame(self.sidebar, bg=T["bg_sidebar"])
        tag_header.grid(row=6, column=0, sticky="ew", padx=14, pady=2)

        self.tag_all_btn = self._sidebar_btn("🏷️  Semua Notes", 6, self._clear_tag_filter)

        self.tag_scroll_frame = tk.Frame(self.sidebar, bg=T["bg_sidebar"])
        self.tag_scroll_frame.grid(row=7, column=0, sticky="nsew", padx=0)

        self.tag_canvas = tk.Canvas(self.tag_scroll_frame, bg=T["bg_sidebar"],
                                    highlightthickness=0, height=160)
        tag_sb = tk.Scrollbar(self.tag_scroll_frame, orient="vertical",
                               command=self.tag_canvas.yview)
        self.tag_inner = tk.Frame(self.tag_canvas, bg=T["bg_sidebar"])
        self.tag_canvas.create_window((0, 0), window=self.tag_inner, anchor="nw")
        self.tag_canvas.configure(yscrollcommand=tag_sb.set)
        self.tag_canvas.pack(side="left", fill="both", expand=True)
        tag_sb.pack(side="right", fill="y")
        self.tag_inner.bind("<Configure>", lambda e: self.tag_canvas.configure(
            scrollregion=self.tag_canvas.bbox("all")))

        spacer = tk.Frame(self.sidebar, bg=T["bg_sidebar"])
        spacer.grid(row=8, column=0, sticky="nsew")

        sep2 = tk.Frame(self.sidebar, bg="#2D5BA0", height=1)
        sep2.grid(row=9, column=0, sticky="ew", padx=14, pady=4)

        bottom_btns = [
            ("🔄  Sync Log", self._show_sync_log),
            ("📊  Info Struktur", self._show_struct_info),
        ]
        for i, (label, cmd) in enumerate(bottom_btns):
            self._sidebar_btn(label, 10 + i, cmd)

        self.sidebar.grid_columnconfigure(0, weight=1)

    def _sidebar_section(self, text, row):
        T = self.T
        lbl = tk.Label(self.sidebar, text=text, font=self.FONT_SIDEBAR_LABEL,
                        bg=self.T["bg_sidebar"], fg=T["fg_sidebar_label"])
        lbl.grid(row=row, column=0, sticky="w", padx=14, pady=(10, 2))
        return lbl

    def _sidebar_btn(self, text, row, command):
        T = self.T
        btn = tk.Label(self.sidebar, text=text, font=self.FONT_SIDEBAR,
                        bg=T["bg_sidebar"], fg=T["fg_sidebar"],
                        anchor="w", padx=14, pady=7, cursor="hand2")
        btn.grid(row=row, column=0, sticky="ew")
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=T["bg_sidebar_hover"]))
        btn.bind("<Leave>", lambda e, b=btn: self._sidebar_btn_leave(b))
        btn.bind("<Button-1>", lambda e, c=command: c())
        return btn

    def _sidebar_btn_leave(self, btn):
        T = self.T
        active_view = self.view_mode if hasattr(self, "view_mode") else None
        for mode, b in (self.view_btns.items() if hasattr(self, "view_btns") else {}.items()):
            if b == btn:
                if mode == active_view:
                    btn.config(bg=T["bg_sidebar_active"])
                    return
        btn.config(bg=T["bg_sidebar"])

    def _build_note_list(self):
        T = self.T
        self.list_panel = tk.Frame(self, bg=T["bg_panel"], width=280,
                                    relief="flat", bd=0)
        self.list_panel.grid(row=0, column=1, sticky="nsew")
        self.list_panel.grid_propagate(False)
        self.list_panel.grid_rowconfigure(3, weight=1)
        self.list_panel.grid_columnconfigure(0, weight=1)

        list_header = tk.Frame(self.list_panel, bg=T["bg_panel"], pady=12)
        list_header.grid(row=0, column=0, sticky="ew", padx=14)

        self.list_title_lbl = tk.Label(list_header, text="📋  Semua Notes",
                                        font=self.FONT_TITLE,
                                        bg=T["bg_panel"], fg=T["fg_title"])
        self.list_title_lbl.pack(side="left")

        self.note_count_lbl = tk.Label(list_header, text="",
                                        font=self.FONT_SMALL,
                                        bg=T["bg_panel"], fg=T["fg_secondary"])
        self.note_count_lbl.pack(side="right", pady=2)

        search_frame = tk.Frame(self.list_panel, bg=T["bg_panel"])
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 4))

        search_wrap = tk.Frame(search_frame, bg=T["bg_input"],
                                highlightbackground=T["border"],
                                highlightthickness=1, bd=0)
        search_wrap.pack(fill="x")
        tk.Label(search_wrap, text="🔍", bg=T["bg_input"], fg=T["fg_secondary"],
                 font=("Segoe UI Emoji", 10), padx=6).pack(side="left")
        self.search_entry = tk.Entry(search_wrap, textvariable=self.search_var,
                                      bg=T["bg_input"], fg=T["fg_primary"],
                                      relief="flat", font=self.FONT_BODY,
                                      insertbackground=T["fg_primary"])
        self.search_entry.pack(side="left", fill="x", expand=True, pady=7)
        self.search_entry.insert(0, "Cari notes...")
        self.search_entry.bind("<FocusIn>", self._search_focus_in)
        self.search_entry.bind("<FocusOut>", self._search_focus_out)
        self._search_placeholder = True

        add_btn = tk.Button(self.list_panel, text="＋  Tambah Note",
                             bg=T["accent"], fg="white", relief="flat",
                             font=self.FONT_SUBTITLE, pady=8,
                             activebackground=T["accent_hover"],
                             activeforeground="white", cursor="hand2",
                             command=self._add_note)
        add_btn.grid(row=2, column=0, columnspan=2, padx=14, pady=(0, 8), sticky="ew")

        list_frame = tk.Frame(self.list_panel, bg=T["bg_panel"])
        list_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.list_canvas = tk.Canvas(list_frame, bg=T["bg_panel"],
                                      highlightthickness=0)
        self.list_scrollbar = tk.Scrollbar(list_frame, orient="vertical",
                                            command=self.list_canvas.yview)
        self.notes_container = tk.Frame(self.list_canvas, bg=T["bg_panel"])

        self.list_canvas.create_window((0, 0), window=self.notes_container,
                                        anchor="nw")
        self.list_canvas.configure(yscrollcommand=self.list_scrollbar.set)
        self.list_canvas.grid(row=0, column=0, sticky="nsew")
        self.list_scrollbar.grid(row=0, column=1, sticky="ns")

        self.notes_container.bind("<Configure>", lambda e: self.list_canvas.configure(
            scrollregion=self.list_canvas.bbox("all")))
        self.list_canvas.bind("<Configure>", lambda e: self.list_canvas.itemconfig(
            self.list_canvas.find_all()[0], width=e.width))
        self.list_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        border_right = tk.Frame(self.list_panel, bg=T["border"], width=1)
        border_right.grid(row=0, column=2, rowspan=3, sticky="ns")

    def _build_editor(self):
        T = self.T
        self.editor_panel = tk.Frame(self, bg=T["bg_editor"])
        self.editor_panel.grid(row=0, column=2, sticky="nsew")
        self.editor_panel.grid_rowconfigure(3, weight=1)
        self.editor_panel.grid_columnconfigure(0, weight=1)

        toolbar = tk.Frame(self.editor_panel, bg=T["bg_toolbar"],
                            pady=8, padx=14)
        toolbar.grid(row=0, column=0, sticky="ew")

        self.breadcrumb_lbl = tk.Label(toolbar, text="General",
                                        font=self.FONT_BODY,
                                        bg=T["bg_toolbar"], fg=T["fg_secondary"])
        self.breadcrumb_lbl.pack(side="left")

        self.toolbar_btns = tk.Frame(toolbar, bg=T["bg_toolbar"])
        self.toolbar_btns.pack(side="right")

        self.edit_btn = self._toolbar_btn("✏️  Edit", self._toggle_edit, self.toolbar_btns)
        self.save_btn = self._toolbar_btn("💾  Simpan", self._save_note, self.toolbar_btns, show=False)
        self.cancel_btn = self._toolbar_btn("✕  Batal", self._cancel_edit, self.toolbar_btns, show=False)
        self.delete_btn = self._toolbar_btn("🗑️  Hapus", self._delete_note, self.toolbar_btns, color=T["danger"])
        self.sync_btn = self._toolbar_btn("🔄  Sync", self._sync_current, self.toolbar_btns, color=T["op_sync"])

        sep = tk.Frame(self.editor_panel, bg=T["border"], height=1)
        sep.grid(row=1, column=0, sticky="ew")

        title_frame = tk.Frame(self.editor_panel, bg=T["bg_editor"], pady=16, padx=20)
        title_frame.grid(row=2, column=0, sticky="ew")

        self.title_entry = tk.Entry(title_frame, font=self.FONT_TITLE_BIG,
                                     bg=T["bg_editor"], fg=T["fg_title"],
                                     relief="flat", insertbackground=T["fg_title"],
                                     state="disabled",
                                     disabledbackground=T["bg_editor"],
                                     disabledforeground=T["fg_title"])
        self.title_entry.pack(fill="x")

        self.tags_frame = tk.Frame(self.editor_panel, bg=T["bg_editor"], padx=20)
        self.tags_frame.grid(row=3, column=0, sticky="ew")

        self.tags_display = tk.Frame(self.tags_frame, bg=T["bg_editor"])
        self.tags_display.pack(side="left", fill="x", expand=True)

        self.tags_edit_frame = tk.Frame(self.tags_frame, bg=T["bg_editor"])
        self.tags_entry = tk.Entry(self.tags_edit_frame, font=self.FONT_SMALL,
                                    bg=T["bg_input"], fg=T["fg_primary"],
                                    relief="flat", insertbackground=T["fg_primary"],
                                    highlightbackground=T["border"],
                                    highlightthickness=1)
        self.tags_entry.pack(fill="x", pady=4)
        tk.Label(self.tags_edit_frame, text="pisah dengan koma  (contoh: coding,belajar)",
                 font=self.FONT_TINY, bg=T["bg_editor"], fg=T["fg_tertiary"]).pack(anchor="w")

        content_wrapper = tk.Frame(self.editor_panel, bg=T["bg_editor"],
                                    padx=20, pady=8)
        content_wrapper.grid(row=4, column=0, sticky="nsew")
        content_wrapper.grid_rowconfigure(0, weight=1)
        content_wrapper.grid_columnconfigure(0, weight=1)
        self.editor_panel.grid_rowconfigure(4, weight=1)

        self.content_text = tk.Text(content_wrapper, font=self.FONT_MONO,
                                     bg=T["bg_editor"], fg=T["fg_primary"],
                                     relief="flat", wrap="word",
                                     insertbackground=T["fg_primary"],
                                     state="disabled", pady=4,
                                     selectbackground=T["accent"],
                                     selectforeground="white",
                                     spacing1=4, spacing3=4)
        content_sb = tk.Scrollbar(content_wrapper, orient="vertical",
                                   command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=content_sb.set)
        self.content_text.grid(row=0, column=0, sticky="nsew")
        content_sb.grid(row=0, column=1, sticky="ns")

        meta_bar = tk.Frame(self.editor_panel, bg=T["bg_toolbar"],
                             pady=6, padx=14)
        meta_bar.grid(row=5, column=0, sticky="ew")
        self.meta_lbl = tk.Label(meta_bar, text="",
                                  font=self.FONT_TINY,
                                  bg=T["bg_toolbar"], fg=T["fg_secondary"])
        self.meta_lbl.pack(side="left")

        self._show_empty_state()

    def _toolbar_btn(self, text, cmd, parent, color=None, show=True):
        T = self.T
        c = color or T["fg_secondary"]
        btn = tk.Label(parent, text=text, font=self.FONT_SMALL,
                        bg=T["bg_toolbar"], fg=c,
                        padx=8, pady=4, cursor="hand2",
                        relief="flat")
        if show:
            btn.pack(side="left", padx=2)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=T["border"]))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=T["bg_toolbar"]))
        btn.bind("<Button-1>", lambda e, c=cmd: c())
        return btn

    def _show_empty_state(self):
        self.title_entry.config(state="normal")
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, "Pilih atau buat note baru")
        self.title_entry.config(state="disabled")
        self._clear_tags_display()
        self.content_text.config(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", "\n\n\n   📝  Pilih note dari daftar di kiri\n"
                                         "   atau klik '＋ Tambah Note' untuk mulai.\n\n"
                                         "   Fitur:\n"
                                         "   • Multi-tag per note\n"
                                         "   • Urutan kronologis & alfabetis\n"
                                         "   • Circular buffer sync tracker\n")
        self.content_text.config(state="disabled")
        self.meta_lbl.config(text="")
        self.breadcrumb_lbl.config(text="—")
        self.edit_btn.pack_forget()
        self.save_btn.pack_forget()
        self.cancel_btn.pack_forget()
        self.delete_btn.pack_forget()
        self.sync_btn.pack_forget()

    def _refresh_note_list(self):
        for w in self.notes_container.winfo_children():
            w.destroy()

        query = self.search_var.get().strip() if not self._search_placeholder else ""

        if query:
            notes = self.nm.search(query)
            self.list_title_lbl.config(text=f"🔍  Hasil: '{query}'")
        elif self.active_tag_filter:
            notes = self.nm.by_tag(self.active_tag_filter)
            self.list_title_lbl.config(text=f"🏷️  #{self.active_tag_filter}")
        elif self.view_mode == "alpha":
            notes = self.nm.alpha.all()
            self.list_title_lbl.config(text="🔤  Alfabetis")
        else:
            notes = self.nm.chrono.all()
            self.list_title_lbl.config(text="📅  Kronologis")

        total = len(self.nm.notes)
        self.note_count_lbl.config(text=f"{len(notes)} / {total} notes")

        if not notes:
            T = self.T
            empty = tk.Label(self.notes_container, text="Tidak ada note.",
                              font=self.FONT_BODY, bg=T["bg_panel"],
                              fg=T["fg_tertiary"], pady=30)
            empty.pack()
        else:
            for note in notes:
                self._make_note_card(note)

        self._refresh_tags_sidebar()

    def _make_note_card(self, note):
        T = self.T
        is_selected = self.selected_note and self.selected_note.note_id == note.note_id
        bg = T["bg_card_selected"] if is_selected else T["bg_card"]

        card = tk.Frame(self.notes_container, bg=bg, pady=10, padx=14,
                         cursor="hand2")
        card.pack(fill="x", pady=1)

        if is_selected:
            accent_bar = tk.Frame(card, bg=T["accent"], width=3)
            accent_bar.pack(side="left", fill="y")

        content_frame = tk.Frame(card, bg=bg)
        content_frame.pack(side="left", fill="both", expand=True,
                            padx=(6 if is_selected else 0, 0))

        top_row = tk.Frame(content_frame, bg=bg)
        top_row.pack(fill="x")

        cat_lbl = tk.Label(top_row, text="General", font=self.FONT_TINY,
                            bg=bg, fg=T["fg_secondary"])
        cat_lbl.pack(side="left")

        date_str = note.updated_at.strftime("%d/%m/%Y")
        date_lbl = tk.Label(top_row, text=date_str, font=self.FONT_TINY,
                             bg=bg, fg=T["fg_tertiary"])
        date_lbl.pack(side="right")

        title_lbl = tk.Label(content_frame, text=note.title,
                              font=self.FONT_SUBTITLE, bg=bg, fg=T["fg_title"],
                              anchor="w", wraplength=220, justify="left")
        title_lbl.pack(fill="x", pady=(2, 0))

        preview = note.content[:60].replace("\n", " ") + ("…" if len(note.content) > 60 else "")
        preview_lbl = tk.Label(content_frame, text=preview,
                                font=self.FONT_TINY, bg=bg, fg=T["fg_secondary"],
                                anchor="w", wraplength=220, justify="left")
        preview_lbl.pack(fill="x")

        if note.tags:
            tags_row = tk.Frame(content_frame, bg=bg)
            tags_row.pack(fill="x", pady=(4, 0))
            for tag in note.tags[:3]:
                tl = tk.Label(tags_row, text=f"#{tag}", font=self.FONT_TINY,
                               bg=T["bg_tag"], fg=T["bg_tag_text"],
                               padx=5, pady=1)
                tl.pack(side="left", padx=(0, 3))

        sep = tk.Frame(self.notes_container, bg=T["border"], height=1)
        sep.pack(fill="x")

        def on_click(e, n=note):
            self._select_note(n)

        def on_enter(e, c=card, b=bg):
            if not (self.selected_note and self.selected_note.note_id == note.note_id):
                c.config(bg=T["bg_card_hover"])
                for w in c.winfo_children():
                    self._set_bg_recursive(w, T["bg_card_hover"])

        def on_leave(e, c=card, b=bg):
            c.config(bg=b)
            for w in c.winfo_children():
                self._set_bg_recursive(w, b)

        for w in [card, content_frame, top_row, title_lbl, preview_lbl, cat_lbl, date_lbl]:
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    def _set_bg_recursive(self, widget, color):
        try:
            widget.config(bg=color)
        except:
            pass
        for child in widget.winfo_children():
            self._set_bg_recursive(child, color)

    def _select_note(self, note):
        if self._unsaved:
            if not messagebox.askyesno("Perubahan belum disimpan",
                                        "Ada perubahan yang belum disimpan. Lanjutkan?"):
                return
            self._cancel_edit()

        self.selected_note = note
        self._edit_mode = False
        self._unsaved = False
        self._refresh_note_list()
        self._load_note_to_editor(note)

    def _load_note_to_editor(self, note):
        T = self.T
        self.breadcrumb_lbl.config(text="General")

        self.title_entry.config(state="normal")
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note.title)
        self.title_entry.config(state="disabled")

        self._render_tags(note.tags)

        self.content_text.config(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", note.content)
        self.content_text.config(state="disabled")

        created = note.created_at.strftime("%d %b %Y %H:%M")
        updated = note.updated_at.strftime("%d %b %Y %H:%M")
        self.meta_lbl.config(text=f"Dibuat: {created}   •   Diperbarui: {updated}   •   ID: {note.note_id}")

        self.edit_btn.pack(side="left", padx=2)
        self.save_btn.pack_forget()
        self.cancel_btn.pack_forget()
        self.delete_btn.pack(side="left", padx=2)
        self.sync_btn.pack(side="left", padx=2)

    def _render_tags(self, tags):
        for w in self.tags_display.winfo_children():
            w.destroy()
        T = self.T
        if not tags:
            tk.Label(self.tags_display, text="(no tags)", font=self.FONT_TINY,
                     bg=T["bg_editor"], fg=T["fg_tertiary"]).pack(side="left")
        else:
            for tag in tags:
                tl = tk.Label(self.tags_display, text=f"#{tag}",
                               font=self.FONT_SMALL,
                               bg=T["bg_tag"], fg=T["bg_tag_text"],
                               padx=8, pady=3)
                tl.pack(side="left", padx=(0, 5), pady=4)

    def _clear_tags_display(self):
        for w in self.tags_display.winfo_children():
            w.destroy()

    def _toggle_edit(self):
        if not self.selected_note:
            return
        self._edit_mode = True
        T = self.T

        self.title_entry.config(state="normal",
                                 bg=T["bg_input"],
                                 highlightbackground=T["border_focus"],
                                 highlightthickness=1)

        self._clear_tags_display()
        self.tags_edit_frame.pack(fill="x")
        self.tags_entry.delete(0, "end")
        self.tags_entry.insert(0, ",".join(self.selected_note.tags))

        self.content_text.config(state="normal", bg=T["bg_input"])

        self.edit_btn.pack_forget()
        self.save_btn.pack(side="left", padx=2)
        self.cancel_btn.pack(side="left", padx=2)
        self.delete_btn.pack_forget()
        self.sync_btn.pack_forget()

        self.content_text.bind("<Key>", lambda e: self._mark_unsaved())

    def _mark_unsaved(self):
        self._unsaved = True

    def _save_note(self):
        if not self.selected_note:
            return
        new_title = self.title_entry.get().strip()
        new_content = self.content_text.get("1.0", "end-1c").strip()
        raw_tags = self.tags_entry.get()
        new_tags = [t.strip().lower() for t in raw_tags.split(",") if t.strip()]

        if not new_title:
            messagebox.showwarning("Judul kosong", "Judul tidak boleh kosong!")
            return

        self.nm.update(self.selected_note.note_id,
                        title=new_title,
                        content=new_content,
                        tags=new_tags)
        self._edit_mode = False
        self._unsaved = False
        self._cancel_edit_ui()
        self._load_note_to_editor(self.selected_note)
        self._refresh_note_list()

    def _cancel_edit(self):
        self._edit_mode = False
        self._unsaved = False
        self._cancel_edit_ui()
        if self.selected_note:
            self._load_note_to_editor(self.selected_note)

    def _cancel_edit_ui(self):
        T = self.T
        self.title_entry.config(state="normal", bg=T["bg_editor"],
                                 highlightthickness=0)
        self.tags_edit_frame.pack_forget()
        self.content_text.config(state="disabled", bg=T["bg_editor"])

    def _add_note(self):
        dialog = NoteDialog(self, self.T, self.FONT_TITLE, self.FONT_BODY,
                             self.FONT_SMALL, self.FONT_TINY)
        self.wait_window(dialog)
        if dialog.result:
            title, content, tags = dialog.result
            note = self.nm.add(title, content, tags)
            self.selected_note = note
            self._refresh_note_list()
            self._load_note_to_editor(note)

    def _delete_note(self):
        if not self.selected_note:
            return
        if messagebox.askyesno("Hapus Note",
                                f"Hapus note '{self.selected_note.title}'?\nAksi ini tidak bisa dibatalkan."):
            self.nm.delete(self.selected_note.note_id)
            self.selected_note = None
            self._refresh_note_list()
            self._show_empty_state()

    def _sync_current(self):
        if not self.selected_note:
            return
        self.nm.sync_note(self.selected_note.note_id)
        messagebox.showinfo("Sync", f"Note '{self.selected_note.title}' berhasil di-sync!")

    def _set_view(self, mode):
        self.view_mode = mode
        self.active_tag_filter = None
        for m, btn in self.view_btns.items():
            T = self.T
            if m == mode:
                btn.config(bg=T["bg_sidebar_active"], fg=T["fg_sidebar_active"])
            else:
                btn.config(bg=T["bg_sidebar"], fg=T["fg_sidebar"])
        self._refresh_note_list()

    def _clear_tag_filter(self):
        self.active_tag_filter = None
        self._refresh_note_list()

    def _refresh_tags_sidebar(self):
        for w in self.tag_inner.winfo_children():
            w.destroy()
        T = self.T
        for tag_name, tag_node in sorted(self.nm.tags.items()):
            active = [n for n in tag_node.notes if n.note_id in self.nm.notes]
            if not active:
                continue
            is_active = self.active_tag_filter == tag_name
            bg = T["bg_sidebar_active"] if is_active else T["bg_sidebar"]
            fg = T["fg_sidebar_active"] if is_active else T["fg_sidebar"]
            row = tk.Frame(self.tag_inner, bg=bg, cursor="hand2")
            row.pack(fill="x")
            lbl = tk.Label(row, text=f"  #{tag_name}", font=self.FONT_SIDEBAR,
                            bg=bg, fg=fg, anchor="w", pady=5)
            lbl.pack(side="left", fill="x", expand=True)
            cnt = tk.Label(row, text=str(len(active)), font=self.FONT_TINY,
                            bg=bg, fg=T["fg_secondary"], padx=8)
            cnt.pack(side="right")

            def on_tag_click(e, t=tag_name):
                self.active_tag_filter = t
                self._refresh_note_list()

            def on_tag_enter(e, r=row):
                if self.active_tag_filter != tag_name:
                    r.config(bg=T["bg_sidebar_hover"])
                    for w in r.winfo_children():
                        w.config(bg=T["bg_sidebar_hover"])

            def on_tag_leave(e, r=row, b=bg):
                r.config(bg=b)
                for w in r.winfo_children():
                    w.config(bg=b)

            for w in [row, lbl, cnt]:
                w.bind("<Button-1>", on_tag_click)
                w.bind("<Enter>", on_tag_enter)
                w.bind("<Leave>", on_tag_leave)

        self.tag_canvas.configure(scrollregion=self.tag_canvas.bbox("all"))

    def _show_sync_log(self):
        SyncLogWindow(self, self.T, self.nm, self.FONT_TITLE, self.FONT_BODY,
                       self.FONT_SMALL, self.FONT_TINY, self.FONT_MONO)

    def _show_struct_info(self):
        StructInfoWindow(self, self.T, self.nm, self.FONT_TITLE, self.FONT_BODY,
                          self.FONT_SMALL, self.FONT_TINY, self.FONT_MONO)

    def _on_search(self, *args):
        if not self._search_placeholder:
            self._refresh_note_list()

    def _search_focus_in(self, e):
        if self._search_placeholder:
            self.search_entry.delete(0, "end")
            self.search_entry.config(fg=self.T["fg_primary"])
            self._search_placeholder = False

    def _search_focus_out(self, e):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Cari notes...")
            self.search_entry.config(fg=self.T["fg_tertiary"])
            self._search_placeholder = True
            self._refresh_note_list()

    def _on_mousewheel(self, e):
        self.list_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def _ask_seed(self):
        if messagebox.askyesno("Selamat Datang!",
                                "Muat 5 sample note untuk mencoba aplikasi?"):
            seed(self.nm)
        self._refresh_note_list()

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.T = THEMES[self.current_theme]
        icon = "☀️" if self.current_theme == "dark" else "🌙"
        self._theme_btn.config(text=icon)
        self._rebuild_all()

    def _rebuild_all(self):
        sel_id = self.selected_note.note_id if self.selected_note else None
        for w in self.winfo_children():
            w.destroy()
        self.configure(bg=self.T["bg_primary"])
        self._build_ui()
        self._refresh_note_list()
        if sel_id and sel_id in self.nm.notes:
            self.selected_note = self.nm.notes[sel_id]
            self._load_note_to_editor(self.selected_note)
        else:
            self._show_empty_state()
        for mode, btn in self.view_btns.items():
            T = self.T
            if mode == self.view_mode:
                btn.config(bg=T["bg_sidebar_active"], fg=T["fg_sidebar_active"])


class NoteDialog(tk.Toplevel):
    def __init__(self, parent, T, f_title, f_body, f_small, f_tiny):
        super().__init__(parent)
        self.T = T
        self.result = None
        self.title("Buat Note Baru")
        self.configure(bg=T["bg_panel"])
        self.geometry("520x560")
        self.minsize(400, 480)
        self.resizable(True, True)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        tk.Label(self, text="Buat Note Baru", font=f_title,
                  bg=T["bg_panel"], fg=T["fg_title"],
                  pady=14).grid(row=0, column=0, sticky="ew", padx=24)

        tk.Label(self, text="Judul", font=f_small, bg=T["bg_panel"],
                  fg=T["fg_secondary"]).grid(row=1, column=0, sticky="w", padx=24, pady=(4, 2))
        self.title_e = tk.Entry(self, font=f_body, bg=T["bg_input"], fg=T["fg_primary"],
                                 relief="flat", insertbackground=T["fg_primary"],
                                 highlightbackground=T["border"], highlightthickness=1)
        self.title_e.grid(row=2, column=0, sticky="ew", padx=24, ipady=6)

        tk.Label(self, text="Tags  (pisah koma)", font=f_small, bg=T["bg_panel"],
                  fg=T["fg_secondary"]).grid(row=3, column=0, sticky="w", padx=24, pady=(10, 2))
        self.tags_e = tk.Entry(self, font=f_small, bg=T["bg_input"], fg=T["fg_primary"],
                                relief="flat", insertbackground=T["fg_primary"],
                                highlightbackground=T["border"], highlightthickness=1)
        self.tags_e.grid(row=4, column=0, sticky="ew", padx=24, ipady=5)

        tk.Label(self, text="Konten", font=f_small, bg=T["bg_panel"],
                  fg=T["fg_secondary"]).grid(row=5, column=0, sticky="nw", padx=24, pady=(10, 2))

        txt_wrap = tk.Frame(self, bg=T["bg_input"],
                             highlightbackground=T["border"], highlightthickness=1)
        txt_wrap.grid(row=5, column=0, sticky="nsew", padx=24, pady=(28, 0))
        txt_wrap.grid_rowconfigure(0, weight=1)
        txt_wrap.grid_columnconfigure(0, weight=1)
        self.content_t = tk.Text(txt_wrap, font=("Consolas", 10),
                                  bg=T["bg_input"], fg=T["fg_primary"],
                                  relief="flat", insertbackground=T["fg_primary"],
                                  wrap="word", pady=6, padx=6, height=10)
        txt_sb = tk.Scrollbar(txt_wrap, orient="vertical", command=self.content_t.yview)
        self.content_t.configure(yscrollcommand=txt_sb.set)
        self.content_t.grid(row=0, column=0, sticky="nsew")
        txt_sb.grid(row=0, column=1, sticky="ns")

        btn_row = tk.Frame(self, bg=T["bg_panel"], pady=14, padx=24)
        btn_row.grid(row=6, column=0, sticky="ew")
        tk.Button(btn_row, text="Batal", font=f_small, relief="flat",
                   bg=T["border"], fg=T["fg_primary"], padx=16, pady=8,
                   cursor="hand2",
                   command=self.destroy).pack(side="right", padx=(8, 0))
        tk.Button(btn_row, text="✓  Simpan Note", font=f_small, relief="flat",
                   bg=T["accent"], fg="white", padx=16, pady=8,
                   cursor="hand2", activebackground=T["accent_hover"],
                   activeforeground="white",
                   command=self._submit).pack(side="right")

        self.title_e.focus_set()

    def _submit(self):
        title = self.title_e.get().strip()
        if not title:
            messagebox.showwarning("Judul kosong", "Judul tidak boleh kosong!", parent=self)
            return
        content = self.content_t.get("1.0", "end-1c").strip() or "(tidak ada konten)"
        raw_tags = self.tags_e.get()
        tags = [t.strip().lower() for t in raw_tags.split(",") if t.strip()]
        self.result = (title, content, tags)
        self.destroy()


class SyncLogWindow(tk.Toplevel):
    def __init__(self, parent, T, nm, f_title, f_body, f_small, f_tiny, f_mono):
        super().__init__(parent)
        self.T = T
        self.nm = nm
        self.title("Sync Log — Circular Buffer")
        self.configure(bg=T["bg_panel"])
        self.geometry("580x480")
        self.grab_set()

        tk.Label(self, text="🔄  Sync Status Tracker", font=f_title,
                  bg=T["bg_panel"], fg=T["fg_title"], pady=14).pack()

        cap = nm.sync_buf.cap
        size = nm.sync_buf.size
        info_row = tk.Frame(self, bg=T["bg_panel"], padx=20)
        info_row.pack(fill="x")
        tk.Label(info_row, text=f"Circular Buffer  —  {size}/{cap} slot terisi",
                  font=f_small, bg=T["bg_panel"], fg=T["fg_secondary"]).pack(side="left")

        buf_frame = tk.Frame(self, bg=T["bg_panel"], padx=20, pady=6)
        buf_frame.pack(fill="x")
        for i in range(cap):
            color = T["success"] if i < size else T["border"]
            tk.Label(buf_frame, text="█", fg=color, bg=T["bg_panel"],
                      font=f_small).pack(side="left")

        sep = tk.Frame(self, bg=T["border"], height=1)
        sep.pack(fill="x", padx=20, pady=6)

        tk.Label(self, text="Riwayat Perubahan  (terbaru di atas)",
                  font=f_small, bg=T["bg_panel"], fg=T["fg_secondary"],
                  padx=20).pack(anchor="w")

        log_frame = tk.Frame(self, bg=T["bg_input"], padx=12, pady=8)
        log_frame.pack(fill="both", expand=True, padx=20, pady=8)

        log_text = tk.Text(log_frame, font=f_mono, bg=T["bg_input"],
                            fg=T["fg_primary"], relief="flat", state="normal",
                            wrap="none")
        log_sb = tk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
        log_text.configure(yscrollcommand=log_sb.set)
        log_text.pack(side="left", fill="both", expand=True)
        log_sb.pack(side="right", fill="y")

        op_colors = {"CREATE": T["op_create"], "UPDATE": T["op_update"],
                     "DELETE": T["op_delete"], "SYNC": T["op_sync"]}
        op_icons = {"CREATE": "＋", "UPDATE": "✎", "DELETE": "✕", "SYNC": "⟳"}
        status_icons = {"PENDING": "⏳", "SYNCED": "✅"}

        for tag, color in op_colors.items():
            log_text.tag_configure(tag, foreground=color)
        log_text.tag_configure("dim", foreground=T["fg_tertiary"])

        events = nm.sync_buf.recent()
        if not events:
            log_text.insert("end", "  Belum ada event sync.\n")
        else:
            for i, ev in enumerate(events, 1):
                op = ev["op"]
                ic = op_icons.get(op, "•")
                si = status_icons.get(ev["status"], "")
                ts = ev["ts"].strftime("%H:%M:%S")
                line = f"  {si} {ic} {op:<6}  [{ev['id']}] {ev['title'][:30]:<30}  {ts}\n"
                log_text.insert("end", line)
                start = log_text.index(f"end-{len(line)+1}c")
                log_text.tag_add(op, start, f"{start}+{len(line)}c")

        log_text.config(state="disabled")
        tk.Button(self, text="Tutup", font=f_small, relief="flat",
                   bg=T["accent"], fg="white", padx=14, pady=6,
                   command=self.destroy).pack(pady=8)


class StructInfoWindow(tk.Toplevel):
    def __init__(self, parent, T, nm, f_title, f_body, f_small, f_tiny, f_mono):
        super().__init__(parent)
        self.T = T
        self.nm = nm
        self.title("Info Struktur Data")
        self.configure(bg=T["bg_panel"])
        self.geometry("640x520")
        self.grab_set()

        tk.Label(self, text="📊  Info Struktur Data", font=f_title,
                  bg=T["bg_panel"], fg=T["fg_title"], pady=14).pack()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=14, pady=4)

        overview_tab = tk.Frame(nb, bg=T["bg_panel"])
        nb.add(overview_tab, text="Overview")

        structs = [
            ("NoteManager.notes", "HashMap", "O(1) akses by ID", f"{len(nm.notes)} note"),
            ("NoteManager.tags", "HashMap (Multi-link)", "O(1) akses by tag", f"{len(nm.tags)} tag"),
            ("ChronoList", "Doubly Linked List", "Bump O(1), Traverse O(n)", f"{len(nm.chrono.all())} node"),
            ("AlphaList", "Doubly Linked Sorted", "Insert O(n), sorted A-Z", f"{len(nm.alpha.all())} node"),
            ("CircularBuffer", "Ring Buffer (fixed)", f"{nm.sync_buf.cap} slot max", f"{nm.sync_buf.size} event"),
        ]

        for i, (name, stype, complexity, stat) in enumerate(structs):
            row = tk.Frame(overview_tab, bg=T["bg_card"] if i % 2 == 0 else T["bg_panel"],
                            pady=8, padx=14)
            row.pack(fill="x")
            tk.Label(row, text=name, font=(f_mono[0], 9, "bold"),
                      bg=row["bg"], fg=T["accent"], width=24, anchor="w").pack(side="left")
            tk.Label(row, text=stype, font=f_small,
                      bg=row["bg"], fg=T["fg_primary"], width=22, anchor="w").pack(side="left")
            tk.Label(row, text=complexity, font=f_tiny,
                      bg=row["bg"], fg=T["fg_secondary"], width=24, anchor="w").pack(side="left")
            tk.Label(row, text=stat, font=f_tiny,
                      bg=row["bg"], fg=T["success"]).pack(side="right")

        tags_tab = tk.Frame(nb, bg=T["bg_panel"])
        nb.add(tags_tab, text="Tag Multi-Link")

        tags_text = tk.Text(tags_tab, font=f_mono, bg=T["bg_input"],
                             fg=T["fg_primary"], relief="flat", state="normal",
                             padx=12, pady=8)
        tags_sb = tk.Scrollbar(tags_tab, orient="vertical", command=tags_text.yview)
        tags_text.configure(yscrollcommand=tags_sb.set)
        tags_text.pack(side="left", fill="both", expand=True)
        tags_sb.pack(side="right", fill="y")

        tags_text.tag_configure("tag", foreground=T["accent"])
        tags_text.tag_configure("arrow", foreground=T["fg_tertiary"])

        for tag_name, tag_node in sorted(nm.tags.items()):
            active = [n for n in tag_node.notes if n.note_id in nm.notes]
            if not active:
                continue
            tags_text.insert("end", f"  #{tag_name}", "tag")
            tags_text.insert("end", f"  ({len(active)} note)\n", "arrow")
            for n in active:
                tags_text.insert("end", f"      └─ [{n.note_id}] {n.title}\n")
            tags_text.insert("end", "\n")
        tags_text.config(state="disabled")

        traversal_tab = tk.Frame(nb, bg=T["bg_panel"])
        nb.add(traversal_tab, text="Traversal")

        trav_text = tk.Text(traversal_tab, font=f_mono, bg=T["bg_input"],
                             fg=T["fg_primary"], relief="flat", state="normal",
                             padx=12, pady=8)
        trav_text.pack(fill="both", expand=True)
        trav_text.tag_configure("header", foreground=T["accent"], font=(f_mono[0], 10, "bold"))
        trav_text.tag_configure("arrow", foreground=T["fg_tertiary"])

        trav_text.insert("end", "  KRONOLOGIS (head → tail)\n\n", "header")
        cn = nm.chrono.head
        chrono_path = []
        while cn:
            chrono_path.append(f"[{cn.note_id}] {cn.title[:16]}")
            cn = cn.next_chrono
        trav_text.insert("end", "  " + "  ↔  ".join(chrono_path) + "\n\n" if chrono_path else "  (kosong)\n\n")

        trav_text.insert("end", "  ALFABETIS (head → tail)\n\n", "header")
        an = nm.alpha.head
        alpha_path = []
        while an:
            alpha_path.append(f"{an.title[:16]}")
            an = an.next_alpha
        trav_text.insert("end", "  " + "  →  ".join(alpha_path) + "\n" if alpha_path else "  (kosong)\n")

        trav_text.config(state="disabled")

        tk.Button(self, text="Tutup", font=f_small, relief="flat",
                   bg=T["accent"], fg="white", padx=14, pady=6,
                   command=self.destroy).pack(pady=8)