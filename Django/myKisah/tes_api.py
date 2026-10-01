import os
import google.generativeai as genai
from dotenv import load_dotenv

print("--- Memulai Tes API Gemini ---")

# 1. Memuat file .env
load_dotenv()
print("Mencoba memuat file .env...")

# 2. Mengambil API Key
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("\n[GAGAL] API Key tidak ditemukan. Pastikan:")
    print("1. File .env ada di folder yang sama dengan test_api.py")
    print("2. Isi file .env sudah benar: GOOGLE_API_KEY=KunciAnda")
    exit()

print(f"API Key ditemukan! (berakhir dengan: ...{api_key[-4:]})")

# 3. Mengonfigurasi dan Menjalankan API
try:
    print("Mengonfigurasi API...")
    genai.configure(api_key=api_key)

    print("Membuat model 'gemini-2.5-flash'...")
    model = genai.GenerativeModel('gemini-2.5-flash')

    print("Mengirim prompt 'Halo, apa kabarmu?'...")
    response = model.generate_content("Halo, apa kabarmu?")

    print("\n--- HASIL ---")
    print("[SUKSES] API Berhasil Merespons!")
    print("Jawaban dari Gemini:", response.text)
    print("-------------")

except Exception as e:
    print("\n--- HASIL ---")
    print(f"[GAGAL] Terjadi error saat menghubungi API:")
    print(e)
    print("-------------")