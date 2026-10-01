# chatbot/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variable hanya sekali
load_dotenv()

# =====================================
# 1️⃣ CHAT UNTUK WEB
# =====================================
def chat_view(request):
    """Menangani halaman web chatbot berbasis session."""
    chat_history = request.session.get('chat_history', [])

    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        if not prompt:
            return render(request, 'chatbot/chat.html', {'history': chat_history})

        chat_history.append({'role': 'user', 'text': prompt})
        api_key = os.getenv('GOOGLE_API_KEY')

        if not api_key:
            response_text = "Error: GOOGLE_API_KEY tidak ditemukan."
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')

                custom_prompt = (
                    "Kamu adalah 'Mommy', chatbot yang lembut, sabar, dan penyayang. "
                    f"Jawab dengan kasih sayang: '{prompt}'"
                )

                response = model.generate_content(custom_prompt)
                response_text = response.text or "(Mommy sedang berpikir... 💭)"
            except Exception as e:
                response_text = f"Terjadi kesalahan: {e}"

        chat_history.append({'role': 'bot', 'text': response_text})
        request.session['chat_history'] = chat_history

    return render(request, 'chatbot/chat.html', {'history': chat_history})


# =====================================
# 2️⃣ API UNTUK UNITY
# =====================================
@csrf_exempt
def api_chat_view(request):
    """
    Endpoint API JSON untuk chatbot Unity.
    Body: {"message": "..."}
    Response: {"user": "...", "bot": "..."}
    """
    if request.method != "POST":
        return JsonResponse({"error": "Gunakan metode POST."}, status=405)

    # Parse JSON dari request body
    try:
        data = json.loads(request.body.decode('utf-8'))
        prompt = data.get('message', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Format JSON tidak valid."}, status=400)

    if not prompt:
        return JsonResponse({"error": "Field 'message' kosong."}, status=400)

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return JsonResponse({"error": "GOOGLE_API_KEY tidak ditemukan."}, status=500)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        custom_prompt = (
            "Kamu adalah 'Mommy', chatbot yang lembut dan penyayang. "
            f"Jawab dengan penuh kasih sayang untuk pesan berikut: '{prompt}'"
        )

        response = model.generate_content(custom_prompt)
        bot_reply = response.text or "(Mommy belum bisa menjawab sekarang, ya 💕)"
    except Exception as e:
        bot_reply = f"Terjadi kesalahan saat memanggil API: {e}"

    return JsonResponse({
        "user": prompt,
        "bot": bot_reply
    })
