import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from pygame import mixer
import os
import time
import tkinter as tk
from tkinter import messagebox

LANGUAGE_CODES = {
    'en': 'English', 'hi': 'Hindi', 'fr': 'French', 'es': 'Spanish', 'zh-cn': 'Chinese (Simplified)',
    'ja': 'Japanese', 'ko': 'Korean', 'de': 'German', 'ru': 'Russian', 'ar': 'Arabic',
    'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'tr': 'Turkish', 'sv': 'Swedish',
    'el': 'Greek', 'pa': 'Punjabi', 'ta': 'Tamil', 'te': 'Telugu', 'ml': 'Malayalam'
}

LANGUAGE_NAMES_TO_CODES = {name: code for code, name in LANGUAGE_CODES.items()}

def translate_text(text, src_language, dest_language):
    translator = Translator()
    try:
        translated = translator.translate(text, src=src_language, dest=dest_language)
        return translated.text
    except Exception as e:
        print(f"Error in translation: {e}")
        return None

def speak(text, language='en'):
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        file_path = os.path.join(os.getcwd(), "output.mp3")
        tts.save(file_path)
        mixer.init()
        mixer.music.load(file_path)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)
        mixer.music.unload()
        mixer.quit()
        os.remove(file_path)
    except Exception as e:
        print(f"Error in TTS: {e}")
        try:
            os.remove(file_path)
        except Exception as remove_error:
            print(f"Error removing file: {remove_error}")

def recognize_speech(src_language, dest_language):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        messagebox.showinfo("Listening", "Please speak now...")
        audio = recognizer.listen(source, timeout=10)
    try:
        spoken_text = recognizer.recognize_google(audio, language=src_language)
        text_input_var.set(spoken_text)
        spoken_text_display.delete(1.0, tk.END)
        spoken_text_display.insert(tk.END, spoken_text)
        translated_text = translate_text(spoken_text, src_language, dest_language)
        if translated_text:
            translated_text_display.delete(1.0, tk.END)
            translated_text_display.insert(tk.END, translated_text)
            root.after(500, lambda: speak(translated_text, language=dest_language))
        else:
            messagebox.showerror("Translation Error", "Could not translate the speech.")
    except sr.UnknownValueError:
        messagebox.showerror("Recognition Error", "Sorry, I couldn't understand your speech.")
    except sr.RequestError:
        messagebox.showerror("API Error", "Sorry, speech recognition service is unavailable.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def handle_text_input(src_language, dest_language):
    text = text_input_var.get().strip()
    if not text:
        messagebox.showwarning("Input Error", "Please enter some text to translate.")
        return
    translated_text = translate_text(text, src_language, dest_language)
    if translated_text:
        translated_text_display.delete(1.0, tk.END)
        translated_text_display.insert(tk.END, translated_text)
        root.after(500, lambda: speak(translated_text, language=dest_language))
    else:
        messagebox.showerror("Translation Error", "Could not translate the text.")

def translate():
    src_language = LANGUAGE_NAMES_TO_CODES.get(src_lang_var.get())
    dest_language = LANGUAGE_NAMES_TO_CODES.get(dest_lang_var.get())
    if not src_language or not dest_language:
        messagebox.showerror("Language Error", "Please select both source and destination languages.")
        return
    if input_mode_var.get() == "text":
        handle_text_input(src_language, dest_language)
    else:
        recognize_speech(src_language, dest_language)

def on_input_mode_change():
    if input_mode_var.get() == "text":
        spoken_text_label.pack_forget()
        spoken_text_display.pack_forget()
        text_input_label.pack(pady=5, padx=10, before=translate_button, anchor="w")
        text_input_entry.pack(pady=5, padx=10, before=translate_button)
    else:
        spoken_text_label.pack(pady=5, padx=10, before=translate_button, anchor="w")
        spoken_text_display.pack(pady=5, padx=10, before=translate_button)
        text_input_label.pack_forget()
        text_input_entry.pack_forget()

root = tk.Tk()
root.title("Transiify")
root.geometry("600x800") 
root.configure(bg="#f0f0f0")

label_font = ("Helvetica", 14)
button_font = ("Helvetica", 12, "bold")

lang_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
lang_frame.pack(fill="x")

src_lang_label = tk.Label(lang_frame, text="Source Language:", font=label_font, bg="#f0f0f0")
src_lang_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
src_lang_var = tk.StringVar()
src_lang_menu = tk.OptionMenu(lang_frame, src_lang_var, *LANGUAGE_CODES.values())
src_lang_menu.grid(row=0, column=1, padx=10, pady=5, sticky="w")

dest_lang_label = tk.Label(lang_frame, text="Destination Language:", font=label_font, bg="#f0f0f0")
dest_lang_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
dest_lang_var = tk.StringVar()
dest_lang_menu = tk.OptionMenu(lang_frame, dest_lang_var, *LANGUAGE_CODES.values())
dest_lang_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

mode_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
mode_frame.pack(fill="x")

input_mode_label = tk.Label(mode_frame, text="Input Mode:", font=label_font, bg="#f0f0f0")
input_mode_label.pack(anchor="w", padx=10)

input_mode_var = tk.StringVar(value="speech")
speech_radio = tk.Radiobutton(mode_frame, text="Speech Input", variable=input_mode_var, value="speech",
                              font=label_font, bg="#f0f0f0", command=on_input_mode_change)
speech_radio.pack(anchor="w", padx=20)

text_radio = tk.Radiobutton(mode_frame, text="Text Input", variable=input_mode_var, value="text",
                            font=label_font, bg="#f0f0f0", command=on_input_mode_change)
text_radio.pack(anchor="w", padx=20)

translate_button = tk.Button(root, text="Translate", font=button_font, bg="#4caf50", fg="white", command=translate)
translate_button.pack(pady=10)

text_input_label = tk.Label(root, text="Enter Text to Translate:", font=label_font, bg="#f0f0f0")
text_input_var = tk.StringVar()
text_input_entry = tk.Entry(root, textvariable=text_input_var, font=label_font, width=60)

spoken_text_var = tk.StringVar()
spoken_text_label = tk.Label(root, text="Recognized Text:", font=label_font, bg="#f0f0f0")

spoken_text_display = tk.Text(root, height=6, width=60, wrap=tk.WORD, font=label_font)
spoken_text_display.pack_forget()

translated_text_label = tk.Label(root, text="Translated Text:", font=label_font, bg="#f0f0f0")
translated_text_label.pack(anchor="w", padx=10)

translated_text_display = tk.Text(root, height=6, width=60, wrap=tk.WORD, font=label_font)
translated_text_display.pack(pady=5, padx=10)

root.mainloop()
