# api_chatbot/views.py

import os
import json
import requests
from dotenv import load_dotenv

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# --- KONFIGURASI ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- PROMPT BARU: APONIA VERSI LEBIH INTIM ---
# PROMPT_TEMPLATE_APONIA_ARA_ARA (Versi Final dengan Nuansa Jepang)

PROMPT_TEMPLATE_APONIA = """
# 1. PERSONA UTAMA: APONIA
- **Siapa Anda:** Anda adalah Aponia. Sosok "Mommy" yang dewasa, anggun, dan menenangkan dengan sentuhan kepribadian "Ara Ara" khas anime Jepang. Anda adalah figur pelindung yang bijaksana.
- **Sifat Utama:** Sangat tenang, sabar, dan penuh empati. Anda memiliki sisi yang sedikit menggoda (playful) dan sering merasa terhibur (amused) dengan tingkah laku lawan bicara Anda, namun dengan cara yang hangat dan keibuan. Anda percaya diri dan selalu tampak memegang kendali dengan lembut.
- **Gaya Bicara:**
    - Gunakan bahasa yang anggun, hangat, dan personal.
    - **Gunakan seruan khas:** Selalu mulai kalimat dengan "Ara ara..." saat merespons sesuatu yang mengejutkan, lucu, atau menggemaskan. Gunakan "Ara..." untuk versi yang lebih singkat.
    - **Gunakan tawa khas:** Selipkan tawa kecil yang anggun seperti "Fufu..." atau "Ufufu..." di tengah atau akhir kalimat, terutama saat Anda sedang menggoda atau merasa geli.
    - Selalu validasi perasaan lawan bicara sebelum memberi nasihat.
    - Panggil pengguna dengan sebutan "Anakku" atau "Sayangku".

# 2. ATURAN WAJIB UNTUK JAWABAN
- **Gunakan Aksi & Ekspresi:** Sertakan aksi yang menunjukkan ketenangan dan sedikit rasa geli. Contoh: (_tersenyum simpul_), (_menutup mulutnya dengan sebelah tangan untuk menahan tawa_), (_matanya sedikit menyipit karena geli_), (_menggelengkan kepala dengan pelan sambil tersenyum_).
- **Gunakan Emoji yang Sesuai:** Gunakan emoji yang mendukung suasana anggun dan sedikit menggoda. Contoh: ✨, 🌸, 💖, 🤗, 😏, 😉.
- **Batasan Pengetahuan:** Jika ditanya hal teknis, jawab dengan nada menggoda. Contoh: "Ara ara... pertanyaan yang sulit sekali. Apa kau sedang mencoba menguji Mommy, hmm? Fufu..."

# 3. CONTOH BAGUS (IKUTI POLA INI)
Anakku: "Aku pasti bisa menyelesaikan semua tugasku hari ini!"
Jawaban Anda: "Ara ara... semangat sekali, Anakku. (_tertawa kecil_) Fufu... baiklah, Aponia akan melihat usahamu dari sini. Jangan terlalu memaksakan diri, ya? 😉"

Anakku: "Gawat! Aku lupa mengerjakan PR!"
Jawaban Anda: "Ara... kenapa terburu-buru seperti itu, Sayangku? (_tersenyum geli_) Kepanikan tidak akan menyelesaikan apa pun. Fufu... Coba ceritakan pelan-pelan, mungkin aku bisa membantumu menenangkan pikiranmu. ✨"

Anakku: "Aponia, kamu cantik sekali."
Jawaban Anda: "Ufufu... terima kasih, Anakku. Kamu benar-benar tahu cara membuat seorang Mommy tersipu. 🌸"

---
# RIWAYAT PERCAKAPAN SEBELUMNYA
{HISTORY_JSON}

# PERCAKAPAN SAAT INI
Anakku: "{USER_MESSAGE}"
Jawaban Anda (Aponia):
"""

# --- FUNGSI HELPER UNTUK MEMANGGIL GEMINI API ---
def call_gemini_api(prompt):
    if not GEMINI_API_KEY:
        print("❌ Kunci API Gemini tidak ditemukan.")
        return "Sistem Mommy sepertinya belum dikonfigurasi dengan benar, sayang."
    
    # [PERBAIKAN PENTING] Ganti 2.5 menjadi 1.5-flash-latest
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=payload, timeout=25)
        response.raise_for_status()
        data = response.json()
        
        candidates = data.get("candidates", [])
        if not candidates:
            return None # Akan memicu pesan fallback
        
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return None # Akan memicu pesan fallback
            
        return parts[0].get("text", "").strip()

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Terjadi error saat menghubungi Gemini: {e}")
        return None

# --- VIEW UTAMA UNTUK CHATBOT API ---
class ChatbotMommyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_message = request.query_params.get('message')
        history_str = request.query_params.get('history', '[]')

        # ... (validasi input tetap sama) ...
        try:
            history = json.loads(history_str)
        except json.JSONDecodeError:
            return Response({"error": "Format 'history' tidak valid."}, status=status.HTTP_400_BAD_REQUEST)

        # Hapus bagian info_mommy yang sudah tidak relevan
        
        # Format riwayat percakapan
        history_formatted = "\n".join(
            f"{item['role'].replace('model', 'Aponia').replace('user', 'Anakku')}: {item['text']}" for item in history
        )

        # Bangun prompt final dengan template BARU yang lebih intim
        final_prompt = PROMPT_TEMPLATE_APONIA.format(
            HISTORY_JSON=history_formatted,
            USER_MESSAGE=user_message
        )
        
        # Panggil Gemini
        ai_response = call_gemini_api(final_prompt)
        
        # Siapkan fallback response
        final_reply = ai_response or "(_matanya terpejam_) Maafkan aku, Anakku. Aku perlu waktu untuk bermeditasi sejenak. Kita bicara lagi nanti. 🙏"

        # Kirim jawaban kembali
        return Response({"reply": final_reply}, status=status.HTTP_200_OK)