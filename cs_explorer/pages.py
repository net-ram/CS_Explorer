import os
import random
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

from . import content as content_data
from .widgets import BasePage, ScrollableFrame

class HomePage(BasePage):
    page_name = "Home"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = controller.colors
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        ttk.Label(self, text="Your Digital Learning Hub", style="Title.TLabel").grid(row=0, column=0, sticky="w", padx=28, pady=(24, 10))

        hero = tk.Frame(self, bg=c["primary"], padx=24, pady=18)
        hero.grid(row=1, column=0, sticky="ew", padx=28)
        hero.grid_columnconfigure(0, weight=3)
        hero.grid_columnconfigure(1, weight=2)
        self.hero_title = tk.Label(hero, text="", bg=c["primary"], fg="white", font=controller.font(17, "bold"), wraplength=620, justify="left")
        self.hero_title.grid(row=0, column=0, sticky="w")
        self.hero_body = tk.Label(hero, text="", bg=c["primary"], fg="#e8eeff", font=controller.font(11), wraplength=640, justify="left")
        self.hero_body.grid(row=1, column=0, sticky="w", pady=(10, 16))
        actions = tk.Frame(hero, bg=c["primary"])
        actions.grid(row=2, column=0, sticky="w")
        ttk.Button(actions, text="Start learning", style="Primary.TButton", command=lambda: controller.show_frame("Learn")).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(actions, text="Jump into Play", style="Secondary.TButton", command=lambda: controller.show_frame("Play")).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(actions, text="Try a quiz", style="Secondary.TButton", command=lambda: controller.show_frame("Quiz")).grid(row=0, column=2)
        ttk.Button(actions, text="Quick tour", style="Secondary.TButton", command=lambda: controller.show_onboarding_tour(force=True)).grid(row=0, column=3, padx=(8, 0))
        self.profile_panel = tk.Frame(hero, bg="#2d53cb", padx=18, pady=18)
        self.profile_panel.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=(18, 0))
        self.profile_header = tk.Label(self.profile_panel, text="Profile Snapshot", bg="#5a4ff3", fg="white", font=controller.font(13, "bold"))
        self.profile_header.pack(anchor="w")
        self.profile_avatar = tk.Label(self.profile_panel, text="🚀", bg="#5a4ff3", fg="white", font=controller.font(28, "bold"))
        self.profile_avatar.pack(anchor="w", pady=(10, 2))
        self.profile_avatar_image = None
        self.profile_stats = tk.Label(self.profile_panel, text="", bg="#5a4ff3", fg="#edf2ff", justify="left", font=controller.font(10), wraplength=330)
        self.profile_stats.pack(anchor="w", pady=(8, 0))

        self.body_scroll = ScrollableFrame(self, bg=c["bg"], controller=controller)
        self.body_scroll.grid(row=2, column=0, sticky="nsew", padx=28, pady=14)
        body = self.body_scroll.inner
        body.configure(bg=c["bg"])
        body.grid_columnconfigure((0, 1), weight=1)
        body.grid_rowconfigure((1, 2), weight=1)

        stats_wrap = tk.Frame(body, bg=c["bg"])
        stats_wrap.grid(row=0, column=0, columnspan=2, sticky="ew")
        stats_wrap.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.stat_values = []
        for idx, label in enumerate(["📘 Topics viewed", "🎮 Play progress", "⚡ Best quiz score", "🏆 Badges earned", "✨ XP"]):
            card = self.make_card(stats_wrap)
            card.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 8, 0), pady=(0, 12))
            value = tk.Label(card, text="0", bg=c["surface"], fg=c["text"], font=controller.font(22, "bold"))
            value.pack(anchor="w")
            tk.Label(card, text=label, bg=c["surface"], fg=c["muted"], font=controller.font(10)).pack(anchor="w", pady=(6, 0))
            self.stat_values.append(value)

        roadmap = self.make_card(body)
        roadmap.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        tk.Label(roadmap, text="Progress map & learning path", bg=c["surface"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        self.roadmap_text = tk.Label(roadmap, text="", bg=c["surface"], fg=c["muted"], wraplength=520, justify="left", font=controller.font(10))
        self.roadmap_text.pack(anchor="w", pady=(10, 8))
        self.path_canvas = tk.Canvas(roadmap, width=520, height=110, bg=c["surface"], highlightthickness=0)
        self.path_canvas.pack(anchor="w", fill="x", pady=(0, 8))
        self.path_status = tk.Label(roadmap, text="", bg=c["surface"], fg=c["text"], wraplength=500, justify="left", font=controller.font(10, "bold"))
        self.path_status.pack(anchor="w", pady=(0, 8))
        self.recommend_text = tk.Label(roadmap, text="", bg=c["surface"], fg=c["text"], wraplength=500, justify="left", font=controller.font(10, "bold"))
        self.recommend_text.pack(anchor="w")

        badges = self.make_card(body, bg=c["warning_soft"])
        badges.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        tk.Label(badges, text="Unlocked badges", bg=c["warning_soft"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        self.badge_wrap = tk.Frame(badges, bg=c["warning_soft"])
        self.badge_wrap.pack(fill="both", expand=True, pady=(10, 0))

        mastery = self.make_card(body, bg=c["accent_soft"])
        mastery.grid(row=2, column=0, sticky="nsew", padx=(0, 8), pady=(8, 0))
        tk.Label(mastery, text="Mastery & motivation", bg=c["accent_soft"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        self.mastery_text = tk.Label(mastery, text="", bg=c["accent_soft"], fg=c["text"], justify="left", wraplength=500, font=controller.font(10))
        self.mastery_text.pack(anchor="w", pady=(10, 0))

        history = self.make_card(body)
        history.grid(row=2, column=1, sticky="nsew", padx=(8, 0), pady=(8, 0))
        tk.Label(history, text="Recent activity feed", bg=c["surface"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        self.history_text = tk.Label(history, text="", bg=c["surface"], fg=c["muted"], justify="left", wraplength=500, font=controller.font(10))
        self.history_text.pack(anchor="w", pady=(10, 10))
        tk.Button(history, text="Reset current profile", command=self.reset_progress, relief="flat", bd=0, bg=c["danger"], fg="white", font=controller.font(10, "bold"), padx=14, pady=10).pack(anchor="w")
        self.refresh_stats()

    def reset_progress(self):
        if not messagebox.askyesno("Reset progress", "This will clear the current profile progress. Continue?"):
            return
        old = self.controller.state_data
        preserved = {key: old.get(key) for key in ["profile_name", "avatar", "avatar_image", "high_contrast", "dark_mode", "large_text", "audio_enabled", "easy_read", "onboarding_seen"]}
        self.controller.state_data = self.controller._default_profile_state(self.controller.current_profile)
        self.controller.state_data.update(preserved)
        self.controller.log_event("Reset the current profile progress.")
        self.controller.save_state()
        self.controller.rebuild_ui("Home")

    def refresh_stats(self):
        state = self.controller.state_data
        level_info = self.controller.current_level_info()
        next_step = (state.get("recommended_focus", ["Explore a topic in Learn to get started."])[0])

        self.hero_title.config(text=f"Hello {state.get('profile_name', self.controller.current_profile)}! Are you ready to build your computing skills and have fun?")
        self.hero_body.config(text="Explore key topics, unlock challenge modes, build your streak, earn XP, and move from Beginner to Expert as you learn.")
        self.stat_values[0].config(text=str(len(state.get("topics_viewed", []))))
        self.stat_values[1].config(text=f"{self.controller.total_play_completed()}/{self.controller.total_play_challenges()}")
        self.stat_values[2].config(text=f"{state.get('best_quiz_score', 0)}")
        self.stat_values[3].config(text=str(len(state.get("badges", []))))
        self.stat_values[4].config(text=str(state.get("xp", 0)))

        weakest = sorted(state.get("mastery", {}).items(), key=lambda item: item[1])[:2]
        strongest = sorted(state.get("mastery", {}).items(), key=lambda item: item[1], reverse=True)[:2]

        self.profile_panel.configure(bg="#2d53cb")
        self.profile_header.configure(bg="#5a4ff3", fg="white")
        avatar_image_path = state.get("avatar_image", "")
        self.profile_avatar_image = None
        if avatar_image_path and os.path.exists(avatar_image_path):
            try:
                if Image is not None and ImageTk is not None:
                    avatar_img = Image.open(avatar_image_path)
                    avatar_img.thumbnail((72, 72))
                    self.profile_avatar_image = ImageTk.PhotoImage(avatar_img)
                else:
                    avatar_img = tk.PhotoImage(file=avatar_image_path)
                    max_w, max_h = 72, 72
                    step_x = max(1, (avatar_img.width() + max_w - 1) // max_w)
                    step_y = max(1, (avatar_img.height() + max_h - 1) // max_h)
                    step = max(step_x, step_y)
                    if step > 1:
                        avatar_img = avatar_img.subsample(step, step)
                    self.profile_avatar_image = avatar_img
                self.profile_avatar.configure(image=self.profile_avatar_image, text="", bg="#5a4ff3")
            except Exception:
                self.profile_avatar.configure(image="", text=state.get("avatar", "🚀"), bg="#5a4ff3", fg="white")
        else:
            self.profile_avatar.configure(image="", text=state.get("avatar", "🚀"), bg="#5a4ff3", fg="white")
        self.profile_stats.configure(
            bg="#5a4ff3",
            fg="#edf2ff",
            text=(
                f"Profile: {self.controller.current_profile}\n"
                f"Level: {level_info['name']}\n"
                f"XP: {state.get('xp', 0)}\n"
                f"Learning streak: {state.get('learning_streak', 0)} day(s)\n"
                f"Unlocked Play modes: {', '.join(state.get('unlocked_games', []))}\n"
                f"Last played: {state.get('last_played', 'N/A')}"
            )
        )
        stage = "Expert review" if state.get('best_quiz_score', 0) >= 8 else ("Explorer path" if state.get('best_quiz_score', 0) >= 4 else "Building foundations")
        self.roadmap_text.config(text=(
            "1. Learn a topic\n2. Unlock and complete Play modes\n3. Use the quiz to test understanding\n4. Follow recommendations to improve\n5. Export a text progress report if needed\n\n"
            f"Current stage: {stage}"
        ))
        self.path_status.config(text=(
            f"Topics complete: {len(state.get('topics_viewed', []))}/{len(content_data.LEARN_TOPICS)}\n"
            f"Unlocked games: {', '.join(state.get('unlocked_games', []))}\n"
            f"Next step: {next_step}"
        ))
        self.recommend_text.config(text="Next best actions:\n- " + "\n- ".join(state.get("recommended_focus", [])[:3]))
        self.mastery_text.config(text=(
            f"Strongest topics: {', '.join(t for t, _ in strongest)}\n"
            f"Topics to revisit: {', '.join(t for t, _ in weakest)}\n"
            f"Best quiz score: {state.get('best_quiz_score', 0)}\n"
            f"Completed play challenges: {self.controller.total_play_completed()}\n"
            f"Level progress: {level_info['name']} ({state.get('xp', 0)} XP) with a {state.get('learning_streak', 0)} day streak."
        ))
        self.history_text.config(text="\n".join(state.get("session_history", [])[-6:]) or "No activity saved yet.")
        self.draw_progress_map()
        for child in self.badge_wrap.winfo_children():
            child.destroy()
        badges = state.get("badges", [])
        if not badges:
            tk.Label(self.badge_wrap, text="No badges yet. Explore Learn or complete a Play task to unlock one.", bg=self.controller.colors["warning_soft"], fg=self.controller.colors["text"], wraplength=500, justify="left", font=self.controller.font(10)).pack(anchor="w")
        else:
            for badge_id in badges:
                title, desc = content_data.BADGE_LIBRARY[badge_id]
                stamp = state.get("badge_timestamps", {}).get(badge_id, "")
                pill = tk.Frame(self.badge_wrap, bg="#fff7e7", highlightbackground=self.controller.colors["warning"], highlightthickness=1, padx=12, pady=10)
                pill.pack(fill="x", pady=4)
                tk.Label(pill, text=title, bg="#fff7e7", fg=self.controller.colors["text"], font=self.controller.font(10, "bold")).pack(anchor="w")
                tk.Label(pill, text=f"{desc}\nAwarded: {stamp}", bg="#fff7e7", fg=self.controller.colors["muted"], font=self.controller.font(9), wraplength=480, justify="left").pack(anchor="w", pady=(3, 0))

    def draw_progress_map(self):
        c = self.controller.colors
        canvas = self.path_canvas
        canvas.delete("all")
        canvas.configure(bg=c["surface"])

        topics_done = len(self.controller.state_data.get("topics_viewed", [])) > 0
        play_done = self.controller.total_play_completed() > 0
        quiz_done = self.controller.state_data.get("quiz_attempts", 0) > 0

        stages = [("Home", True), ("Learn", topics_done), ("Play", play_done), ("Quiz", quiz_done)]
        xs = [70, 210, 350, 490]
        y = 45

        for i in range(len(xs)-1):
            line_color = c["success"] if stages[i+1][1] else c["border"]
            canvas.create_line(xs[i]+22, y, xs[i+1]-22, y, fill=line_color, width=4)

        for idx, ((label, done), x) in enumerate(zip(stages, xs), start=1):
            fill = c["success"] if done else c["surface_dark"]
            outline = c["primary"] if done else c["border"]
            text_color = "white" if done else c["muted"]
            canvas.create_oval(x-22, y-22, x+22, y+22, fill=fill, outline=outline, width=2)
            canvas.create_text(x, y, text=str(idx), fill=text_color, font=self.controller.font(11, "bold"))
            canvas.create_text(x, y+34, text=label, fill=c["text"], font=self.controller.font(9, "bold"))

    def on_show(self):
        self.refresh_stats()



class LearnPage(BasePage):
    page_name = "Learn"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = controller.colors
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        ttk.Label(self, text="Learn & Explore", style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", padx=28, pady=(24, 12))

        sidebar = self.make_card(self, bg=c["surface"], padx=12, pady=12)
        sidebar.grid(row=1, column=0, sticky="ns", padx=(28, 12), pady=(0, 24))
        tk.Label(sidebar, text="Topics", bg=c["surface"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w", padx=8, pady=(4, 10))
        self.topic_filter_var = tk.StringVar()
        self.topic_list_wrap = tk.Frame(sidebar, bg=c["surface"])
        self.topic_list_wrap.pack(fill="both", expand=True)
        self.topic_buttons = {}
        self.topic_order = list(content_data.LEARN_TOPICS.keys())
        for idx, topic in enumerate(self.topic_order, start=1):
            btn = tk.Button(self.topic_list_wrap, text=f"{idx}. {topic}", relief="flat", bd=0, bg=c["surface_alt"], activebackground=c["primary_soft"], fg=c["text"], font=controller.font(10, "bold"), anchor="w", padx=14, pady=12, command=lambda t=topic: self.show_topic(t))
            btn.pack(fill="x", padx=8, pady=4)
            self.topic_buttons[topic] = btn
        self.no_results_label = tk.Label(self.topic_list_wrap, text="No topics match your search yet.", bg=c["surface"], fg=c["muted"], font=controller.font(9))

        self.content_wrap = ScrollableFrame(self, bg=c["bg"], controller=controller)
        self.content_wrap.grid(row=1, column=1, sticky="nsew", padx=(0, 28), pady=(0, 24))
        content = self.content_wrap.inner

        hero = self.make_card(content, bg=c["surface"], padx=24, pady=22)
        hero.pack(fill="x")
        self.topic_title = tk.Label(hero, text="Select a topic", bg=c["surface"], fg=c["text"], font=controller.font(22, "bold"))
        self.topic_title.pack(anchor="w")
        self.topic_subtitle = tk.Label(hero, text="", bg=c["surface"], fg=c["muted"], font=controller.font(11, slant="italic"))
        self.topic_subtitle.pack(anchor="w", pady=(4, 0))
        self.progress_markers = tk.Label(hero, text="Intro  →  Core idea  →  Example  →  Apply it", bg=c["surface"], fg=c["primary_dark"], font=controller.font(10, "bold"))
        self.progress_markers.pack(anchor="w", pady=(10, 0))
        self.topic_overview = self.make_glossary_text_widget(hero, bg=c["surface"], fg=c["text"], font=controller.font(11), width_chars=90, min_height=4)
        self.topic_overview.pack(anchor="w", fill="x", pady=(14, 0))

        upper = tk.Frame(content, bg=c["bg"])
        upper.pack(fill="both", expand=True, pady=(14, 0))
        upper.grid_columnconfigure((0, 1), weight=1)

        self.points_card = self.make_card(upper)
        self.points_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(self.points_card, text="Core ideas", bg=c["surface"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        self.points_container = tk.Frame(self.points_card, bg=c["surface"])
        self.points_container.pack(fill="x", pady=(12, 0))

        self.real_life_card = self.make_card(upper, bg=c["primary_soft"])
        self.real_life_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(self.real_life_card, text="Why this matters in real life", bg=c["primary_soft"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        self.real_life_text = self.make_glossary_text_widget(self.real_life_card, bg=c["primary_soft"], fg=c["text"], font=controller.font(11), width_chars=40, min_height=4)
        self.real_life_text.pack(anchor="w", fill="x", pady=(12, 0))

        middle = tk.Frame(content, bg=c["bg"])
        middle.pack(fill="both", expand=True, pady=(14, 0))
        middle.grid_columnconfigure((0, 1), weight=1)

        self.detail_card = self.make_card(middle, bg=c["surface_alt"])
        self.detail_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        tk.Label(self.detail_card, text="Key Terms", bg=c["surface_alt"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.detail_text = self.make_glossary_text_widget(self.detail_card, bg=c["surface_alt"], fg=c["text"], font=controller.font(10), width_chars=40, min_height=9)
        self.detail_text.pack(anchor="w", fill="x", pady=(10, 0))

        self.scenario_card = self.make_card(middle, bg=c["warning_soft"])
        self.scenario_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        tk.Label(self.scenario_card, text="Example scenario", bg=c["warning_soft"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.scenario_text = self.make_glossary_text_widget(self.scenario_card, bg=c["warning_soft"], fg=c["text"], font=controller.font(10), width_chars=40, min_height=6)
        self.scenario_text.pack(anchor="w", fill="x", pady=(10, 0))

        bottom = tk.Frame(content, bg=c["bg"])
        bottom.pack(fill="both", expand=True, pady=(14, 0))
        bottom.grid_columnconfigure((0, 1), weight=1)

        self.deeper_card = self.make_card(bottom)
        self.deeper_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        tk.Label(self.deeper_card, text="Deeper Reading", bg=c["surface"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.deeper_text = self.make_glossary_text_widget(self.deeper_card, bg=c["surface"], fg=c["text"], font=controller.font(10), width_chars=40, min_height=12)
        self.deeper_text.pack(anchor="w", fill="x", pady=(10, 0))

        self.career_card = self.make_card(bottom, bg=c["surface_dark"])
        self.career_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        tk.Label(self.career_card, text="Career link", bg=c["surface_dark"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.career_text = self.make_glossary_text_widget(self.career_card, bg=c["surface_dark"], fg=c["text"], font=controller.font(10), width_chars=40, min_height=4)
        self.career_text.pack(anchor="w", fill="x", pady=(10, 0))
        self.next_button = ttk.Button(self.career_card, text="Open related practice", command=self.open_related)
        self.next_button.pack(anchor="w", pady=(12, 0))

        self.current_topic = list(content_data.LEARN_TOPICS.keys())[0]
        self.filter_topics()
        self.show_topic(self.current_topic)

    def make_glossary_text_widget(self, parent, bg, fg, font, width_chars, min_height=3):
        widget = tk.Text(
            parent,
            wrap="word",
            relief="flat",
            bd=0,
            highlightthickness=0,
            bg=bg,
            fg=fg,
            font=font,
            cursor="arrow",
            width=width_chars,
            height=min_height,
        )
        widget.configure(state="disabled")
        return widget

    def estimate_text_height(self, value, width_chars, min_height=3):
        lines = 0
        for paragraph in value.split("\n"):
            paragraph = paragraph.strip()
            if not paragraph:
                lines += 1
                continue
            words = paragraph.split()
            current = 0
            lines += 1
            for word in words:
                word_len = len(word) + 1
                if current + word_len > width_chars:
                    lines += 1
                    current = word_len
                else:
                    current += word_len
        return max(min_height, min(lines + 1, 24))

    def populate_glossary_text(self, widget, value, topic, bg, fg, width_chars, min_height=3):
        widget.configure(state="normal", bg=bg, fg=fg, cursor="arrow")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(height=self.estimate_text_height(value, width_chars, min_height=min_height))
        widget.configure(state="disabled")

    def show_topic(self, topic):
        self.current_topic = topic
        info = content_data.LEARN_TOPICS[topic]
        c = self.controller.colors
        self.topic_title.config(text=topic)
        self.topic_subtitle.config(text=info["subtitle"])
        self.progress_markers.config(text="Intro  →  Core idea  →  Example  →  Apply it")
        self.populate_glossary_text(self.topic_overview, info["overview"], topic, c["surface"], c["text"], width_chars=90, min_height=4)
        self.populate_glossary_text(self.real_life_text, info.get("real_life", info.get("why_it_matters", "")), topic, c["primary_soft"], c["text"], width_chars=40, min_height=4)

        key_terms = info.get("key_terms", [])
        if key_terms:
            detail_text = "\n\n".join([f"{idx + 1}. {term}" for idx, term in enumerate(key_terms)])
        else:
            detail_text = (
                f"1. {info.get('key_term', 'algorithm')}\n\n"
                f"2. {info.get('simple_example', 'A computing system follows a set of instructions to complete a task.')}\n\n"
                f"3. {info.get('common_mistake', 'A  is assuming the first idea is always the best one without testing it.')}\n\n"
                "4. Input — information that enters a system.\n\n"
                "5. Output — the result a system produces."
            )
        self.populate_glossary_text(self.detail_text, detail_text, topic, c["surface_alt"], c["text"], width_chars=40, min_height=9)
        self.populate_glossary_text(self.scenario_text, info.get("scenario", info.get("challenge", "")), topic, c["warning_soft"], c["text"], width_chars=40, min_height=6)
        self.populate_glossary_text(self.career_text, info.get("career_link", "Career link: software, digital, and technical roles all build on this topic."), topic, c["surface_dark"], c["text"], width_chars=40, min_height=4)
        deeper_value = info.get("deeper_dive", info.get("why_it_matters", info.get("overview", "")))
        self.populate_glossary_text(self.deeper_text, deeper_value, topic, c["surface"], c["text"], width_chars=40, min_height=8)

        for child in self.points_container.winfo_children():
            child.destroy()
        for point in info["key_points"]:
            row = tk.Frame(self.points_container, bg=c["surface"])
            row.pack(fill="x", pady=5)
            bullet = tk.Canvas(row, width=18, height=18, bg=c["surface"], highlightthickness=0)
            bullet.pack(side="left", anchor="n")
            bullet.create_oval(4, 4, 14, 14, fill=c["primary"], outline="")
            point_text = self.make_glossary_text_widget(row, bg=c["surface"], fg=c["muted"], font=self.controller.font(11), width_chars=62, min_height=2)
            point_text.pack(side="left", fill="x", expand=True, padx=(4, 0))
            self.populate_glossary_text(point_text, point, topic, c["surface"], c["muted"], width_chars=62, min_height=2)

        for key, btn in self.topic_buttons.items():
            btn.configure(bg=c["primary_soft"] if key == topic else c["surface_alt"])
        self.controller.mark_topic_viewed(topic)
        self.content_wrap.canvas.yview_moveto(0)

    def show_glossary_term(self, term):
        definition = content_data.GLOSSARY.get(term.lower(), "No definition available yet.")
        messagebox.showinfo(term.title(), definition)

    def filter_topics(self):
        for topic in self.topic_order:
            self.topic_buttons[topic].pack_forget()
        self.no_results_label.pack_forget()
        for topic in self.topic_order:
            self.topic_buttons[topic].pack(fill="x", padx=8, pady=4)

    def open_related(self):
        topic = self.current_topic
        if topic in ("Algorithms", "Programming", "Cybersecurity"):
            self.controller.show_frame("Play")
        else:
            self.controller.show_frame("Quiz")



class PlayPage(BasePage):
    page_name = "Play"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = controller.colors
        self.current_game = "builder"
        self.current_index = {key: 0 for key in content_data.PLAY_GAMES}
        self.current_steps = []
        self.current_attempts = 0
        self.selected_option = None
        self.answer_locked = False
        self.selected_game_buttons = {}
        self.builder_difficulty = tk.StringVar(value="Beginner")
        self.drag_index = None
        self.trace_job = None
        self.flow_selected_symbol = None
        self.flow_drag_widget = None
        self.binary_selected_left = None
        self.binary_selected_right = None
        self.binary_remaining = set()
        self.binary_timer_seconds = 0
        self.binary_timer_job = None
        self.logic_inputs = [0, 0]
        self.bug_selected_line = None
        self.bug_selected_fix = None
        self.phishing_found = set()
        self.phishing_verdict = None

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        ttk.Label(self, text="Play Lab", style="Title.TLabel").grid(row=0, column=0, sticky="w", padx=28, pady=(24, 12))

        hero = self.make_card(self, bg=c["surface"], padx=20, pady=16)
        hero.grid(row=1, column=0, sticky="ew", padx=28)
        hero.grid_columnconfigure(0, weight=2)
        hero.grid_columnconfigure(1, weight=1)
        tk.Label(hero, text="Practise through deeper interactive challenges", bg=c["surface"], fg=c["text"], font=controller.font(15, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(hero, text="Algorithm Builder uses drag ordering and trace animation, Flowchart Challenge uses drag-and-drop symbols, Binary Puzzle uses timed card matching, Logic Gate Mini Game uses live output switches, and the new bug-race and phishing modes feel more like investigations than quiz questions.", bg=c["surface"], fg=c["muted"], wraplength=760, justify="left", font=controller.font(10)).grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.progress_summary = tk.Label(hero, text="", bg=c["surface"], fg=c["text"], justify="left", font=controller.font(10))
        self.progress_summary.grid(row=0, column=1, rowspan=2, sticky="e")

        selector = tk.Frame(self, bg=c["bg"])
        selector.grid(row=2, column=0, sticky="ew", padx=28, pady=(14, 10))
        selector.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for idx, key in enumerate(content_data.PLAY_GAMES):
            game = content_data.PLAY_GAMES[key]
            btn = tk.Button(selector, text=f"{game['title']}\n{game['description']}", relief="flat", bd=0, justify="left", anchor="w", wraplength=250, padx=14, pady=14, font=controller.font(10, "bold"), command=lambda g=key: self.switch_game(g))
            row = idx // 4
            col = idx % 4
            btn.grid(row=row, column=col, sticky="ew", padx=4, pady=4)
            self.selected_game_buttons[key] = btn

        self.play_scroll = ScrollableFrame(self, bg=c["bg"], controller=controller)
        self.play_scroll.grid(row=3, column=0, sticky="nsew", padx=28, pady=(4, 24))
        body = self.play_scroll.inner
        body.configure(bg=c["bg"])
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        left = self.make_card(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(3, weight=1)
        self.game_title = tk.Label(left, text="", bg=c["surface"], fg=c["text"], font=controller.font(18, "bold"))
        self.game_title.grid(row=0, column=0, sticky="w")
        self.challenge_status = tk.Label(left, text="", bg=c["surface"], fg=c["muted"], font=controller.font(10))
        self.challenge_status.grid(row=1, column=0, sticky="w", pady=(4, 8))
        diff_row = tk.Frame(left, bg=c["surface"])
        diff_row.grid(row=2, column=0, sticky="w", pady=(0, 8))
        tk.Label(diff_row, text="Builder difficulty:", bg=c["surface"], fg=c["text"], font=controller.font(10, "bold")).grid(row=0, column=0, padx=(0, 8))
        self.diff_combo = ttk.Combobox(diff_row, state="readonly", values=["Beginner", "Intermediate", "Advanced"], textvariable=self.builder_difficulty, width=16)
        self.diff_combo.grid(row=0, column=1)
        self.diff_combo.bind("<<ComboboxSelected>>", lambda e: self.change_difficulty())
        self.builder_unlock_text = tk.Label(
            diff_row,
            text="",
            bg=c["surface"],
            fg=c["muted"],
            justify="left",
            wraplength=620,
            font=controller.font(9)
        )
        self.builder_unlock_text.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.reorder_frame = tk.Frame(left, bg=c["surface"])
        self.reorder_frame.grid(row=3, column=0, sticky="nsew")
        self.reorder_frame.grid_columnconfigure(0, weight=1)
        self.reorder_frame.grid_rowconfigure(1, weight=1)
        self.reorder_prompt = tk.Label(self.reorder_frame, text="", bg=c["surface"], fg=c["text"], wraplength=720, justify="left", font=controller.font(12, "bold"))
        self.reorder_prompt.grid(row=0, column=0, sticky="w")
        self.step_list = tk.Listbox(self.reorder_frame, font=controller.font(12), bd=0, highlightthickness=2, selectbackground=c["primary"], selectforeground="white", activestyle="none")
        self.step_list.grid(row=1, column=0, sticky="nsew", pady=(14, 14))
        self.step_list.bind("<Control-Up>", lambda e: self.move_up())
        self.step_list.bind("<Control-Down>", lambda e: self.move_down())
        self.step_list.bind("<ButtonPress-1>", self.start_step_drag)
        self.step_list.bind("<B1-Motion>", self.drag_step_motion)
        self.step_list.bind("<ButtonRelease-1>", self.end_step_drag)
        reorder_controls = tk.Frame(self.reorder_frame, bg=c["surface"])
        reorder_controls.grid(row=2, column=0, sticky="w")
        tk.Label(self.reorder_frame, text="Drag the steps into order, or use Move Up / Move Down for precision.", bg=c["surface"], fg=c["muted"], font=controller.font(9)).grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Button(reorder_controls, text="Move Up", style="Primary.TButton", command=self.move_up).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(reorder_controls, text="Move Down", style="Secondary.TButton", command=self.move_down).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(reorder_controls, text="Shuffle", style="Secondary.TButton", command=self.shuffle_steps).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(reorder_controls, text="Check", style="Primary.TButton", command=self.check_reorder).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(reorder_controls, text="Next", style="Secondary.TButton", command=self.next_challenge).grid(row=0, column=4)

        self.flowchart_frame = tk.Frame(left, bg=c["surface"])
        self.flowchart_frame.grid(row=3, column=0, sticky="nsew")
        self.flowchart_frame.grid_columnconfigure(0, weight=1)
        self.flowchart_prompt = tk.Label(self.flowchart_frame, text="", bg=c["surface"], fg=c["text"], wraplength=720, justify="left", font=controller.font(12, "bold"))
        self.flowchart_prompt.grid(row=0, column=0, sticky="w")
        self.flowchart_intro = tk.Label(self.flowchart_frame, text="", bg=c["surface"], fg=c["muted"], wraplength=720, justify="left", font=controller.font(10))
        self.flowchart_intro.grid(row=1, column=0, sticky="w", pady=(6, 10))
        self.flowchart_canvas = tk.Canvas(self.flowchart_frame, bg=c["surface"], highlightthickness=0, height=270)
        self.flowchart_canvas.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.flowchart_symbol_bar = tk.Frame(self.flowchart_frame, bg=c["surface"])
        self.flowchart_symbol_bar.grid(row=3, column=0, sticky="w")
        flow_controls = tk.Frame(self.flowchart_frame, bg=c["surface"])
        flow_controls.grid(row=4, column=0, sticky="w", pady=(12, 0))
        ttk.Button(flow_controls, text="Reset", style="Secondary.TButton", command=self.load_flowchart).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(flow_controls, text="Check", style="Primary.TButton", command=self.check_flowchart).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(flow_controls, text="Next", style="Secondary.TButton", command=self.next_challenge).grid(row=0, column=2)

        self.binary_frame = tk.Frame(left, bg=c["surface"])
        self.binary_frame.grid(row=3, column=0, sticky="nsew")
        self.binary_frame.grid_columnconfigure((0, 1), weight=1)
        self.binary_prompt = tk.Label(self.binary_frame, text="", bg=c["surface"], fg=c["text"], wraplength=720, justify="left", font=controller.font(12, "bold"))
        self.binary_prompt.grid(row=0, column=0, sticky="w")
        self.binary_timer_label = tk.Label(self.binary_frame, text="", bg=c["surface"], fg=c["danger"], font=controller.font(11, "bold"))
        self.binary_timer_label.grid(row=0, column=1, sticky="e")
        self.binary_intro = tk.Label(self.binary_frame, text="", bg=c["surface"], fg=c["muted"], wraplength=720, justify="left", font=controller.font(10))
        self.binary_intro.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 10))
        self.binary_left = tk.Frame(self.binary_frame, bg=c["surface"])
        self.binary_left.grid(row=2, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        self.binary_right = tk.Frame(self.binary_frame, bg=c["surface"])
        self.binary_right.grid(row=2, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        self.binary_status = tk.Label(self.binary_frame, text="", bg=c["surface"], fg=c["muted"], font=controller.font(10))
        self.binary_status.grid(row=3, column=0, columnspan=2, sticky="w")
        binary_controls = tk.Frame(self.binary_frame, bg=c["surface"])
        binary_controls.grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Button(binary_controls, text="Reset round", style="Secondary.TButton", command=self.load_binary).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(binary_controls, text="Next", style="Secondary.TButton", command=self.next_challenge).grid(row=0, column=1)

        self.logic_frame = tk.Frame(left, bg=c["surface"])
        self.logic_frame.grid(row=3, column=0, sticky="nsew")
        self.logic_frame.grid_columnconfigure(0, weight=1)
        self.logic_prompt = tk.Label(self.logic_frame, text="", bg=c["surface"], fg=c["text"], wraplength=720, justify="left", font=controller.font(12, "bold"))
        self.logic_prompt.grid(row=0, column=0, sticky="w")
        self.logic_gate_label = tk.Label(self.logic_frame, text="", bg=c["surface"], fg=c["primary_dark"], font=controller.font(14, "bold"))
        self.logic_gate_label.grid(row=1, column=0, sticky="w", pady=(6, 10))
        self.logic_switch_wrap = tk.Frame(self.logic_frame, bg=c["surface"])
        self.logic_switch_wrap.grid(row=2, column=0, sticky="w", pady=(0, 10))
        self.logic_switch_a = tk.Button(self.logic_switch_wrap, text="Input A: 0", relief="flat", bd=0, bg=c["surface_alt"], fg=c["text"], font=controller.font(11, "bold"), padx=16, pady=12, command=lambda: self.toggle_logic_input(0))
        self.logic_switch_a.grid(row=0, column=0, padx=(0, 8))
        self.logic_switch_b = tk.Button(self.logic_switch_wrap, text="Input B: 0", relief="flat", bd=0, bg=c["surface_alt"], fg=c["text"], font=controller.font(11, "bold"), padx=16, pady=12, command=lambda: self.toggle_logic_input(1))
        self.logic_switch_b.grid(row=0, column=1, padx=(0, 8))
        self.logic_lamp = tk.Canvas(self.logic_frame, width=180, height=110, bg=c["surface"], highlightthickness=0)
        self.logic_lamp.grid(row=3, column=0, sticky="w", pady=(6, 8))
        logic_controls = tk.Frame(self.logic_frame, bg=c["surface"])
        logic_controls.grid(row=4, column=0, sticky="w", pady=(12, 0))
        ttk.Button(logic_controls, text="Check lamp", style="Primary.TButton", command=self.check_logic_game).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(logic_controls, text="Next", style="Secondary.TButton", command=self.next_challenge).grid(row=0, column=1)

        self.bug_frame = tk.Frame(left, bg=c["surface"])
        self.bug_frame.grid(row=3, column=0, sticky="nsew")
        self.bug_frame.grid_columnconfigure(0, weight=1)
        self.bug_prompt = tk.Label(self.bug_frame, text="", bg=c["surface"], fg=c["text"], wraplength=720, justify="left", font=controller.font(12, "bold"))
        self.bug_prompt.grid(row=0, column=0, sticky="w")
        self.bug_lines_wrap = tk.Frame(self.bug_frame, bg=c["surface"])
        self.bug_lines_wrap.grid(row=1, column=0, sticky="ew", pady=(10, 10))
        self.bug_fix_wrap = tk.Frame(self.bug_frame, bg=c["surface"])
        self.bug_fix_wrap.grid(row=2, column=0, sticky="ew")
        self.bug_fix_buttons = []
        bug_controls = tk.Frame(self.bug_frame, bg=c["surface"])
        bug_controls.grid(row=3, column=0, sticky="w", pady=(12, 0))
        ttk.Button(bug_controls, text="Submit fix", style="Primary.TButton", command=self.check_buggage).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(bug_controls, text="Next", style="Secondary.TButton", command=self.next_challenge).grid(row=0, column=1)

        self.phishing_frame = tk.Frame(left, bg=c["surface"])
        self.phishing_frame.grid(row=3, column=0, sticky="nsew")
        self.phishing_frame.grid_columnconfigure(0, weight=1)
        self.phishing_prompt = tk.Label(self.phishing_frame, text="", bg=c["surface"], fg=c["text"], wraplength=720, justify="left", font=controller.font(12, "bold"))
        self.phishing_prompt.grid(row=0, column=0, sticky="w")
        self.inbox_card = tk.Frame(self.phishing_frame, bg=c["code"], padx=14, pady=14)
        self.inbox_card.grid(row=1, column=0, sticky="ew", pady=(10, 10))
        self.email_sender = tk.Label(self.inbox_card, text="", bg=c["code"], fg=c["text"], justify="left", anchor="w", font=controller.font(10, "bold"))
        self.email_sender.pack(anchor="w")
        self.email_subject = tk.Label(self.inbox_card, text="", bg=c["code"], fg=c["text"], justify="left", anchor="w", font=controller.font(10))
        self.email_subject.pack(anchor="w", pady=(4, 4))
        self.email_body = tk.Label(self.inbox_card, text="", bg=c["code"], fg=c["text"], justify="left", anchor="w", wraplength=680, font=controller.font(10))
        self.email_body.pack(anchor="w", pady=(4, 0))
        self.phishing_clue_wrap = tk.Frame(self.phishing_frame, bg=c["surface"])
        self.phishing_clue_wrap.grid(row=2, column=0, sticky="ew")
        self.phishing_verdict_wrap = tk.Frame(self.phishing_frame, bg=c["surface"])
        self.phishing_verdict_wrap.grid(row=3, column=0, sticky="w", pady=(12, 0))
        self.safe_btn = tk.Button(self.phishing_verdict_wrap, text="Mark as Safe", relief="flat", bd=0, bg=c["surface_alt"], fg=c["text"], font=controller.font(11, "bold"), padx=16, pady=12, command=lambda: self.set_phishing_verdict("Safe"))
        self.safe_btn.grid(row=0, column=0, padx=(0, 8))
        self.unsafe_btn = tk.Button(self.phishing_verdict_wrap, text="Mark as Unsafe", relief="flat", bd=0, bg=c["surface_alt"], fg=c["text"], font=controller.font(11, "bold"), padx=16, pady=12, command=lambda: self.set_phishing_verdict("Unsafe"))
        self.unsafe_btn.grid(row=0, column=1, padx=(0, 8))
        ttk.Button(self.phishing_verdict_wrap, text="Submit", style="Primary.TButton", command=self.check_phishing).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(self.phishing_verdict_wrap, text="Next", style="Secondary.TButton", command=self.next_challenge).grid(row=0, column=3)

        self.choice_frame = tk.Frame(left, bg=c["surface"])
        self.choice_frame.grid(row=3, column=0, sticky="nsew")
        self.choice_frame.grid_columnconfigure(0, weight=1)
        self.choice_frame.grid_rowconfigure(3, weight=1)
        self.choice_prompt = tk.Label(self.choice_frame, text="", bg=c["surface"], fg=c["text"], wraplength=720, justify="left", font=controller.font(12, "bold"))
        self.choice_prompt.grid(row=0, column=0, sticky="w")
        self.code_box = tk.Label(self.choice_frame, text="", bg=c["code"], fg=c["text"], justify="left", anchor="w", font=("Consolas", max(9, int(11 * controller.scale))), padx=14, pady=14)
        self.code_box.grid(row=1, column=0, sticky="ew", pady=(12, 12))
        self.option_buttons = []
        options_wrap = tk.Frame(self.choice_frame, bg=c["surface"])
        options_wrap.grid(row=2, column=0, sticky="ew")
        options_wrap.grid_columnconfigure(0, weight=1)
        for idx in range(4):
            btn = tk.Button(options_wrap, text="", relief="flat", bd=0, bg=c["surface_alt"], activebackground=c["primary_soft"], fg=c["text"], justify="left", anchor="w", wraplength=680, font=controller.font(11), padx=16, pady=14, command=lambda i=idx: self.select_choice(i))
            btn.grid(row=idx, column=0, sticky="ew", pady=5)
            self.option_buttons.append(btn)
        choice_controls = tk.Frame(self.choice_frame, bg=c["surface"])
        choice_controls.grid(row=3, column=0, sticky="w", pady=(16, 0))
        ttk.Button(choice_controls, text="Submit", style="Primary.TButton", command=self.check_choice).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(choice_controls, text="Hint", style="Secondary.TButton", command=self.show_hint).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(choice_controls, text="Next", style="Secondary.TButton", command=self.next_challenge).grid(row=0, column=2)

        right = tk.Frame(body, bg=c["bg"])
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right.grid_columnconfigure(0, weight=1)
        self.feedback_card = self.make_card(right, bg=c["primary_soft"])
        self.feedback_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(self.feedback_card, text="Smart feedback", bg=c["primary_soft"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.feedback_text = tk.Label(self.feedback_card, text="Choose a play mode to begin.", bg=c["primary_soft"], fg=c["text"], wraplength=420, justify="left", font=controller.font(10))
        self.feedback_text.pack(anchor="w", pady=(10, 0))
        self.trace_card = self.make_card(right)
        self.trace_card.grid(row=1, column=0, sticky="ew", pady=8)
        tk.Label(self.trace_card, text="Trace / worked solution", bg=c["surface"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.trace_text = tk.Label(self.trace_card, text="Correct builder answers animate a trace here.", bg=c["surface"], fg=c["muted"], wraplength=420, justify="left", font=controller.font(10))
        self.trace_text.pack(anchor="w", pady=(10, 0))
        self.progress_card = self.make_card(right, bg=c["success_soft"])
        self.progress_card.grid(row=2, column=0, sticky="ew", pady=8)
        tk.Label(self.progress_card, text="Progress & difficulty unlocks", bg=c["success_soft"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.mode_progress_text = tk.Label(self.progress_card, text="", bg=c["success_soft"], fg=c["text"], wraplength=420, justify="left", font=controller.font(10))
        self.mode_progress_text.pack(anchor="w", pady=(10, 0))
        self.bind_all("<Key-1>", self._choice_key)
        self.bind_all("<Key-2>", self._choice_key)
        self.bind_all("<Key-3>", self._choice_key)
        self.bind_all("<Key-4>", self._choice_key)
        self.bind_all("<Return>", self._return_action)
        self.switch_game(self.current_game)

    def _choice_key(self, event):
        if self.controller.active_page != "Play" or content_data.PLAY_GAMES[self.current_game]["type"] != "choice":
            return
        idx = int(event.keysym) - 1
        if 0 <= idx < 4:
            self.select_choice(idx)

    def _return_action(self, event):
        if self.controller.active_page != "Play":
            return
        mode = content_data.PLAY_GAMES[self.current_game]["type"]
        if mode == "reorder":
            self.check_reorder()
        elif mode == "flowchart":
            self.check_flowchart()
        elif mode == "logic":
            self.check_logic_game()
        else:
            self.check_choice()

    def unlocked_builder_levels(self):
        completed = len(self.controller.state_data["play_state"]["builder"]["completed"])
        levels = ["Beginner"]
        if completed >= 1:
            levels.append("Intermediate")
        if completed >= 3:
            levels.append("Advanced")
        return levels

    def refresh_builder_unlock_text(self):
        completed = len(self.controller.state_data["play_state"]["builder"]["completed"])
        unlocked = self.unlocked_builder_levels()
        intermediate_status = "Unlocked" if "Intermediate" in unlocked else f"Locked — complete {max(0, 1 - completed)} more Builder challenge"
        advanced_status = "Unlocked" if "Advanced" in unlocked else f"Locked — complete {max(0, 3 - completed)} more Builder challenges"
        self.builder_unlock_text.config(
            text=(
                f"Builder progression: {completed} challenge(s) completed.\n"
                f"Intermediate: {intermediate_status}.\n"
                f"Advanced: {advanced_status}."
            )
        )

    def change_difficulty(self):
        if self.current_game == "builder":
            requested = self.builder_difficulty.get()
            unlocked = self.unlocked_builder_levels()
            if requested not in unlocked:
                completed = len(self.controller.state_data["play_state"]["builder"]["completed"])
                if requested == "Intermediate":
                    messagebox.showinfo(
                        "Intermediate locked",
                        f"Complete 1 Builder challenge to unlock Intermediate. You have completed {completed} so far."
                    )
                elif requested == "Advanced":
                    messagebox.showinfo(
                        "Advanced locked",
                        f"Complete 3 Builder challenges to unlock Advanced. You have completed {completed} so far."
                    )
                self.builder_difficulty.set(unlocked[-1])
            self.current_index["builder"] = 0
            self.refresh_builder_unlock_text()
            self.load_current_challenge(reset_feedback=True)

    def switch_game(self, game_key):
        if game_key not in self.controller.state_data.get("unlocked_games", ["builder"]):
            messagebox.showinfo("Locked for now", "View more Learn topics first to unlock this game mode.")
            return
        self.current_game = game_key
        self.current_attempts = 0
        self.selected_option = None
        self.answer_locked = False
        c = self.controller.colors
        for key, btn in self.selected_game_buttons.items():
            btn.configure(bg=c["primary_soft"] if key == game_key else c["surface"], fg=c["text"], activebackground=c["primary_soft"])
        self.diff_combo.configure(state="readonly" if game_key == "builder" else "disabled")
        if self.builder_difficulty.get() not in self.unlocked_builder_levels():
            self.builder_difficulty.set(self.unlocked_builder_levels()[-1])
        self.refresh_builder_unlock_text()
        self.load_current_challenge(reset_feedback=True)
        self.refresh_mode_progress()

    def game_record(self):
        return self.controller.state_data["play_state"][self.current_game]

    def available_challenges(self):
        game = content_data.PLAY_GAMES[self.current_game]
        if self.current_game == "builder":
            return [c for c in game["challenges"] if c.get("difficulty", "Beginner") == self.builder_difficulty.get()]
        return game["challenges"]

    def current_challenge(self):
        challenges = self.available_challenges()
        if not challenges:
            return None
        idx = self.current_index[self.current_game] % len(challenges)
        return challenges[idx]

    def load_current_challenge(self, reset_feedback=False):
        if self.trace_job:
            try:
                self.after_cancel(self.trace_job)
            except Exception:
                pass
            self.trace_job = None
        if self.binary_timer_job:
            try:
                self.after_cancel(self.binary_timer_job)
            except Exception:
                pass
            self.binary_timer_job = None
        challenge = self.current_challenge()
        game = content_data.PLAY_GAMES[self.current_game]
        if challenge is None:
            self.set_feedback("This Builder difficulty is still locked. Complete more Builder challenges to unlock it.", mode="warning")
            return
        label = f"{challenge['title']}" + (f" • {challenge.get('difficulty')}" if self.current_game == 'builder' else "")
        self.game_title.config(text=game["title"])
        self.challenge_status.config(text=f"Challenge {self.current_index[self.current_game] + 1} of {len(self.available_challenges())}: {label}")
        if game["type"] == "reorder":
            self.choice_frame.grid_remove()
            self.flowchart_frame.grid_remove()
            self.binary_frame.grid_remove()
            self.logic_frame.grid_remove()
            self.bug_frame.grid_remove()
            self.phishing_frame.grid_remove()
            self.reorder_frame.grid()
            self.reorder_prompt.config(text=challenge["prompt"])
            self.shuffle_steps()
            self.trace_text.config(text="Correct builder answers animate a trace here.")
        elif game["type"] == "flowchart":
            self.choice_frame.grid_remove()
            self.reorder_frame.grid_remove()
            self.binary_frame.grid_remove()
            self.logic_frame.grid_remove()
            self.bug_frame.grid_remove()
            self.phishing_frame.grid_remove()
            self.flowchart_frame.grid()
            self.load_flowchart()
            self.trace_text.config(text="Correct flowchart solutions appear here.")
        elif game["type"] == "binary":
            self.choice_frame.grid_remove()
            self.reorder_frame.grid_remove()
            self.flowchart_frame.grid_remove()
            self.logic_frame.grid_remove()
            self.bug_frame.grid_remove()
            self.phishing_frame.grid_remove()
            self.binary_frame.grid()
            self.load_binary()
            self.trace_text.config(text="Successful binary rounds are explained here.")
        elif game["type"] == "logic":
            self.choice_frame.grid_remove()
            self.reorder_frame.grid_remove()
            self.flowchart_frame.grid_remove()
            self.binary_frame.grid_remove()
            self.bug_frame.grid_remove()
            self.phishing_frame.grid_remove()
            self.logic_frame.grid()
            self.load_logic_game()
            self.trace_text.config(text="Logic gate explanations appear here after you check the lamp.")
        elif game["type"] == "bugrace":
            self.choice_frame.grid_remove()
            self.reorder_frame.grid_remove()
            self.flowchart_frame.grid_remove()
            self.binary_frame.grid_remove()
            self.logic_frame.grid_remove()
            self.phishing_frame.grid_remove()
            self.bug_frame.grid()
            self.load_bug_challenge()
            self.trace_text.config(text="Bug explanations appear here after you submit the fix.")
        elif game["type"] == "phishing":
            self.choice_frame.grid_remove()
            self.reorder_frame.grid_remove()
            self.flowchart_frame.grid_remove()
            self.binary_frame.grid_remove()
            self.logic_frame.grid_remove()
            self.bug_frame.grid_remove()
            self.phishing_frame.grid()
            self.load_phishing_challenge()
            self.trace_text.config(text="Email safety explanations appear here after you submit the verdict.")
        else:
            self.reorder_frame.grid_remove()
            self.flowchart_frame.grid_remove()
            self.binary_frame.grid_remove()
            self.logic_frame.grid_remove()
            self.bug_frame.grid_remove()
            self.phishing_frame.grid_remove()
            self.choice_frame.grid()
            self.choice_prompt.config(text=challenge["prompt"])
            self.code_box.config(text=challenge.get("code", ""))
            self.selected_option = None
            self.answer_locked = False
            for idx, option in enumerate(challenge["options"]):
                self.option_buttons[idx].config(text=f"{idx + 1}. {option}", state="normal", bg=self.controller.colors["surface_alt"])
        if reset_feedback:
            self.set_feedback("Choose a response, then submit for attempt-aware coaching.", mode="neutral")
        self.refresh_mode_progress()

    def set_feedback(self, text, mode="neutral"):
        c = self.controller.colors
        bg = c["primary_soft"]
        if mode == "success":
            bg = c["success_soft"]
        elif mode == "danger":
            bg = c["danger_soft"]
        elif mode == "warning":
            bg = c["warning_soft"]
        self.feedback_card.configure(bg=bg)
        for child in self.feedback_card.winfo_children():
            child.configure(bg=bg)
        self.feedback_text.config(text=text)

    def refresh_mode_progress(self):
        record = self.game_record()
        total = len(content_data.PLAY_GAMES[self.current_game]["challenges"])
        stars = sum(int(v) for v in record.get("stars", {}).values())
        unlocked_text = ", ".join(self.controller.state_data.get("unlocked_games", []))
        builder_completed = len(self.controller.state_data["play_state"]["builder"]["completed"])
        self.progress_summary.config(
            text=(
                f"Total play progress: {self.controller.total_play_completed()}/{self.controller.total_play_challenges()}\n"
                f"Unlocked modes: {unlocked_text}\n"
                f"Builder challenges completed: {builder_completed}"
            )
        )
        level_text = ", ".join(self.unlocked_builder_levels())
        self.mode_progress_text.config(text=(f"Completed in this mode: {len(record.get('completed', []))}/{total}\nAttempts recorded: {record.get('attempts', 0)}\nStars collected: {stars}\nUnlocked builder levels: {level_text}\nIntermediate unlocks after 1 Builder challenge.\nAdvanced unlocks after 3 Builder challenges.\n3 stars = first try, 2 stars = second try, 1 star = after support"))
        self.refresh_builder_unlock_text()

    def start_step_drag(self, event):
        if self.current_game != "builder":
            return
        self.drag_index = self.step_list.nearest(event.y)
        if self.drag_index is not None and self.step_list.size() > 0:
            self.step_list.selection_clear(0, tk.END)
            self.step_list.selection_set(self.drag_index)

    def drag_step_motion(self, event):
        if self.current_game != "builder" or self.drag_index is None:
            return
        new_index = self.step_list.nearest(event.y)
        if new_index == self.drag_index or new_index < 0 or new_index >= len(self.current_steps):
            return
        item = self.current_steps.pop(self.drag_index)
        self.current_steps.insert(new_index, item)
        self.drag_index = new_index
        self._render_steps()
        self.step_list.selection_set(new_index)

    def end_step_drag(self, event):
        self.drag_index = None

    def animate_trace(self, lines, index=0, built=""):
        if index >= len(lines):
            self.trace_job = None
            return
        built = built + (("\n" if built else "") + lines[index])
        self.trace_text.config(text=built)
        self.trace_job = self.after(180, lambda: self.animate_trace(lines, index + 1, built))

    def shuffle_steps(self):
        challenge = self.current_challenge()
        self.current_steps = challenge["steps"][:]
        random.shuffle(self.current_steps)
        while self.current_steps == challenge["answer"]:
            random.shuffle(self.current_steps)
        self.current_attempts = 0
        self._render_steps()

    def _render_steps(self):
        self.step_list.delete(0, tk.END)
        for idx, step in enumerate(self.current_steps, start=1):
            self.step_list.insert(tk.END, f"{idx}. {step}")
        if self.current_steps:
            self.step_list.selection_clear(0, tk.END)
            self.step_list.selection_set(0)

    def _selected_index(self):
        selection = self.step_list.curselection()
        if not selection:
            messagebox.showinfo("Select a step", "Choose a step first.")
            return None
        return selection[0]

    def move_up(self):
        idx = self._selected_index()
        if idx is None or idx == 0:
            return
        self.current_steps[idx - 1], self.current_steps[idx] = self.current_steps[idx], self.current_steps[idx - 1]
        self._render_steps()
        self.step_list.selection_set(idx - 1)

    def move_down(self):
        idx = self._selected_index()
        if idx is None or idx == len(self.current_steps) - 1:
            return
        self.current_steps[idx + 1], self.current_steps[idx] = self.current_steps[idx], self.current_steps[idx + 1]
        self._render_steps()
        self.step_list.selection_set(idx + 1)


    def load_flowchart(self):
        c = self.controller.colors
        challenge = self.current_challenge()
        self.flow_selected_symbol = None
        self.flow_drag_widget = None
        self.binary_selected_left = None
        self.binary_selected_right = None
        self.binary_remaining = set()
        self.binary_timer_seconds = 0
        self.binary_timer_job = None
        self.logic_inputs = [0, 0]
        self.bug_selected_line = None
        self.bug_selected_fix = None
        self.phishing_found = set()
        self.phishing_verdict = None
        self.flowchart_prompt.config(text=challenge["prompt"])
        self.flowchart_intro.config(text=challenge.get("intro", ""))
        self.flowchart_canvas.delete("all")

        self.flowchart_canvas.create_rectangle(305, 10, 415, 50, fill=c["surface_alt"], outline=c["primary"], width=2)
        self.flowchart_canvas.create_text(360, 30, text="Start", fill=c["text"], font=self.controller.font(10, "bold"))
        self.flowchart_canvas.create_line(360, 50, 360, 80, fill=c["muted"], width=2, arrow=tk.LAST)

        self.flowchart_canvas.create_rectangle(250, 90, 470, 140, fill="", outline=c["warning"], width=3, dash=(6, 4), tags="drop_zone")
        self.flowchart_canvas.create_text(360, 115, text="Drag missing symbol here", fill=c["muted"], font=self.controller.font(10), tags="drop_text")

        self.flowchart_canvas.create_line(360, 140, 360, 170, fill=c["muted"], width=2)
        self.flowchart_canvas.create_line(250, 115, 165, 115, fill=c["success"], width=3)
        self.flowchart_canvas.create_line(470, 115, 555, 115, fill=c["danger"], width=3)

        self.flowchart_canvas.create_line(165, 115, 165, 170, fill=c["success"], width=3)
        self.flowchart_canvas.create_line(555, 115, 555, 170, fill=c["danger"], width=3)

        self.flowchart_canvas.create_rectangle(95, 180, 235, 220, fill=c["success_soft"], outline=c["success"], width=2)
        self.flowchart_canvas.create_rectangle(485, 180, 625, 220, fill=c["danger_soft"], outline=c["danger"], width=2)
        self.flowchart_canvas.create_text(165, 200, text=challenge.get("yes_label", "Yes"), fill=c["text"], font=self.controller.font(9, "bold"))
        if challenge.get("no_label"):
            self.flowchart_canvas.create_text(555, 200, text=challenge.get("no_label", "No"), fill=c["text"], font=self.controller.font(9, "bold"))
        self.flowchart_canvas.create_text(145, 95, text="YES", fill=c["success"], font=self.controller.font(9, "bold"))
        if challenge.get("no_label"):
            self.flowchart_canvas.create_text(575, 95, text="NO", fill=c["danger"], font=self.controller.font(9, "bold"))

        for child in self.flowchart_symbol_bar.winfo_children():
            child.destroy()

        for symbol in challenge["symbols"]:
            lbl = tk.Label(
                self.flowchart_symbol_bar,
                text=symbol,
                bg=c["surface_alt"],
                fg=c["text"],
                relief="raised",
                bd=1,
                padx=14,
                pady=10,
                font=self.controller.font(10, "bold"),
            )
            lbl.pack(side="left", padx=(0, 8), pady=4)
            lbl.bind("<ButtonPress-1>", self.start_flow_drag)
            lbl.bind("<B1-Motion>", self.drag_flow_symbol)
            lbl.bind("<ButtonRelease-1>", self.end_flow_drag)

    def start_flow_drag(self, event):
        self.flow_drag_widget = event.widget
        event.widget.configure(relief="sunken")

    def drag_flow_symbol(self, event):
        if self.flow_drag_widget is not event.widget:
            return

    def end_flow_drag(self, event):
        if self.flow_drag_widget is None:
            return
        widget = self.flow_drag_widget
        widget.configure(relief="raised")
        canvas = self.flowchart_canvas
        x = canvas.winfo_pointerx() - canvas.winfo_rootx()
        y = canvas.winfo_pointery() - canvas.winfo_rooty()
        if 250 <= x <= 470 and 90 <= y <= 140:
            challenge = self.current_challenge()
            self.flow_selected_symbol = widget.cget("text")
            canvas.delete("placed_symbol")
            canvas.create_rectangle(250, 90, 470, 140, fill=self.controller.colors["primary_soft"], outline=self.controller.colors["primary"], width=3, tags="placed_symbol")
            canvas.create_text(360, 108, text=self.flow_selected_symbol, fill=self.controller.colors["text"], font=self.controller.font(10, "bold"), tags="placed_symbol")
            canvas.create_text(360, 126, text=challenge["center_text"], fill=self.controller.colors["text"], font=self.controller.font(9), tags="placed_symbol")
            self.set_feedback(f"You placed '{self.flow_selected_symbol}'. Check whether it fits this flowchart.", mode="neutral")
        self.flow_drag_widget = None

    def check_flowchart(self):
        challenge = self.current_challenge()
        if not self.flow_selected_symbol:
            messagebox.showinfo("Place a symbol", "Drag a symbol into the missing slot first.")
            return
        self.current_attempts += 1
        self.controller.increment_play_attempt(self.current_game)
        if self.flow_selected_symbol == challenge["correct_symbol"]:
            stars = self._star_value(self.current_attempts)
            self.controller.update_play_record(self.current_game, challenge["id"], stars, topic="Algorithms")
            self.trace_text.config(text=f"Placed symbol: {self.flow_selected_symbol}\n\n{challenge['explanation']}")
            self.set_feedback(f"Correct. You placed the right symbol and connected the branches visually. You earned {stars} star(s).", mode="success")
        else:
            self.set_feedback(f"That symbol does not fit this point in the flowchart. {challenge['hint']}", mode="danger")
            self.trace_text.config(text="Think about whether this stage needs a decision or a process.")
        self.refresh_mode_progress()


    def load_binary(self):
        c = self.controller.colors
        challenge = self.current_challenge()
        self.binary_prompt.config(text=challenge["prompt"])
        self.binary_intro.config(text="Select one binary card and one decimal card to make a match. Clear every pair before the timer ends.")
        self.binary_selected_left = None
        self.binary_selected_right = None
        self.binary_remaining = set(tuple(pair) for pair in challenge["pairs"])

        for child in self.binary_left.winfo_children():
            child.destroy()
        for child in self.binary_right.winfo_children():
            child.destroy()

        binaries = [pair[0] for pair in challenge["pairs"]]
        decimals = [pair[1] for pair in challenge["pairs"]]
        random.shuffle(binaries)
        random.shuffle(decimals)

        for value in binaries:
            btn = tk.Button(self.binary_left, text=value, relief="flat", bd=0, bg=c["surface_alt"], fg=c["text"], font=self.controller.font(12, "bold"), padx=16, pady=12, command=lambda v=value: self.select_binary_left(v))
            btn.pack(fill="x", pady=4)

        for value in decimals:
            btn = tk.Button(self.binary_right, text=value, relief="flat", bd=0, bg=c["surface_alt"], fg=c["text"], font=self.controller.font(12, "bold"), padx=16, pady=12, command=lambda v=value: self.select_binary_right(v))
            btn.pack(fill="x", pady=4)

        self.binary_timer_seconds = int(challenge.get("time_limit", 45))
        self.update_binary_timer()
        self.binary_status.config(text=f"Matches remaining: {len(self.binary_remaining)}")

    def update_binary_timer(self):
        self.binary_timer_label.config(text=f"Time left: {self.binary_timer_seconds}s")
        if self.binary_timer_seconds <= 0:
            self.binary_timer_job = None
            self.set_feedback("Time is up for this Build the Byte round. Reset the round or move to the next one.", mode="danger")
            return
        self.binary_timer_seconds -= 1
        self.binary_timer_job = self.after(1000, self.update_binary_timer)

    def select_binary_left(self, value):
        self.binary_selected_left = value
        c = self.controller.colors
        for child in self.binary_left.winfo_children():
            child.configure(bg=c["primary_soft"] if child.cget("text") == value and child.cget("state") != "disabled" else c["surface_alt"] if child.cget("state") != "disabled" else c["success_soft"])
        self.try_binary_match()

    def select_binary_right(self, value):
        self.binary_selected_right = value
        c = self.controller.colors
        for child in self.binary_right.winfo_children():
            child.configure(bg=c["primary_soft"] if child.cget("text") == value and child.cget("state") != "disabled" else c["surface_alt"] if child.cget("state") != "disabled" else c["success_soft"])
        self.try_binary_match()

    def try_binary_match(self):
        if self.binary_selected_left is None or self.binary_selected_right is None:
            return
        pair = (self.binary_selected_left, self.binary_selected_right)
        self.current_attempts += 1
        self.controller.increment_play_attempt(self.current_game)
        c = self.controller.colors

        if pair in self.binary_remaining:
            self.binary_remaining.remove(pair)
            for child in self.binary_left.winfo_children():
                if child.cget("text") == self.binary_selected_left:
                    child.configure(bg=c["success_soft"], state="disabled")
            for child in self.binary_right.winfo_children():
                if child.cget("text") == self.binary_selected_right:
                    child.configure(bg=c["success_soft"], state="disabled")
            self.set_feedback("Correct match. Keep building the byte before the timer runs out.", mode="success")
        else:
            self.set_feedback("That pair does not match. Try another binary and decimal card.", mode="danger")
            for child in self.binary_left.winfo_children():
                if child.cget("state") != "disabled":
                    child.configure(bg=c["surface_alt"])
            for child in self.binary_right.winfo_children():
                if child.cget("state") != "disabled":
                    child.configure(bg=c["surface_alt"])

        self.binary_selected_left = None
        self.binary_selected_right = None
        self.binary_status.config(text=f"Matches remaining: {len(self.binary_remaining)}")

        if not self.binary_remaining:
            if self.binary_timer_job:
                try:
                    self.after_cancel(self.binary_timer_job)
                except Exception:
                    pass
                self.binary_timer_job = None
            challenge = self.current_challenge()
            stars = 3 if self.binary_timer_seconds >= 20 else 2 if self.binary_timer_seconds >= 8 else 1
            self.controller.update_play_record(self.current_game, challenge["id"], stars, topic="Programming")
            self.trace_text.config(text=challenge["explanation"])
            self.set_feedback(f"Round complete. You matched every card and earned {stars} star(s).", mode="success")
        self.refresh_mode_progress()


    def load_logic_game(self):
        challenge = self.current_challenge()
        self.logic_prompt.config(text=challenge["prompt"])
        self.logic_gate_label.config(text=f"Gate: {challenge['gate']}  |  Target output: {challenge['target']}")
        self.logic_inputs = [0, 0]
        self.bug_selected_line = None
        self.bug_selected_fix = None
        self.phishing_found = set()
        self.phishing_verdict = None
        self.update_logic_ui()

    def toggle_logic_input(self, index):
        challenge = self.current_challenge()
        if challenge["gate"] == "NOT" and index == 1:
            return
        self.logic_inputs[index] = 0 if self.logic_inputs[index] else 1
        self.update_logic_ui()

    def current_logic_output(self):
        challenge = self.current_challenge()
        gate = challenge["gate"]
        a, b = self.logic_inputs
        if gate == "AND":
            return 1 if a == 1 and b == 1 else 0
        if gate == "OR":
            return 1 if a == 1 or b == 1 else 0
        return 0 if a == 1 else 1

    def update_logic_ui(self):
        c = self.controller.colors
        challenge = self.current_challenge()
        self.logic_switch_a.configure(text=f"Input A: {self.logic_inputs[0]}", bg=c["primary_soft"] if self.logic_inputs[0] else c["surface_alt"])
        if challenge["gate"] == "NOT":
            self.logic_switch_b.configure(text="Input B: n/a", state="disabled", bg=c["surface_dark"])
        else:
            self.logic_switch_b.configure(text=f"Input B: {self.logic_inputs[1]}", state="normal", bg=c["primary_soft"] if self.logic_inputs[1] else c["surface_alt"])
        output = self.current_logic_output()
        lamp_color = c["warning"] if output == 1 else c["surface_dark"]
        self.logic_lamp.delete("all")
        self.logic_lamp.create_text(90, 16, text=f"Current output: {output}", fill=c["text"], font=self.controller.font(10, "bold"))
        self.logic_lamp.create_oval(45, 28, 135, 98, fill=lamp_color, outline=c["border"], width=2)
        self.logic_lamp.create_text(90, 63, text="LAMP", fill="white" if output == 1 else c["muted"], font=self.controller.font(11, "bold"))

    def check_logic_game(self):
        challenge = self.current_challenge()
        self.current_attempts += 1
        self.controller.increment_play_attempt(self.current_game)
        output = self.current_logic_output()
        if output == challenge["target"]:
            stars = self._star_value(self.current_attempts)
            self.controller.update_play_record(self.current_game, challenge["id"], stars, topic="Computational Thinking")
            self.trace_text.config(text=challenge["explanation"])
            self.set_feedback(f"Correct. You set the switches to produce the target output and earned {stars} star(s).", mode="success")
        else:
            self.set_feedback(f"The lamp is showing {output}, not {challenge['target']}. {challenge['hint']}", mode="danger")
        self.refresh_mode_progress()


    def load_bug_challenge(self):
        c = self.controller.colors
        challenge = self.current_challenge()
        self.bug_prompt.config(text=challenge["prompt"])
        self.bug_selected_line = None
        self.bug_selected_fix = None
        for child in self.bug_lines_wrap.winfo_children():
            child.destroy()
        for child in self.bug_fix_wrap.winfo_children():
            child.destroy()
        self.bug_fix_buttons = []
        for idx, line in enumerate(challenge["lines"]):
            btn = tk.Button(
                self.bug_lines_wrap,
                text=f"{idx + 1}. {line}",
                relief="flat",
                bd=0,
                bg=c["code"],
                fg=c["text"],
                justify="left",
                anchor="w",
                font=("Consolas", max(9, int(11 * self.controller.scale))),
                padx=14,
                pady=10,
                command=lambda i=idx: self.select_bug_line(i),
            )
            btn.pack(fill="x", pady=3)
        for idx, option in enumerate(challenge["fixes"]):
            btn = tk.Button(
                self.bug_fix_wrap,
                text=option,
                relief="flat",
                bd=0,
                bg=c["surface_alt"],
                fg=c["text"],
                justify="left",
                anchor="w",
                wraplength=680,
                font=self.controller.font(10),
                padx=14,
                pady=12,
                command=lambda i=idx: self.select_bug_fix(i),
            )
            btn.pack(fill="x", pady=4)
            self.bug_fix_buttons.append(btn)

    def select_bug_line(self, idx):
        self.bug_selected_line = idx
        c = self.controller.colors
        for i, child in enumerate(self.bug_lines_wrap.winfo_children()):
            child.configure(bg=c["primary_soft"] if i == idx else c["code"])

    def select_bug_fix(self, idx):
        self.bug_selected_fix = idx
        c = self.controller.colors
        for i, btn in enumerate(self.bug_fix_buttons):
            btn.configure(bg=c["primary_soft"] if i == idx else c["surface_alt"])

    def check_buggage(self):
        challenge = self.current_challenge()
        if self.bug_selected_line is None or self.bug_selected_fix is None:
            messagebox.showinfo("Complete both steps", "First click the buggy line, then choose the best fix.")
            return
        self.current_attempts += 1
        self.controller.increment_play_attempt(self.current_game)
        if self.bug_selected_line == challenge["bug_line"] and self.bug_selected_fix == challenge["answer"]:
            stars = self._star_value(self.current_attempts)
            self.controller.update_play_record(self.current_game, challenge["id"], stars, topic="Problem Solving")
            self.trace_text.config(text=challenge["explanation"])
            self.set_feedback(f"Correct. You spotted the bug and chose the strongest fix. {stars} star(s) earned.", mode="success")
        else:
            self.set_feedback(f"Not quite. Review which line causes the real problem. {challenge['hint']}", mode="danger")
        self.refresh_mode_progress()

    def load_phishing_challenge(self):
        c = self.controller.colors
        challenge = self.current_challenge()
        self.phishing_prompt.config(text=challenge["prompt"])
        self.email_sender.config(text=f"From: {challenge['sender']}")
        self.email_subject.config(text=f"Subject: {challenge['subject']}")
        self.email_body.config(text=challenge["body"])
        self.phishing_found = set()
        self.phishing_verdict = None
        self.safe_btn.configure(bg=c["surface_alt"])
        self.unsafe_btn.configure(bg=c["surface_alt"])
        for child in self.phishing_clue_wrap.winfo_children():
            child.destroy()
        for idx, clue in enumerate(challenge["clues"]):
            btn = tk.Button(
                self.phishing_clue_wrap,
                text=clue,
                relief="flat",
                bd=0,
                bg=c["surface_alt"],
                fg=c["text"],
                justify="left",
                anchor="w",
                wraplength=680,
                font=self.controller.font(10),
                padx=14,
                pady=12,
                command=lambda i=idx: self.toggle_phishing_clue(i),
            )
            btn.pack(fill="x", pady=4)

    def toggle_phishing_clue(self, idx):
        c = self.controller.colors
        if idx in self.phishing_found:
            self.phishing_found.remove(idx)
        else:
            self.phishing_found.add(idx)
        for i, child in enumerate(self.phishing_clue_wrap.winfo_children()):
            child.configure(bg=c["warning_soft"] if i in self.phishing_found else c["surface_alt"])

    def set_phishing_verdict(self, verdict):
        c = self.controller.colors
        self.phishing_verdict = verdict
        self.safe_btn.configure(bg=c["primary_soft"] if verdict == "Safe" else c["surface_alt"])
        self.unsafe_btn.configure(bg=c["primary_soft"] if verdict == "Unsafe" else c["surface_alt"])

    def check_phishing(self):
        challenge = self.current_challenge()
        if self.phishing_verdict is None:
            messagebox.showinfo("Choose a verdict", "Inspect the clues, then mark the email as Safe or Unsafe.")
            return
        self.current_attempts += 1
        self.controller.increment_play_attempt(self.current_game)
        enough_clues = len(self.phishing_found) >= max(2, len(challenge["clues"]) - 1)
        if self.phishing_verdict == challenge["safe_answer"] and enough_clues:
            stars = self._star_value(self.current_attempts)
            self.controller.update_play_record(self.current_game, challenge["id"], stars, topic="Cybersecurity")
            self.trace_text.config(text=challenge["explanation"])
            self.set_feedback(f"Correct. You inspected the inbox and made the right judgement. {stars} star(s) earned.", mode="success")
        else:
            self.set_feedback(f"Check the sender, urgency, and request more carefully. {challenge['hint']}", mode="danger")
        self.refresh_mode_progress()

    def _star_value(self, attempts):
        return 3 if attempts <= 1 else 2 if attempts == 2 else 1

    def check_reorder(self):
        challenge = self.current_challenge()
        self.current_attempts += 1
        self.controller.increment_play_attempt(self.current_game)
        if self.current_steps == challenge["answer"]:
            stars = self._star_value(self.current_attempts)
            self.controller.update_play_record(self.current_game, challenge["id"], stars, topic="Algorithms")
            trace_lines = [f"{idx + 1}. {step}" for idx, step in enumerate(challenge.get("trace", []))]
            if self.trace_job:
                try:
                    self.after_cancel(self.trace_job)
                except Exception:
                    pass
                self.trace_job = None
            self.trace_text.config(text="")
            self.animate_trace(trace_lines)
            self.set_feedback(f"Correct. You built a valid algorithm in {self.current_attempts} attempt(s) and earned {stars} star(s). {challenge['explanation']}", mode="success")
            self.controller.announce()
        else:
            mismatches = [i for i, (a, b) in enumerate(zip(self.current_steps, challenge["answer"])) if a != b]
            first_wrong = mismatches[0] if mismatches else 0
            should_be = challenge["answer"][first_wrong]
            currently = self.current_steps[first_wrong]
            self.set_feedback(f"Not quite. Step {first_wrong + 1} should be '{should_be}', but you placed '{currently}'. {challenge['hint']}", mode="danger")
            self.trace_text.config(text="Use the hint to improve the order, then try again.")
        self.refresh_mode_progress()

    def select_choice(self, idx):
        if self.answer_locked:
            return
        self.selected_option = idx
        for i, button in enumerate(self.option_buttons):
            button.configure(bg=self.controller.colors["primary_soft"] if i == idx else self.controller.colors["surface_alt"])

    def show_hint(self):
        challenge = self.current_challenge()
        self.set_feedback(f"Hint: {challenge['hint']}", mode="warning")

    def check_choice(self):
        if self.answer_locked:
            return
        if self.selected_option is None:
            messagebox.showinfo("Choose an option", "Select an option before submitting.")
            return
        challenge = self.current_challenge()
        self.current_attempts += 1
        self.controller.increment_play_attempt(self.current_game)
        correct = self.selected_option == challenge["answer"]
        if correct:
            stars = self._star_value(self.current_attempts)
            if self.current_game == "debug":
                topic = "Programming"
            elif self.current_game == "flowchart":
                topic = "Algorithms"
            else:
                topic = "Cybersecurity"
            self.controller.update_play_record(self.current_game, challenge.get("title", str(self.current_index[self.current_game])), stars, topic=topic)
            self.set_feedback(f"Correct. You earned {stars} star(s). {challenge['explanation']}", mode="success")
            self.controller.announce()
        else:
            answer_text = challenge["options"][challenge["answer"]]
            self.set_feedback(f"Not yet. The safest or strongest answer is '{answer_text}'. {challenge['explanation']}", mode="danger")
        for i, button in enumerate(self.option_buttons):
            if i == challenge["answer"]:
                button.configure(bg=self.controller.colors["success_soft"])
            elif i == self.selected_option and not correct:
                button.configure(bg=self.controller.colors["danger_soft"])
            button.configure(state="disabled")
        self.answer_locked = True
        self.refresh_mode_progress()

    def next_challenge(self):
        total = max(1, len(self.available_challenges()))
        self.current_index[self.current_game] = (self.current_index[self.current_game] + 1) % total
        self.current_attempts = 0
        self.load_current_challenge(reset_feedback=True)

    def on_show(self):
        self.refresh_mode_progress()


class QuizPage(BasePage):
    page_name = "Quiz"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = controller.colors
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.question_set = []
        self.wrong_questions = []
        self.current_index = 0
        self.score = 0
        self.selected_option = None
        self.answer_locked = False
        self.topic_results = {}
        self.difficulty_var = tk.StringVar(value="Mixed")
        ttk.Label(self, text="Challenge Quiz", style="Title.TLabel").grid(row=0, column=0, sticky="w", padx=28, pady=(24, 12))

        body = tk.Frame(self, bg=c["bg"])
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 24))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)
        question_card = self.make_card(body)
        question_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        question_card.grid_columnconfigure(0, weight=1)
        self.status_label = tk.Label(question_card, text="", bg=c["surface"], fg=c["muted"], font=controller.font(10))
        self.status_label.grid(row=0, column=0, sticky="w")
        self.question_text = tk.Label(question_card, text="", bg=c["surface"], fg=c["text"], justify="left", wraplength=720, font=controller.font(15, "bold"))
        self.question_text.grid(row=1, column=0, sticky="w", pady=(14, 18))
        top_controls = tk.Frame(question_card, bg=c["surface"])
        top_controls.grid(row=2, column=0, sticky="w", pady=(0, 10))
        tk.Label(top_controls, text="Quiz difficulty:", bg=c["surface"], fg=c["text"], font=controller.font(10, "bold")).grid(row=0, column=0, padx=(0, 8))
        self.diff_combo = ttk.Combobox(top_controls, state="readonly", values=["Mixed", "Beginner", "Intermediate", "Advanced"], textvariable=self.difficulty_var, width=16)
        self.diff_combo.grid(row=0, column=1, padx=(0, 8))
        ttk.Button(top_controls, text="Start fresh quiz", style="Secondary.TButton", command=self.start_quiz).grid(row=0, column=2)
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(question_card, text="", relief="flat", bd=0, bg=c["surface_alt"], activebackground=c["primary_soft"], fg=c["text"], font=controller.font(11), wraplength=620, justify="left", anchor="w", padx=16, pady=16, command=lambda idx=i: self.select_option(idx))
            btn.grid(row=i + 3, column=0, sticky="ew", pady=6)
            self.option_buttons.append(btn)
        controls = tk.Frame(question_card, bg=c["surface"])
        controls.grid(row=8, column=0, sticky="w", pady=(18, 0))
        ttk.Button(controls, text="Submit answer", style="Primary.TButton", command=self.submit_answer).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(controls, text="Next question", style="Secondary.TButton", command=self.next_question).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(controls, text="Retry weak areas", style="Secondary.TButton", command=self.retry_weak_areas).grid(row=0, column=2)
        side = tk.Frame(body, bg=c["bg"])
        side.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        side.grid_rowconfigure((0, 1, 2), weight=1)
        side.grid_columnconfigure(0, weight=1)
        self.feedback_card = self.make_card(side, bg=c["primary_soft"])
        self.feedback_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(self.feedback_card, text="Feedback", bg=c["primary_soft"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.feedback_text = tk.Label(self.feedback_card, text="Use number keys 1–4 or click an option, then press Submit.", bg=c["primary_soft"], fg=c["text"], wraplength=420, justify="left", font=controller.font(10))
        self.feedback_text.pack(anchor="w", pady=(10, 0))
        self.summary_card = self.make_card(side)
        self.summary_card.grid(row=1, column=0, sticky="nsew", pady=8)
        tk.Label(self.summary_card, text="Topic feedback", bg=c["surface"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.summary_text = tk.Label(self.summary_card, text="Your topic summary will appear here.", bg=c["surface"], fg=c["muted"], wraplength=420, justify="left", font=controller.font(10))
        self.summary_text.pack(anchor="w", pady=(10, 0))
        self.tip_card = self.make_card(side, bg=c["warning_soft"])
        self.tip_card.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        tk.Label(self.tip_card, text="Accessibility & revision", bg=c["warning_soft"], fg=c["text"], font=controller.font(13, "bold")).pack(anchor="w")
        self.tip_text = tk.Label(self.tip_card, text="Keyboard support: 1–4 select, Enter submits, and N moves on after feedback.", bg=c["warning_soft"], fg=c["text"], wraplength=420, justify="left", font=controller.font(10))
        self.tip_text.pack(anchor="w", pady=(10, 0))
        self.bind_all("<Key-1>", self._number_select)
        self.bind_all("<Key-2>", self._number_select)
        self.bind_all("<Key-3>", self._number_select)
        self.bind_all("<Key-4>", self._number_select)
        self.bind_all("<Return>", self._enter_submit)
        self.bind_all("<Key-n>", self._next_shortcut)
        self.bind_all("<Key-N>", self._next_shortcut)
        self.start_quiz()

    def _number_select(self, event):
        if self.controller.active_page == "Quiz":
            self.select_option(int(event.keysym) - 1)

    def _enter_submit(self, event):
        if self.controller.active_page == "Quiz":
            self.submit_answer()

    def _next_shortcut(self, event):
        if self.controller.active_page == "Quiz":
            self.next_question()

    def set_feedback(self, text, mode="neutral"):
        c = self.controller.colors
        bg = c["primary_soft"]
        if mode == "success":
            bg = c["success_soft"]
        elif mode == "danger":
            bg = c["danger_soft"]
        self.feedback_card.configure(bg=bg)
        for child in self.feedback_card.winfo_children():
            child.configure(bg=bg)
        self.feedback_text.config(text=text)

    def _prepare_question(self, q):
        options = list(q["options"])
        answer_text = options[q["answer"]]
        random.shuffle(options)
        q2 = dict(q)
        q2["options"] = options
        q2["answer"] = options.index(answer_text)
        return q2

    def start_quiz(self, questions=None):
        difficulty = self.difficulty_var.get()
        pool = questions or [q for q in content_data.QUIZ_QUESTIONS if difficulty == "Mixed" or q.get("difficulty", "Intermediate") == difficulty]
        if len(pool) < 8:
            pool = content_data.QUIZ_QUESTIONS
        selected = random.sample(pool, k=min(8, len(pool)))
        self.question_set = [self._prepare_question(q) for q in selected]
        self.current_index = 0
        self.score = 0
        self.selected_option = None
        self.answer_locked = False
        self.topic_results = {}
        self.wrong_questions = []
        self.summary_text.config(text="Your topic summary will appear here.")
        self.set_feedback("Choose an answer and submit it to see targeted feedback.")
        self.show_question()

    def show_question(self):
        q = self.question_set[self.current_index]
        self.question_text.config(text=q["question"])
        for idx, option in enumerate(q["options"]):
            self.option_buttons[idx].config(text=f"{idx + 1}. {option}", bg=self.controller.colors["surface_alt"], state="normal")
        self.selected_option = None
        self.answer_locked = False
        self.status_label.config(text=f"Question {self.current_index + 1} of {len(self.question_set)} • {q.get('difficulty', 'Intermediate')}")
        self.set_feedback("Choose an answer and submit it to see targeted feedback.")

    def select_option(self, idx):
        if self.answer_locked:
            return
        self.selected_option = idx
        for i, button in enumerate(self.option_buttons):
            button.configure(bg=self.controller.colors["primary_soft"] if i == idx else self.controller.colors["surface_alt"])

    def submit_answer(self):
        if self.answer_locked:
            return
        if self.selected_option is None:
            messagebox.showinfo("Choose an answer", "Select an answer before submitting.")
            return
        q = self.question_set[self.current_index]
        topic = q["topic"]
        hits, asked = self.topic_results.get(topic, (0, 0))
        asked += 1
        correct = self.selected_option == q["answer"]
        if correct:
            self.score += 1
            hits += 1
            self.set_feedback(f"Correct. {q['explanation']}", mode="success")
            self.controller.announce()
        else:
            correct_text = q["options"][q["answer"]]
            self.set_feedback(f"Not quite. Correct answer: {correct_text}. {q['explanation']}", mode="danger")
            self.wrong_questions.append(q)
        self.topic_results[topic] = (hits, asked)
        for i, button in enumerate(self.option_buttons):
            if i == q["answer"]:
                button.configure(bg=self.controller.colors["success_soft"])
            elif i == self.selected_option and not correct:
                button.configure(bg=self.controller.colors["danger_soft"])
            button.configure(state="disabled")
        self.answer_locked = True

    def next_question(self):
        if not self.answer_locked:
            messagebox.showinfo("Submit first", "Submit your answer before moving on.")
            return
        if self.current_index < len(self.question_set) - 1:
            self.current_index += 1
            self.show_question()
        else:
            self.finish_quiz()

    def retry_weak_areas(self):
        if not self.wrong_questions:
            messagebox.showinfo("No weak-area set", "Finish a quiz attempt first, or get at least one question wrong to build a retry set.")
            return
        pool = [dict(q) for q in self.wrong_questions]
        self.start_quiz(questions=pool)

    def finish_quiz(self):
        total = len(self.question_set)
        percentage = int((self.score / total) * 100)
        self.status_label.config(text="Quiz complete")
        self.question_text.config(text="Well done — you completed the quiz.")
        for button in self.option_buttons:
            button.config(text="", state="disabled", bg=self.controller.colors["surface_alt"])
        lines = [f"This attempt: {self.score}/{total} ({percentage}%)."]
        weak_topics = []
        for topic, (hits, asked) in sorted(self.topic_results.items()):
            lines.append(f"{topic}: {hits}/{asked}")
            if hits < asked:
                weak_topics.append(topic)
        if weak_topics:
            lines.append("Recommended revision focus: " + ", ".join(weak_topics))
        else:
            lines.append("No weak areas in this attempt — strong overall performance.")
        self.summary_text.config(text="\n".join(lines))
        self.set_feedback("Use Retry weak areas for a targeted follow-up set, or restart with a different difficulty.")
        self.controller.state_data["recommended_focus"] = ([f"Revise {topic} before the next quiz attempt." for topic in weak_topics] or ["Stretch goal: try a harder quiz difficulty or export the progress report."])
        self.controller.update_quiz_stats(self.score, total, topic_breakdown=self.topic_results, wrong_topics=weak_topics)

    def on_show(self):
        pass




class AboutPage(BasePage):
    page_name = "About"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        c = controller.colors
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="About CS Explorer", style="Title.TLabel").grid(row=0, column=0, sticky="w", padx=28, pady=(24, 12))

        self.scroll = ScrollableFrame(self, bg=c["bg"], controller=controller)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 24))
        body = self.scroll.inner
        body.configure(bg=c["bg"])
        body.grid_columnconfigure((0, 1), weight=1)

        overview = self.make_card(body)
        overview.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        tk.Label(overview, text="The aim of CS Explorer and who it is for", bg=c["surface"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        tk.Label(
            overview,
            text=(
                "CS Explorer is designed to introduce computer science in a way that feels clearer, more engaging, and easier to explore. "
                "It is aimed at learners aged 14 to 17, an age group that often needs a balance between simple explanations and more active, motivating ways to learn.\n\n"
                "The app breaks larger ideas into shorter sections, uses practice tasks and game-like challenges to keep attention, and gives visible progress through badges, XP, levels, and saved profiles. "
                "This helps learners in this age group see that computer science is not just about reading information, but about applying ideas, making decisions, solving problems, and improving over time.\n\n"
                "It is especially useful for 14 to 17 year olds because it combines guidance with independence: learners can explore topics at their own pace, practise through Play, check understanding with Quiz, "
                "and return to their own saved profile without losing progress."
            ),
            bg=c["surface"], fg=c["muted"], wraplength=980, justify="left", font=controller.font(11)
        ).pack(anchor="w", pady=(10, 0))

        sections = self.make_card(body, bg=c["primary_soft"])
        sections.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        tk.Label(sections, text="Sections Explained", bg=c["primary_soft"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        tk.Label(
            sections,
            text=(
                "Home tracks progress and gives a quick summary of where the learner is in their journey.\n\n"
                "Learn explains the core ideas through topic overviews, key ideas, real-life relevance, scenarios, examples, glossary support, and short follow-up tasks.\n\n"
                "Play turns those ideas into interactive practice through algorithm, debugging, and cybersecurity challenges.\n\n"
                "Quiz checks understanding, gives feedback, and helps learners revisit weaker areas.\n\n"
                "About explains the purpose of the app and how its support features work."
            ),
            bg=c["primary_soft"], fg=c["text"], wraplength=480, justify="left", font=controller.font(11)
        ).pack(anchor="w", pady=(10, 0))

        progress = self.make_card(body, bg=c["accent_soft"])
        progress.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        tk.Label(progress, text="Progress Tracking", bg=c["accent_soft"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        tk.Label(
            progress,
            text=(
                "CS Explorer tracks progress in several ways.\n\n"
                "Profiles allow different learners to keep separate saved journeys.\n\n"
                "The Home page shows topics viewed, play progress, quiz score, badges earned, XP, level, and learning streak.\n\n"
                "The progress map shows what has been completed, which parts are unlocked, and what to do next.\n\n"
                "Play records completed challenges, attempts, stars, and unlocked difficulty levels.\n\n"
                "Quiz records scores and helps identify weaker areas to revisit.\n\n"
                "Badges, timestamps, recent activity, and exported progress reports all make learning progress more visible over time."
            ),
            bg=c["accent_soft"], fg=c["text"], wraplength=480, justify="left", font=controller.font(11)
        ).pack(anchor="w", pady=(10, 0))

        accessibility = self.make_card(body, bg=c["warning_soft"])
        accessibility.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        tk.Label(accessibility, text="Accessibility Features", bg=c["warning_soft"], fg=c["text"], font=controller.font(14, "bold")).pack(anchor="w")
        tk.Label(
            accessibility,
            text=(
                "CS Explorer includes several accessibility features to make learning easier to follow.\n\n"
                "Large text increases readability for learners who benefit from bigger, clearer text.\n\n"
                "High contrast improves visibility by increasing separation between text and background colours.\n\n"
                "Dark mode gives an alternative display option that some learners may find more comfortable for longer viewing.\n\n"
                "Visible focus outlines and keyboard navigation support help learners move through the interface without relying only on a mouse.\n\n"
                "The layout also uses short sections, headings, and clear grouping so information is easier to scan and revisit."
            ),
            bg=c["warning_soft"], fg=c["text"], wraplength=980, justify="left", font=controller.font(11)
        ).pack(anchor="w", pady=(10, 0))

