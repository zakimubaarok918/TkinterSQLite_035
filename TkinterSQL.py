
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Membuat database
db = sqlite3.connect("prediksi_diabetes.db")
cursor = db.cursor()

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
db.commit()
db.close()


# Fungsi prediksi
def prediksi(gula, bmi, riwayat):
    if gula >= 200:
        if gula >= 250:
            return "Sangat Tinggi"
        return "Tinggi"

    elif gula >= 140:
        if bmi >= 30 or riwayat == "Ya":
            return "Tinggi"
        return "Sedang"

    elif bmi >= 30:
        if riwayat == "Ya":
            return "Sedang"
        return "Waspada"

    elif riwayat == "Ya":
        return "Waspada"

    return "Rendah"


# Fungsi simpan dan tampilkan hasil
def simpan():
    nama = nama_input.get().strip()
    usia = usia_input.get().strip()
    gula = gula_input.get().strip()
    bmi = bmi_input.get().strip()
    riwayat = riwayat_input.get()

    if not nama or not usia or not gula or not bmi:
        messagebox.showwarning("Peringatan", "Semua data harus diisi!")
        return

    try:
        usia = int(usia)
        gula = float(gula)
        bmi = float(bmi)
    except ValueError:
        messagebox.showerror("Error", "Usia, gula darah, dan BMI harus berupa angka!")
        return

    if not 1 <= usia <= 120:
        messagebox.showerror("Error", "Usia harus 1 sampai 120 tahun!")
        return

    if not 20 <= gula <= 600:
        messagebox.showerror("Error", "Gula darah harus 20 sampai 600!")
        return

    if not 10 <= bmi <= 100:
        messagebox.showerror("Error", "BMI harus 10 sampai 100!")
        return

    if riwayat not in ["Ya", "Tidak"]:
        messagebox.showerror("Error", "Pilih riwayat diabetes orang tua!")
        return

    hasil = prediksi(gula, bmi, riwayat)

    warna = {
        "Rendah": "green",
        "Waspada": "goldenrod",
        "Sedang": "orange",
        "Tinggi": "red",
        "Sangat Tinggi": "darkred"
    }

    hasil_label.config(
        text="Hasil Prediksi: " + hasil,
        bg=warna[hasil],
        fg="white"
    )

    try:
        db = sqlite3.connect("prediksi_diabetes.db")
        cursor = db.cursor()

        cursor.execute("""
        INSERT INTO pasien
        (nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nama, usia, gula, bmi, riwayat, hasil))

        db.commit()
        db.close()

        messagebox.showinfo("Berhasil", "Data pasien berhasil disimpan!")

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))


# Fungsi melihat data
def lihat_data():
    jendela = tk.Toplevel(root)
    jendela.title("Data Pasien")
    jendela.geometry("850x350")

    kolom = (
        "id", "nama_pasien", "usia", "gula_darah",
        "bmi", "riwayat_ortu", "hasil_prediksi"
    )

    tabel = ttk.Treeview(jendela, columns=kolom, show="headings")

    judul = [
        "ID", "Nama Pasien", "Usia", "Gula Darah",
        "BMI", "Riwayat Ortu", "Hasil Prediksi"
    ]

    for kol, teks in zip(kolom, judul):
        tabel.heading(kol, text=teks)
        tabel.column(kol, width=115, anchor="center")

    tabel.pack(fill="both", expand=True)

    db = sqlite3.connect("prediksi_diabetes.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pasien ORDER BY id DESC")
    data = cursor.fetchall()
    db.close()

    for baris in data:
        tabel.insert("", "end", values=baris)

    if not data:
        messagebox.showinfo("Informasi", "Belum ada data pasien.")


# Fungsi reset
def reset():
    nama_input.delete(0, tk.END)
    usia_input.delete(0, tk.END)
    gula_input.delete(0, tk.END)
    bmi_input.delete(0, tk.END)
    riwayat_input.set("")

    hasil_label.config(
        text="Hasil Prediksi: -",
        bg="lightgray",
        fg="black"
    )


# Membuat tampilan aplikasi
root = tk.Tk()
root.title("Prediksi Risiko Diabetes")
root.geometry("470x520")
root.configure(bg="lightblue")
root.resizable(False, False)

tk.Label(
    root,
    text="APLIKASI PREDIKSI RISIKO DIABETES",
    font=("Arial", 14, "bold"),
    bg="lightblue"
).pack(pady=15)

form = tk.Frame(root, bg="lightblue")
form.pack()

tk.Label(form, text="Nama Pasien", bg="lightblue").grid(row=0, column=0, sticky="w", pady=7)
nama_input = tk.Entry(form, width=28)
nama_input.grid(row=0, column=1)

tk.Label(form, text="Usia", bg="lightblue").grid(row=1, column=0, sticky="w", pady=7)
usia_input = tk.Entry(form, width=28)
usia_input.grid(row=1, column=1)

tk.Label(form, text="Gula Darah (mg/dL)", bg="lightblue").grid(row=2, column=0, sticky="w", pady=7)
gula_input = tk.Entry(form, width=28)
gula_input.grid(row=2, column=1)

tk.Label(form, text="BMI", bg="lightblue").grid(row=3, column=0, sticky="w", pady=7)
bmi_input = tk.Entry(form, width=28)
bmi_input.grid(row=3, column=1)

tk.Label(form, text="Riwayat Diabetes Ortu", bg="lightblue").grid(row=4, column=0, sticky="w", pady=7)
riwayat_input = ttk.Combobox(
    form, values=["Ya", "Tidak"], state="readonly", width=25
)
riwayat_input.grid(row=4, column=1)
riwayat_input.set("")

hasil_label = tk.Label(
    root,
    text="Hasil Prediksi: -",
    font=("Arial", 12, "bold"),
    bg="lightgray",
    pady=10,
    width=35
)
hasil_label.pack(pady=20)

tk.Button(
    root, text="Simpan & Prediksi", command=simpan,
    bg="green", fg="white", width=18
).pack(pady=4)

tk.Button(
    root, text="Lihat Data", command=lihat_data,
    bg="blue", fg="white", width=18
).pack(pady=4)

tk.Button(
    root, text="Reset", command=reset, width=18
).pack(pady=4)

tk.Label(
    root,
    text="Aplikasi pembelajaran, bukan alat diagnosis medis.",
    bg="lightblue",
    font=("Arial", 8)
).pack(pady=12)

root.mainloop()
