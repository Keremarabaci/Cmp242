
import os
import uuid
import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import pathlib
import datetime

DATA_DIR = "students"  # tüm veriler buraya kaydedilecek

os.makedirs(DATA_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    # basit: dosya sistemine uygun hale getir
    return "".join(c for c in name if c.isalnum() or c in "._- ").strip()

class StudentStore:
    """Öğrenciyi kaydetme / okuma işlemleri (klasör + metadata json)."""

    def __init__(self, base_dir=DATA_DIR):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def list_students(self):
        """Tüm öğrencilerin metadatalarını oku ve döndür."""
        students = []
        for d in os.listdir(self.base_dir):
            dd = os.path.join(self.base_dir, d)
            if os.path.isdir(dd):
                meta_path = os.path.join(dd, "meta.json")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                            meta["_dir"] = dd
                            students.append(meta)
                    except Exception as e:
                        print("Metadata okunamadı:", meta_path, e)
        # Son eklenen en üstte olacak şekilde sırala
        students.sort(key=lambda m: m.get("saved_at", ""), reverse=True)
        return students

    def save_student(self, first_name, last_name, image_path=None, file_paths=None):
        """
        Yeni öğrenci kaydet.
        - Her öğrenci için benzersiz klasör: uuid
        - meta.json dosyası tutulur
        - resim ve dosyalar klasöre kopyalanır
        """
        uid = str(uuid.uuid4())
        folder = os.path.join(self.base_dir, uid)
        os.makedirs(folder, exist_ok=True)

        saved_files = []
        saved_image = None

        # Resmi kopyala
        if image_path:
            try:
                ext = pathlib.Path(image_path).suffix
                image_name = f"photo{ext}"
                dest = os.path.join(folder, image_name)
                shutil.copy2(image_path, dest)
                saved_image = image_name
            except Exception as e:
                raise RuntimeError(f"Resim kaydedilemedi: {e}")

        # Diğer dosyaları kopyala
        if file_paths:
            for i, fp in enumerate(file_paths, start=1):
                try:
                    basename = os.path.basename(fp)
                    # aynı isim çakışmasını önlemek için başına indeks ekle
                    dest_name = f"{i}_{sanitize_filename(basename)}"
                    dest = os.path.join(folder, dest_name)
                    shutil.copy2(fp, dest)
                    saved_files.append(dest_name)
                except Exception as e:
                    print("Dosya kopyalanamadı:", fp, e)

        meta = {
            "id": uid,
            "first_name": first_name,
            "last_name": last_name,
            "photo": saved_image,      # dosya adı (klasör içinde)
            "files": saved_files,      # dosya adları (klasör içinde)
            "saved_at": datetime.datetime.utcnow().isoformat() + "Z"
        }

        meta_path = os.path.join(folder, "meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return meta

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Öğrenci Yöneticisi")
        self.geometry("850x520")
        self.resizable(True, True)

        self.store = StudentStore(DATA_DIR)
        self.selected_image_path = None
        self.selected_files = []

        self.create_widgets()
        self.refresh_student_list()

    def create_widgets(self):
        # Grid: solda liste, sağda detay ve form
        self.columnconfigure(0, weight=1, minsize=260)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # Soldaki çerçeve: öğrenci listesi
        left_frame = ttk.Frame(self, padding=8)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        ttk.Label(left_frame, text="Öğrenciler", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.student_listbox = tk.Listbox(left_frame)
        self.student_listbox.grid(row=1, column=0, sticky="nsew", pady=6)
        self.student_listbox.bind("<<ListboxSelect>>", self.on_student_select)

        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=6)
        ttk.Button(btn_frame, text="Yenile", command=self.refresh_student_list).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Yeni Öğrenci Ekle", command=self.clear_form).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Sil", command=self.delete_selected_student).pack(side="left", padx=2)

        # Sağdaki çerçeve: form ve detay gösterim
        right_frame = ttk.Frame(self, padding=8)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)

        # Form
        form = ttk.LabelFrame(right_frame, text="Öğrenci Bilgileri", padding=10)
        form.grid(row=0, column=0, sticky="nsew")
        for i in range(2): form.columnconfigure(i, weight=1)

        ttk.Label(form, text="Ad:").grid(row=0, column=0, sticky="w")
        self.entry_first = ttk.Entry(form)
        self.entry_first.grid(row=0, column=1, sticky="ew")

        ttk.Label(form, text="Soyad:").grid(row=1, column=0, sticky="w")
        self.entry_last = ttk.Entry(form)
        self.entry_last.grid(row=1, column=1, sticky="ew")

        # Resim yükleme
        ttk.Label(form, text="Fotoğraf:").grid(row=2, column=0, sticky="w")
        photo_btn = ttk.Button(form, text="Resim Seç", command=self.choose_image)
        photo_btn.grid(row=2, column=1, sticky="w")
        self.photo_label = ttk.Label(form, text="(Seçilmedi)")
        self.photo_label.grid(row=3, column=0, columnspan=2, sticky="w")

        # Dosya yükleme
        ttk.Label(form, text="Dosyalar:").grid(row=4, column=0, sticky="w")
        files_btn = ttk.Button(form, text="Dosya(lar) Seç", command=self.choose_files)
        files_btn.grid(row=4, column=1, sticky="w")
        self.files_listbox = tk.Listbox(form, height=4)
        self.files_listbox.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=6)

        # Kaydet butonu
        save_btn = ttk.Button(form, text="Kaydet", command=self.save_student)
        save_btn.grid(row=6, column=0, columnspan=2, sticky="ew", pady=6)

        # Detay gösterimi
        detail_box = ttk.LabelFrame(right_frame, text="Seçili Öğrenci Detayları", padding=10)
        detail_box.grid(row=1, column=0, sticky="nsew", pady=10)
        detail_box.columnconfigure(1, weight=1)
        detail_box.rowconfigure(0, weight=1)

        # Fotoğraf gösterimi (thumbnail)
        self.photo_canvas = tk.Canvas(detail_box, width=220, height=220, bd=1, relief="sunken")
        self.photo_canvas.grid(row=0, column=0, rowspan=4, sticky="nw", padx=6, pady=6)
        self.photo_image_tk = None

        # Bilgiler
        ttk.Label(detail_box, text="İsim:").grid(row=0, column=1, sticky="w")
        self.lbl_name = ttk.Label(detail_box, text="-")
        self.lbl_name.grid(row=0, column=2, sticky="w")

        ttk.Label(detail_box, text="Kaydedildi:").grid(row=1, column=1, sticky="w")
        self.lbl_saved = ttk.Label(detail_box, text="-")
        self.lbl_saved.grid(row=1, column=2, sticky="w")

        ttk.Label(detail_box, text="Dosyalar:").grid(row=2, column=1, sticky="nw")
        self.detail_files_listbox = tk.Listbox(detail_box, height=6)
        self.detail_files_listbox.grid(row=2, column=2, sticky="nsew", padx=4, pady=4)
        self.detail_files_listbox.bind("<Double-Button-1>", self.open_detail_file)

    def refresh_student_list(self):
        self.student_listbox.delete(0, tk.END)
        self.students = self.store.list_students()
        for s in self.students:
            display = f"{s['first_name']} {s['last_name']}"
            self.student_listbox.insert(tk.END, display)

    def clear_form(self):
        self.entry_first.delete(0, tk.END)
        self.entry_last.delete(0, tk.END)
        self.selected_image_path = None
        self.selected_files = []
        self.photo_label.config(text="(Seçilmedi)")
        self.files_listbox.delete(0, tk.END)

    def choose_image(self):
        fp = filedialog.askopenfilename(title="Fotoğraf seç", filetypes=[("Image files", ".png;.jpg;.jpeg;.bmp;.gif"), ("All files", ".*")])
        if fp:
            self.selected_image_path = fp
            self.photo_label.config(text=os.path.basename(fp))

    def choose_files(self):
        fps = filedialog.askopenfilenames(title="Dosyalar", filetypes=[("All files", ".")])
        if fps:
            self.selected_files = list(fps)
            self.files_listbox.delete(0, tk.END)
            for f in self.selected_files:
                self.files_listbox.insert(tk.END, os.path.basename(f))

    def save_student(self):
        first = self.entry_first.get().strip()
        last = self.entry_last.get().strip()
        if not first or not last:
            messagebox.showwarning("Eksik bilgi", "Lütfen ad ve soyad girin.")
            return
        try:
            meta = self.store.save_student(first, last, image_path=self.selected_image_path, file_paths=self.selected_files)
            messagebox.showinfo("Kaydedildi", f"{first} {last} kaydedildi.")
            self.clear_form()
            self.refresh_student_list()
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme sırasında hata: {e}")

    def on_student_select(self, event):
        sel = self.student_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        meta = self.students[idx]
        self.show_student_detail(meta)

    def show_student_detail(self, meta):
        # İsim
        self.lbl_name.config(text=f"{meta.get('first_name','')} {meta.get('last_name','')}")
        self.lbl_saved.config(text=meta.get("saved_at", "-"))

        # Dosyalar listesini doldur
        self.detail_files_listbox.delete(0, tk.END)
        folder = meta.get("_dir")
        if not folder:
            return
        files = meta.get("files", [])
        for f in files:
            self.detail_files_listbox.insert(tk.END, f)

        # Fotoğrafı göster (thumbnail)
        self.photo_canvas.delete("all")
        photo_name = meta.get("photo")
        if photo_name:
            photo_path = os.path.join(folder, photo_name)
            if os.path.exists(photo_path):
                try:
                    img = Image.open(photo_path)
                    # Thumbnail oluştur
                    img.thumbnail((220, 220))
                    self.photo_image_tk = ImageTk.PhotoImage(img)
                    self.photo_canvas.create_image(110, 110, image=self.photo_image_tk)
                except Exception as e:
                    print("Fotoğraf açılamadı:", e)
            else:
                self.photo_canvas.create_text(110,110, text="Fotoğraf bulunamadı")
        else:
            self.photo_canvas.create_text(110,110, text="(Fotoğraf yok)")

    def open_detail_file(self, event):
        sel = self.detail_files_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        filename = self.detail_files_listbox.get(idx)
        # karşılık gelen öğrenci
        sel_idx = self.student_listbox.curselection()
        if not sel_idx:
            return
        meta = self.students[sel_idx[0]]
        folder = meta.get("_dir")
        fullpath = os.path.join(folder, filename)
        if os.path.exists(fullpath):
            try:
                # Windows'ta dosyayı aç
                os.startfile(fullpath)
            except Exception as e:
                messagebox.showerror("Açma hatası", f"Dosya açılamadı: {e}")
        else:
            messagebox.showerror("Bulunamadı", "Dosya bulunamadı.")

    def delete_selected_student(self):
        sel = self.student_listbox.curselection()
        if not sel:
            messagebox.showwarning("Seçim yok", "Lütfen silmek için bir öğrenci seçin.")
            return
        idx = sel[0]
        meta = self.students[idx]
        folder = meta.get("_dir")
        if messagebox.askyesno("Sil", f"{meta['first_name']} {meta['last_name']} silinsin mi? Bu işlem geri alınamaz."):
            try:
                shutil.rmtree(folder)
                messagebox.showinfo("Silindi", "Öğrenci ve dosyaları silindi.")
                self.refresh_student_list()
                # temizle detay alanı
                self.lbl_name.config(text="-")
                self.lbl_saved.config(text="-")
                self.detail_files_listbox.delete(0, tk.END)
                self.photo_canvas.delete("all")
            except Exception as e:
                messagebox.showerror("Hata", f"Silme işlemi sırasında hata: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
