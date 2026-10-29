
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


DB_NAME = "prediksi_diabetes.db"

def koneksi_database():
    return sqlite3.connect(DB_NAME)


def buat_tabel():
    with koneksi_database() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pasien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pasien TEXT NOT NULL,
                usia INTEGER NOT NULL,
                gula_darah REAL NOT NULL,
                bmi REAL NOT NULL,
                riwayat_ortu TEXT NOT NULL,
                hasil_prediksi TEXT NOT NULL
            )
        """)
        conn.commit()


def prediksi_risiko(gula, bmi, riwayat):
    if gula >= 200:
        if gula >= 250:
            return "Sangat Tinggi"
        return "Tinggi"

    elif gula >= 140:
        if bmi >= 30 or riwayat == "Ya":
            return "Tinggi"
        return "Sedang"

    else:
        if bmi >= 30:
            if riwayat == "Ya":
                return "Sedang"
            return "Waspada"

        elif riwayat == "Ya":
            return "Waspada"

        else:
            return "Rendah"


def simpan_data():
    nama = entry_nama.get().strip()
    usia_text = entry_usia.get().strip()
    gula_text = entry_gula.get().strip()
    bmi_text = entry_bmi.get().strip()
    riwayat = combo_riwayat.get()

    # Validasi input kosong
    if not nama or not usia_text or not gula_text or not bmi_text:
        messagebox.showwarning(
            "Peringatan", "Semua kolom harus diisi!"
        )
        return

    if not usia_text.isdigit():
        messagebox.showerror(
            "Input Salah", "Usia harus berupa bilangan bulat."
        )
        return

    try:
        usia = int(usia_text)
        gula = float(gula_text)
        bmi = float(bmi_text)
    except ValueError:
        messagebox.showerror(
            "Input Salah",
            "Gula darah dan BMI harus berupa angka."
        )
        return

    # Validasi rentang nilai
    if not 1 <= usia <= 120:
        messagebox.showerror(
            "Input Salah", "Usia harus antara 1 sampai 120 tahun."
        )
        return

    if not 20 <= gula <= 600:
        messagebox.showerror(
            "Input Salah",
            "Gula darah harus antara 20 sampai 600 mg/dL."
        )
        return

    if not 10 <= bmi <= 100:
        messagebox.showerror(
            "Input Salah", "BMI harus antara 10 sampai 100."
        )
        return

    if riwayat not in ("Ya", "Tidak"):
        messagebox.showwarning(
            "Peringatan", "Pilih riwayat diabetes orang tua."
        )
        return

    hasil = prediksi_risiko(gula, bmi, riwayat)

    # Warna label hasil
    warna = {
        "Rendah": "#2e8b57",
        "Waspada": "#daa520",
        "Sedang": "#ff8c00",
        "Tinggi": "#dc3545",
        "Sangat Tinggi": "#8b0000"
    }

    label_hasil.config(
        text=f"Hasil Prediksi: {hasil}",
        bg=warna[hasil],
        fg="white"
    )

    try:
        with koneksi_database() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pasien
                (nama_pasien, usia, gula_darah, bmi,
                 riwayat_ortu, hasil_prediksi)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nama, usia, gula, bmi, riwayat, hasil))
            conn.commit()

        messagebox.showinfo(
            "Berhasil",
            f"Data pasien berhasil disimpan.\n"
            f"Hasil prediksi: {hasil}"
        )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error", str(error)
        )


def lihat_data():
    jendela_data = tk.Toplevel(root)
    jendela_data.title("Riwayat Data Pasien")
    jendela_data.geometry("950x400")

    kolom = (
        "id", "nama_pasien", "usia", "gula_darah",
        "bmi", "riwayat_ortu", "hasil_prediksi"
    )

    tabel = ttk.Treeview(
        jendela_data,
        columns=kolom,
        show="headings"
    )

    judul = {
        "id": "ID",
        "nama_pasien": "Nama Pasien",
        "usia": "Usia",
        "gula_darah": "Gula Darah",
        "bmi": "BMI",
        "riwayat_ortu": "Riwayat Ortu",
        "hasil_prediksi": "Hasil Prediksi"
    }

    for kolom_nama in kolom:
        tabel.heading(
            kolom_nama, text=judul[kolom_nama]
        )
        tabel.column(
            kolom_nama, width=125, anchor="center"
        )

    tabel.column("id", width=50)
    tabel.column("nama_pasien", width=170)

    scrollbar = ttk.Scrollbar(
        jendela_data,
        orient="vertical",
        command=tabel.yview
    )
    tabel.configure(yscrollcommand=scrollbar.set)

    tabel.pack(
        side="left", fill="both", expand=True, padx=(10, 0), pady=10
    )
    scrollbar.pack(
        side="right", fill="y", padx=(0, 10), pady=10
    )

    try:
        with koneksi_database() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nama_pasien, usia, gula_darah,
                       bmi, riwayat_ortu, hasil_prediksi
                FROM pasien
                ORDER BY id DESC
            """)
            data = cursor.fetchall()

        for baris in data:
            tabel.insert("", "end", values=baris)

        if not data:
            messagebox.showinfo(
                "Informasi", "Belum ada data pasien."
            )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error", str(error)
        )


def reset_form():
    entry_nama.delete(0, tk.END)
    entry_usia.delete(0, tk.END)
    entry_gula.delete(0, tk.END)
    entry_bmi.delete(0, tk.END)
    combo_riwayat.set("Tidak")
    label_hasil.config(
        text="Hasil Prediksi: -",
        bg="#e9ecef",
        fg="black"
    )



buat_tabel()

root = tk.Tk()
root.title("Aplikasi Prediksi Risiko Diabetes")
root.geometry("520x600")
root.resizable(False, False)
root.configure(bg="#f2f5f9")

judul = tk.Label(
    root,
    text="PREDIKSI RISIKO DIABETES",
    font=("Arial", 17, "bold"),
    bg="#1f4e79",
    fg="white",
    pady=18
)
judul.pack(fill="x")

form = tk.Frame(root, bg="#f2f5f9", padx=30, pady=20)
form.pack(fill="both", expand=True)

tk.Label(
    form, text="Nama Pasien", bg="#f2f5f9",
    font=("Arial", 10)
).grid(row=0, column=0, sticky="w", pady=8)

entry_nama = tk.Entry(form, width=30)
entry_nama.grid(row=0, column=1, pady=8)

tk.Label(
    form, text="Usia (tahun)", bg="#f2f5f9",
    font=("Arial", 10)
).grid(row=1, column=0, sticky="w", pady=8)

entry_usia = tk.Entry(form, width=30)
entry_usia.grid(row=1, column=1, pady=8)

tk.Label(
    form, text="Gula Darah (mg/dL)", bg="#f2f5f9",
    font=("Arial", 10)
).grid(row=2, column=0, sticky="w", pady=8)

entry_gula = tk.Entry(form, width=30)
entry_gula.grid(row=2, column=1, pady=8)

tk.Label(
    form, text="BMI", bg="#f2f5f9",
    font=("Arial", 10)
).grid(row=3, column=0, sticky="w", pady=8)

entry_bmi = tk.Entry(form, width=30)
entry_bmi.grid(row=3, column=1, pady=8)

tk.Label(
    form, text="Riwayat Diabetes Ortu",
    bg="#f2f5f9", font=("Arial", 10)
).grid(row=4, column=0, sticky="w", pady=8)

combo_riwayat = ttk.Combobox(
    form,
    values=["Ya", "Tidak"],
    state="readonly",
    width=27
)
combo_riwayat.grid(row=4, column=1, pady=8)
combo_riwayat.set("Tidak")

label_hasil = tk.Label(
    form,
    text="Hasil Prediksi: -",
    font=("Arial", 12, "bold"),
    bg="#e9ecef",
    fg="black",
    pady=12
)
label_hasil.grid(
    row=5, column=0, columnspan=2,
    sticky="ew", pady=18
)

tombol = tk.Frame(form, bg="#f2f5f9")
tombol.grid(row=6, column=0, columnspan=2, pady=10)

tk.Button(
    tombol,
    text="Simpan & Prediksi",
    command=simpan_data,
    bg="#198754",
    fg="white",
    width=17
).grid(row=0, column=0, padx=5, pady=5)

tk.Button(
    tombol,
    text="Lihat Data",
    command=lihat_data,
    bg="#0d6efd",
    fg="white",
    width=12
).grid(row=0, column=1, padx=5, pady=5)

tk.Button(
    tombol,
    text="Reset",
    command=reset_form,
    bg="#6c757d",
    fg="white",
    width=10
).grid(row=1, column=0, columnspan=2, pady=5)

catatan = tk.Label(
    form,
    text="Untuk pembelajaran, bukan diagnosis medis.",
    font=("Arial", 8),
    fg="#555555",
    bg="#f2f5f9"
)
catatan.grid(row=7, column=0, columnspan=2, pady=10)

root.mainloop()
