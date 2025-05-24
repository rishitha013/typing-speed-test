import tkinter as tk
import random
import time
import difflib

class TypingTest:
    def __init__(self, window):
        self.root = window
        self.root.title("Typing Speed Test")
        self.root.geometry("800x800")
        self.root.resizable(False, False)

        self.theme = "light"
        self.bg_color = "white"
        self.text_color = "black"
        self.difficulty = tk.StringVar(value="medium")

        
        try:
            self.bg_image = tk.PhotoImage(file="bg_typing_test.png")
        except tk.TclError:
            self.bg_image = None

        self.canvas = tk.Canvas(self.root, width=800, height=800)
        self.canvas.pack(fill="both", expand=True)
        if self.bg_image:
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

       
        self.time_left = 60
        self.start_time = None
        self.timer_running = False
        self.sentence = self.get_sentence()

        
        self.title_label = tk.Label(self.root, text="Typing Speed Test", font=("Arial", 24, "bold"), bg=self.bg_color, fg=self.text_color)
        self.canvas.create_window(400, 30, window=self.title_label)

       
        self.difficulty_label = tk.Label(self.root, text="Difficulty:", font=("Arial", 12), bg=self.bg_color, fg=self.text_color)
        self.difficulty_menu = tk.OptionMenu(self.root, self.difficulty, "easy", "medium", "hard", command=self.change_difficulty)
        self.difficulty_menu.config(font=("Arial", 12))
        self.canvas.create_window(340, 70, window=self.difficulty_label)
        self.canvas.create_window(430, 70, window=self.difficulty_menu)

        
        self.label_sentence = tk.Label(self.root, text=self.sentence, font=("Arial", 16, "bold"), wraplength=700,
                                       bg=self.bg_color, fg=self.text_color, justify="left")
        self.canvas.create_window(400, 130, window=self.label_sentence)

       
        self.entry = tk.Text(self.root, height=4, font=("Courier", 14), wrap="word",
                             bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color)
        self.canvas.create_window(400, 220, window=self.entry, width=700, height=100)

      
        self.timer_label = tk.Label(self.root, text="Time Left: 60s", font=("Arial", 12), bg=self.bg_color, fg=self.text_color)
        self.live_stats_label = tk.Label(self.root, text="", font=("Arial", 12), bg=self.bg_color, fg=self.text_color)
        self.canvas.create_window(400, 280, window=self.timer_label)
        self.canvas.create_window(400, 310, window=self.live_stats_label)

        
        self.button = tk.Button(self.root, text="Check Result", font=("Arial", 12), command=self.show_results)
        self.canvas.create_window(400, 350, window=self.button)

        
        self.stats_label = tk.Label(self.root, text="", font=("Arial", 12), bg=self.bg_color, fg=self.text_color)
        self.canvas.create_window(400, 390, window=self.stats_label)

        
        self.restart_button = tk.Button(self.root, text="Restart", font=("Arial", 12), command=self.restart_test)
        self.theme_button = tk.Button(self.root, text="Toggle Theme", font=("Arial", 12), command=self.toggle_theme)
        self.history_button = tk.Button(self.root, text="View History", font=("Arial", 12), command=self.show_history)
        self.canvas.create_window(300, 430, window=self.restart_button)
        self.canvas.create_window(400, 430, window=self.theme_button)
        self.canvas.create_window(500, 430, window=self.history_button)

        self.restart_button.lower()
        self.entry.bind("<KeyPress>", self.start_timer)

    def get_sentence(self):
        file_map = {
            "easy": "sentences_easy.txt",
            "medium": "sentences_medium.txt",
            "hard": "sentences_hard.txt"
        }
        file_name = file_map.get(self.difficulty.get(), "sentences_medium.txt")
        try:
            with open(file_name, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            return random.choice(lines)
        except FileNotFoundError:
            return f"Could not load {file_name}."

    def change_difficulty(self, _=None):
        self.restart_test()

    def start_timer(self, event):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()
        self.track_typing()

    def update_timer(self):
        if self.time_left > 0:
            elapsed = int(time.time() - self.start_time)
            self.time_left = max(0, 60 - elapsed)
            self.timer_label.config(text=f"Time Left: {self.time_left}s")
            self.root.after(1000, self.update_timer)
        else:
            self.show_results()

    def track_typing(self):
        typed_text = self.entry.get("1.0", tk.END).strip()
        chars_typed = len(typed_text)
        chars_left = max(0, len(self.sentence) - chars_typed)
        words_typed = len(typed_text.split())
        elapsed = time.time() - self.start_time if self.start_time else 1
        wpm = (words_typed / elapsed) * 60 if elapsed > 0 else 0

        self.live_stats_label.config(
            text=f"Typed: {chars_typed} | Left: {chars_left} | Words: {words_typed} | WPM: {wpm:.2f}"
        )

        self.entry.tag_remove("mistake", "1.0", tk.END)
        for i in range(min(len(typed_text), len(self.sentence))):
            if typed_text[i] != self.sentence[i]:
                line, col = "1", i
                start = f"{line}.{col}"
                end = f"{line}.{col+1}"
                self.entry.tag_add("mistake", start, end)
        self.entry.tag_config("mistake", foreground="red")

        if self.timer_running:
            self.root.after(300, self.track_typing)

    def show_results(self):
        typed_text = self.entry.get("1.0", tk.END).strip()
        total_chars = len(typed_text)
        total_words = len(typed_text.split())

        accuracy = difflib.SequenceMatcher(None, typed_text, self.sentence).ratio() * 100 if self.sentence else 0
        elapsed_minutes = (60 - self.time_left) / 60
        wpm = total_words / elapsed_minutes if elapsed_minutes > 0 else 0

        self.stats_label.config(
            text=f"Chars: {total_chars} | Words: {total_words} | WPM: {wpm:.2f} | Accuracy: {accuracy:.2f}%"
        )

        with open("typing_history.txt", "a") as history_file:
            history_file.write(
                f"Difficulty: {self.difficulty.get().capitalize()} | Chars: {total_chars}, Words: {total_words}, "
                f"WPM: {wpm:.2f}, Accuracy: {accuracy:.2f}%\n"
            )

        self.entry.config(state='disabled')
        self.button.config(state='disabled')
        self.restart_button.lift()

    def restart_test(self):
        self.time_left = 60
        self.timer_running = False
        self.sentence = self.get_sentence()
        self.label_sentence.config(text=self.sentence)
        self.entry.config(state='normal')
        self.entry.delete("1.0", tk.END)
        self.timer_label.config(text="Time Left: 60s")
        self.stats_label.config(text="")
        self.live_stats_label.config(text="")
        self.entry.tag_remove("mistake", "1.0", tk.END)
        self.button.config(state='normal')
        self.restart_button.lower()

    def toggle_theme(self):
        if self.theme == "light":
            self.theme = "dark"
            self.bg_color = "#1e1e1e"
            self.text_color = "white"
        else:
            self.theme = "light"
            self.bg_color = "white"
            self.text_color = "black"

        widgets = [
            self.title_label, self.label_sentence, self.entry,
            self.timer_label, self.live_stats_label, self.stats_label,
            self.difficulty_label
        ]
        for widget in widgets:
            widget.config(bg=self.bg_color, fg=self.text_color)
        self.entry.config(insertbackground=self.text_color)
        self.canvas.config(bg=self.bg_color)

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Typing History")
        history_window.geometry("600x400")

        text_area = tk.Text(history_window, wrap="word", font=("Arial", 12))
        text_area.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_area)
        scrollbar.pack(side="right", fill="y")
        text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_area.yview)

        try:
            with open("typing_history.txt", "r") as f:
                history = f.read()
                text_area.insert("1.0", history)
        except FileNotFoundError:
            text_area.insert("1.0", "No history found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTest(root)
    root.mainloop()
