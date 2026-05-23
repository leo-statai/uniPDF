import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfWriter


def merge_pdfs(pdf_list, output_path):
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    writer = PdfWriter()
    for path in pdf_list:
        writer.append(path)
    with open(output_path, "wb") as f:
        writer.write(f)
    writer.close()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mesclar PDFs")
        self.resizable(False, False)
        self._paths = []
        self._build()

    def _build(self):
        tk.Label(self, text="Arquivos para mesclar (na ordem desejada):", anchor="w").pack(
            fill="x", padx=10, pady=(10, 2)
        )

        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10)

        self.lb = tk.Listbox(frame, selectmode=tk.SINGLE, width=62, height=14, activestyle="dotbox")
        sb = tk.Scrollbar(frame, command=self.lb.yview)
        self.lb.config(yscrollcommand=sb.set)
        self.lb.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        btns = tk.Frame(self)
        btns.pack(fill="x", padx=10, pady=4)
        tk.Button(btns, text="Adicionar",  command=self._add).pack(side="left", padx=2)
        tk.Button(btns, text="Remover",    command=self._remove).pack(side="left", padx=2)
        tk.Button(btns, text="▲", width=3, command=self._up).pack(side="left", padx=2)
        tk.Button(btns, text="▼", width=3, command=self._down).pack(side="left", padx=2)

        out_frame = tk.Frame(self)
        out_frame.pack(fill="x", padx=10, pady=6)
        tk.Label(out_frame, text="Salvar como:").pack(side="left")
        self.out_var = tk.StringVar(value="pdfs_agrupados.pdf")
        tk.Entry(out_frame, textvariable=self.out_var, width=40).pack(side="left", padx=6)
        tk.Button(out_frame, text="Escolher…", command=self._pick_output).pack(side="left")

        tk.Button(
            self, text="Mesclar PDFs", command=self._merge,
            bg="#2E7D32", fg="white", font=("", 11, "bold"), padx=12, pady=6,
        ).pack(pady=10)

    # --- lista ---

    def _add(self):
        files = filedialog.askopenfilenames(title="Selecionar PDFs", filetypes=[("PDF", "*.pdf")])
        for f in files:
            if f not in self._paths:
                self._paths.append(f)
                self.lb.insert(tk.END, os.path.basename(f))

    def _remove(self):
        if sel := self.lb.curselection():
            i = sel[0]
            self.lb.delete(i)
            self._paths.pop(i)

    def _up(self):
        if (sel := self.lb.curselection()) and sel[0] > 0:
            i = sel[0]
            self._swap(i, i - 1)
            self.lb.select_set(i - 1)

    def _down(self):
        if (sel := self.lb.curselection()) and sel[0] < self.lb.size() - 1:
            i = sel[0]
            self._swap(i, i + 1)
            self.lb.select_set(i + 1)

    def _swap(self, a, b):
        self._paths[a], self._paths[b] = self._paths[b], self._paths[a]
        text_a, text_b = self.lb.get(a), self.lb.get(b)
        self.lb.delete(a); self.lb.insert(a, text_b)
        self.lb.delete(b); self.lb.insert(b, text_a)

    # --- saída ---

    def _pick_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=os.path.basename(self.out_var.get()),
        )
        if path:
            self.out_var.set(path)

    # --- mesclar ---

    def _merge(self):
        if not self._paths:
            messagebox.showwarning("Aviso", "Adicione ao menos um arquivo PDF.")
            return
        output = self.out_var.get().strip()
        if not output:
            messagebox.showwarning("Aviso", "Informe o caminho do arquivo de saída.")
            return
        try:
            merge_pdfs(self._paths, output)
            messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{output}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    App().mainloop()
