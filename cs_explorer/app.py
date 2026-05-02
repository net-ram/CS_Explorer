import copy
import csv
import json
import os
import shutil
from html import escape
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, ttk

from . import content
from .config import APP_TITLE, APP_GEOMETRY, STATE_FILE, LOGO_FILE, SCHEMES, BASE_DIR
from .pages import HomePage, LearnPage, PlayPage, QuizPage, AboutPage
from .widgets import ScrollableFrame


AVATAR_CHOICES = ["🚀", "🧠", "🎮", "🛡️", "🤖", "🌟"]
AVATAR_DIR = os.path.join(BASE_DIR, "profile_avatars")


class CSExplorerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self._upgrade_content()
        self.master_state = self._load_master_state()
        self.current_profile = self.master_state.get("current_profile", "Student Explorer")
        self.state_data = self.master_state["profiles"][self.current_profile]
        self.active_page = "Home"
        self.frames = {}
        self.sidebar_buttons = {}
        self.colors = SCHEMES[self._scheme_name()]
        self.scale = 1.18 if self.state_data.get("large_text") else 1.0

        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(1360, 860)
        self.configure(bg=self.colors["bg"])
        self.style = ttk.Style(self)
        self._configure_styles()
        self._build_layout()
        self._bind_global_keys()
        self._apply_focus_styles(self)
        self.show_frame("Home")

    def _scheme_name(self):
        if self.state_data.get("high_contrast"):
            return "contrast"
        if self.state_data.get("dark_mode"):
            return "dark"
        return "default"



    def _safe_profile_slug(self, name):
        cleaned = "".join(ch for ch in name if ch.isalnum() or ch in ("_", "-")).strip()
        return cleaned or "profile"

    def _avatar_path_for_profile(self, name, suffix=".png"):
        os.makedirs(AVATAR_DIR, exist_ok=True)
        return os.path.join(AVATAR_DIR, f"{self._safe_profile_slug(name)}_avatar{suffix}")

    def current_level_info(self, xp=None):
        xp = int(self.state_data.get("xp", 0) if xp is None else xp)
        levels = [
            ("Beginner", 0, 120),
            ("Explorer", 120, 280),
            ("Expert", 280, None),
        ]
        for name, floor, ceiling in levels:
            if ceiling is None or xp < ceiling:
                return {"name": name, "floor": floor, "ceiling": ceiling, "xp": xp}
        return {"name": "Expert", "floor": 280, "ceiling": None, "xp": xp}

    def add_xp(self, amount):
        amount = int(max(0, amount))
        old_xp = int(self.state_data.get("xp", 0))
        old_level = self.current_level_info(old_xp)["name"]
        self.state_data["xp"] = old_xp + amount
        new_level = self.current_level_info(self.state_data["xp"])["name"]
        if new_level != old_level:
            self.log_event(f"Level up! You reached {new_level} level.")

    def update_streak(self):
        today = datetime.now().date()
        today_str = today.isoformat()
        last_str = self.state_data.get("last_active_date", "")
        if last_str == today_str:
            return
        yesterday_str = (today - timedelta(days=1)).isoformat()
        if last_str == yesterday_str:
            self.state_data["learning_streak"] = int(self.state_data.get("learning_streak", 0)) + 1
        else:
            self.state_data["learning_streak"] = 1
        self.state_data["last_active_date"] = today_str

    def show_onboarding_tour_if_needed(self):
        if not self.state_data.get("onboarding_seen", False):
            self.show_onboarding_tour(force=True)

    def show_onboarding_tour(self, force=False):
        if self.state_data.get("onboarding_seen") and not force:
            return
        messagebox.showinfo(
            "Welcome to CS Explorer",
            "Quick tour:\n\n"
            "• Home shows your progress, levels, streak, and what to do next.\n"
            "• Learn introduces a topic and explains the key ideas.\n"
            "• Play lets you practise through challenges and scenarios.\n"
            "• Quiz checks understanding and helps you revisit weak areas."
        )
        self.state_data["onboarding_seen"] = True
        self.save_state()

    def _default_profile_state(self, name="Student Explorer"):
        state = {
            "profile_name": name,
            "avatar": "🚀",
            "avatar_image": "",
            "topics_viewed": [],
            "play_state": {
                key: {"completed": [], "stars": {}, "attempts": 0, "best_score": 0}
                for key in content.PLAY_GAMES
            },
            "best_quiz_score": 0,
            "last_quiz_score": 0,
            "quiz_attempts": 0,
            "badges": [],
            "badge_timestamps": {},
            "high_contrast": False,
            "dark_mode": False,
            "large_text": False,
            "audio_enabled": True,
            "easy_read": False,
            "xp": 0,
            "learning_streak": 0,
            "last_active_date": "",
            "onboarding_seen": False,
            "session_history": [],
            "mastery": {topic: 0 for topic in content.LEARN_TOPICS},
            "recommended_focus": ["Start with Learn to unlock more of the learning path."],
            "last_played": "",
            "report_count": 0,
            "unlocked_games": ["builder"],
            "quiz_history": [],
        }
        return state

    def _normalise_profile(self, profile):
        base = self._default_profile_state(profile.get("profile_name", "Student Explorer"))
        if isinstance(profile, dict):
            for key, value in profile.items():
                if key == "play_state" and isinstance(value, dict):
                    for game_key in content.PLAY_GAMES:
                        incoming = value.get(game_key, {}) if isinstance(value.get(game_key, {}), dict) else {}
                        base["play_state"][game_key]["completed"] = list(dict.fromkeys(incoming.get("completed", [])))
                        base["play_state"][game_key]["stars"] = {str(k): int(v) for k, v in dict(incoming.get("stars", {})).items()}
                        base["play_state"][game_key]["attempts"] = int(incoming.get("attempts", 0))
                        base["play_state"][game_key]["best_score"] = int(incoming.get("best_score", 0))
                elif key == "mastery" and isinstance(value, dict):
                    for topic in content.LEARN_TOPICS:
                        base["mastery"][topic] = int(value.get(topic, 0))
                elif key in base:
                    base[key] = value
        base["topics_viewed"] = [t for t in base.get("topics_viewed", []) if t in content.LEARN_TOPICS]
        base["last_played"] = base.get("last_played") or ""
        base["session_history"] = list(base.get("session_history", []))[-15:]
        base["recommended_focus"] = list(base.get("recommended_focus", [])) or ["Explore a topic in Learn to begin the roadmap."]
        self._refresh_badges_for_profile(base)
        self._update_unlocked_games_for_profile(base)
        return base

    def _load_master_state(self):
        if os.path.exists(STATE_FILE):
            try:
                raw = json.load(open(STATE_FILE, "r", encoding="utf-8"))
                if isinstance(raw, dict) and "profiles" in raw:
                    profiles = {}
                    for name, profile in raw.get("profiles", {}).items():
                        profiles[name] = self._normalise_profile(profile)
                    if not profiles:
                        profiles = {"Student Explorer": self._default_profile_state()}
                    current = raw.get("current_profile") or next(iter(profiles))
                    if current not in profiles:
                        current = next(iter(profiles))
                    return {"profiles": profiles, "current_profile": current}
                if isinstance(raw, dict):
                    profile_name = raw.get("profile_name", "Student Explorer")
                    return {
                        "profiles": {profile_name: self._normalise_profile(raw)},
                        "current_profile": profile_name,
                    }
            except Exception:
                pass
        default = self._default_profile_state()
        return {"profiles": {default["profile_name"]: default}, "current_profile": default["profile_name"]}

    def save_state(self):
        self.state_data["last_played"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._refresh_badges_for_profile(self.state_data)
        self._update_unlocked_games_for_profile(self.state_data)
        self.master_state["profiles"][self.current_profile] = self.state_data
        self.master_state["current_profile"] = self.current_profile
        with open(STATE_FILE, "w", encoding="utf-8") as handle:
            json.dump(self.master_state, handle, indent=2)

    def _upgrade_content(self):
        content.BADGE_LIBRARY.update({
            "pathway_planner": ("Pathway Planner", "View three or more topics and follow the guided roadmap."),
            "accessible_explorer": ("Accessible Explorer", "Use at least one accessibility support feature."),
            "report_exporter": ("Progress Reporter", "Export a learner progress report."),
        })
        content.PLAY_GAMES = copy.deepcopy(content.PLAY_GAMES)
        content.PLAY_GAMES["builder"]["challenges"] = [
            {"id": "toast_beginner", "difficulty": "Beginner", "title": "Morning Routine Algorithm", "prompt": "Arrange the steps into a sensible order so the routine works from start to finish.", "steps": ["Wake up", "Turn off the alarm", "Get dressed", "Brush your teeth", "Leave for school"], "answer": ["Wake up", "Turn off the alarm", "Brush your teeth", "Get dressed", "Leave for school"], "hint": "Start with the action that makes every later step possible.", "explanation": "A good algorithm follows a logical sequence from first action to outcome.", "trace": ["Start", "Wake up", "Turn off the alarm", "Brush your teeth", "Get dressed", "Leave for school", "End"]},
            {"id": "largest_beginner", "difficulty": "Beginner", "title": "Finding the Largest Number", "prompt": "Order the logic for a simple max-finding algorithm.", "steps": ["Look at the next number", "Start by assuming the first number is the largest", "Replace the largest if the new number is bigger", "Repeat until all numbers have been checked", "Output the largest number"], "answer": ["Start by assuming the first number is the largest", "Look at the next number", "Replace the largest if the new number is bigger", "Repeat until all numbers have been checked", "Output the largest number"], "hint": "Initialise a value before comparing anything else.", "explanation": "This models initialise, compare, update, repeat, and output — a core computational pattern.", "trace": ["largest = first number", "read next number", "compare", "update largest if needed", "repeat until finished", "print largest"]},
            {"id": "login_intermediate", "difficulty": "Intermediate", "title": "Login with Branching", "prompt": "Build an algorithm that checks a username and password, then branches to the correct outcome.", "steps": ["If both are correct, show the dashboard", "Ask the user for a username and password", "Check whether the username exists", "Check whether the password matches", "If any check fails, show an access denied message"], "answer": ["Ask the user for a username and password", "Check whether the username exists", "Check whether the password matches", "If both are correct, show the dashboard", "If any check fails, show an access denied message"], "hint": "Branching still begins with input, then checks, then outcomes.", "explanation": "This introduces conditional logic: different outputs depend on different conditions.", "trace": ["Input credentials", "Check username", "Check password", "IF both pass → dashboard", "ELSE → access denied"]},
            {"id": "quiz_advanced", "difficulty": "Advanced", "title": "Adaptive Revision Loop", "prompt": "Reorder the steps for an algorithm that keeps giving revision questions until the learner reaches the target score.", "steps": ["Ask the next question", "Stop once the target score is reached", "Check whether the answer is correct and update the score", "Start with score = 0", "Repeat while the score is below the target"], "answer": ["Start with score = 0", "Repeat while the score is below the target", "Ask the next question", "Check whether the answer is correct and update the score", "Stop once the target score is reached"], "hint": "Loops need a starting state, a condition, repeated steps, and an exit point.", "explanation": "This is a loop-based algorithm, useful when building interactive learning tools.", "trace": ["score = 0", "WHILE score < target", "ask question", "check answer", "update score", "END loop when target reached"]},
            {"id": "cyber_advanced", "difficulty": "Advanced", "title": "Phishing Response Flow", "prompt": "Build a branching algorithm for handling a suspicious email safely.", "steps": ["If it looks suspicious, do not click the link", "Report the message to a trusted adult or teacher", "Read the email carefully", "Check the sender and spelling", "Delete or quarantine the message after reporting"], "answer": ["Read the email carefully", "Check the sender and spelling", "If it looks suspicious, do not click the link", "Report the message to a trusted adult or teacher", "Delete or quarantine the message after reporting"], "hint": "The analysis comes before the action, and safety comes before deletion.", "explanation": "This task combines sequencing with a decision point and safe security behaviour.", "trace": ["Open message view", "Inspect sender/spelling", "IF suspicious → avoid link", "Report", "Delete/quarantine"]},
        ]
        extra_questions = [
            {"question": "Which feature helps users go straight to the next challenge after feedback?", "options": ["Keyboard shortcuts", "A printer cable", "Low battery mode", "A wallpaper"], "answer": 0, "explanation": "Keyboard shortcuts speed up navigation and improve accessibility.", "topic": "Software Engineering", "difficulty": "Beginner"},
            {"question": "What is the main purpose of a loop in an algorithm?", "options": ["To repeat steps while a condition is true", "To make the screen colourful", "To rename variables", "To hide bugs"], "answer": 0, "explanation": "Loops repeat a block of logic until a condition changes.", "topic": "Algorithms", "difficulty": "Beginner"},
            {"question": "Why is adaptive feedback useful in a quiz app?", "options": ["It helps learners focus on weak areas", "It removes the need for testing", "It makes every answer correct", "It stops progress saving"], "answer": 0, "explanation": "Adaptive feedback can point learners back to the areas that need more revision.", "topic": "Problem Solving", "difficulty": "Intermediate"},
            {"question": "Which option is the best example of abstraction?", "options": ["Focusing on the key details of a route and ignoring the colour of every building", "Writing every tiny detail even when it is irrelevant", "Restarting the computer repeatedly", "Sharing your password"], "answer": 0, "explanation": "Abstraction means keeping the important detail and ignoring noise.", "topic": "Computational Thinking", "difficulty": "Intermediate"},
            {"question": "Why should educational apps keep track of mastery by topic?", "options": ["So feedback can be targeted", "To make the font smaller", "To stop users changing screens", "To disable saving"], "answer": 0, "explanation": "Topic mastery helps the app recommend what to revise next.", "topic": "Software Engineering", "difficulty": "Intermediate"},
            {"question": "What makes an algorithm with branching different from a simple sequence?", "options": ["It can choose between different paths depending on conditions", "It always runs backwards", "It removes all inputs", "It never ends"], "answer": 0, "explanation": "Branching creates different outcomes depending on rules or conditions.", "topic": "Algorithms", "difficulty": "Advanced"},
            {"question": "Which is the strongest reason to include an exportable progress report?", "options": ["It gives clear evidence of learning progress", "It makes passwords shorter", "It removes accessibility options", "It hides quiz scores"], "answer": 0, "explanation": "A report can summarise progress, achievements, and next actions for users or teachers.", "topic": "Software Engineering", "difficulty": "Advanced"},
            {"question": "Which AI risk is most linked to poor-quality training data?", "options": ["Biased or unfair outcomes", "Stronger batteries", "Faster typing", "Louder speakers"], "answer": 0, "explanation": "Weak or biased data can lead to weak or unfair AI outputs.", "topic": "Artificial Intelligence", "difficulty": "Advanced"},
        ]
        for q in content.QUIZ_QUESTIONS:
            q.setdefault("difficulty", "Intermediate")
        content.PLAY_GAMES["cyber"]["challenges"].extend([
            {
                "title": "Fake Prize Message",
                "prompt": "You receive a message saying you have won a prize and need to enter your bank details today. What is the safest response?",
                "code": "Scenario: prize message + pressure + sensitive data request",
                "options": [
                    "Enter the details quickly so the prize is not lost",
                    "Ignore the pressure, verify the source, and avoid sharing any personal financial details",
                    "Forward the message to more people so they can win too",
                    "Reply with your home address first",
                ],
                "answer": 1,
                "hint": "Unexpected prizes and urgent deadlines are common scam tactics.",
                "explanation": "A genuine organisation will not pressure you into sharing sensitive details through an unverified message.",
            },
            {
                "title": "Oversharing Online",
                "prompt": "A friend wants to post a photo that clearly shows your school badge and home street sign. What is the safest choice?",
                "code": "Scenario: photo sharing + personal location details",
                "options": [
                    "Let them post it because it looks funny",
                    "Ask them to crop or avoid posting details that reveal your identity or location",
                    "Post your timetable in the comments too",
                    "Tag your full address for context",
                ],
                "answer": 1,
                "hint": "Think about what information strangers could learn from the image.",
                "explanation": "Protecting location and identity details helps reduce privacy and safety risks online.",
            },
        ])
        content.PLAY_GAMES["debug"]["challenges"].extend([
            {
                "title": "Login Counter Bug",
                "prompt": "A school app should count failed logins, but it never changes the counter. What is the most likely issue?",
                "code": "failed = 0\nwhile failed < 3:\n    print('Try again')",
                "options": [
                    "The variable is never updated inside the loop",
                    "Counters cannot be used in loops",
                    "print should always come before the loop",
                    "The number 3 must be a string",
                ],
                "answer": 0,
                "hint": "Ask yourself what changes after each failed attempt.",
                "explanation": "If the counter never changes, the loop condition stays true and the app cannot track progress properly.",
            },
        ])
        content.QUIZ_QUESTIONS = content.QUIZ_QUESTIONS + extra_questions

    def total_play_completed(self):
        return sum(len(self.state_data["play_state"].get(key, {}).get("completed", [])) for key in content.PLAY_GAMES)

    def total_play_challenges(self):
        return sum(len(game["challenges"]) for game in content.PLAY_GAMES.values())

    def _configure_styles(self):
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        c = self.colors
        self.style.configure("Sidebar.TFrame", background=c["nav"])
        self.style.configure("Title.TLabel", background=c["bg"], foreground=c["text"], font=self.font(28, "bold"))
        self.style.configure("Section.TLabel", background=c["bg"], foreground=c["text"], font=self.font(18, "bold"))
        self.style.configure("Body.TLabel", background=c["bg"], foreground=c["muted"], font=self.font(11))
        self.style.configure("Primary.TButton", font=self.font(10, "bold"), padding=(14, 11), background=c["accent"], foreground="white", borderwidth=0, focusthickness=3, focuscolor=c["accent"])
        self.style.map("Primary.TButton", background=[("active", c["success"]), ("pressed", c["success"])], foreground=[("disabled", "#f0f0f0")])
        self.style.configure("Secondary.TButton", font=self.font(10, "bold"), padding=(14, 11), background=c["primary_soft"], foreground=c["text"], borderwidth=0)
        self.style.map("Secondary.TButton", background=[("active", c["surface_dark"]), ("pressed", c["surface_dark"])])
        self.style.configure("TCombobox", arrowsize=max(12, int(14 * self.scale)))
        self.style.configure("Accent.Horizontal.TProgressbar", troughcolor=c["primary_soft"], background=c["primary"], bordercolor=c["primary_soft"], lightcolor=c["primary"], darkcolor=c["primary"])

    def font(self, size, weight="normal", slant="roman"):
        return ("Segoe UI", max(9, int(size * self.scale)), weight, slant)

    def _bind_global_keys(self):
        self.bind_all("<Alt-Key-1>", lambda e: self.show_frame("Home"))
        self.bind_all("<Alt-Key-2>", lambda e: self.show_frame("Learn"))
        self.bind_all("<Alt-Key-3>", lambda e: self.show_frame("Play"))
        self.bind_all("<Alt-Key-4>", lambda e: self.show_frame("Quiz"))
        self.bind_all("<Alt-Key-5>", lambda e: self.show_frame("About"))

    def _build_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        c = self.colors

        sidebar_outer = ttk.Frame(self, style="Sidebar.TFrame", width=310)
        sidebar_outer.grid(row=0, column=0, sticky="ns")
        sidebar_outer.grid_propagate(False)

        sidebar_canvas = tk.Canvas(sidebar_outer, bg=c["nav"], highlightthickness=0, width=310)
        sidebar_scroll = ttk.Scrollbar(sidebar_outer, orient="vertical", command=sidebar_canvas.yview)
        sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)
        sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scroll.pack(side="right", fill="y")

        sidebar = tk.Frame(sidebar_canvas, bg=c["nav"])
        sidebar_window = sidebar_canvas.create_window((0, 0), window=sidebar, anchor="nw")

        sidebar.bind("<Configure>", lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        sidebar_canvas.bind("<Configure>", lambda e: sidebar_canvas.itemconfigure(sidebar_window, width=e.width))
        sidebar_canvas.bind("<MouseWheel>", lambda e: sidebar_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        sidebar.bind("<MouseWheel>", lambda e: sidebar_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.logo_image = None
        try:
            if os.path.exists(LOGO_FILE):
                self.logo_image = tk.PhotoImage(file=LOGO_FILE)
                max_w, max_h = 252, 248
                step_x = max(1, (self.logo_image.width() + max_w - 1) // max_w)
                step_y = max(1, (self.logo_image.height() + max_h - 1) // max_h)
                step = max(step_x, step_y)
                if step > 1:
                    self.logo_image = self.logo_image.subsample(step, step)
                tk.Label(sidebar, image=self.logo_image, bg=c["nav"]).pack(anchor="w", padx=18, pady=(10, 8))
            else:
                logo = tk.Canvas(sidebar, width=64, height=64, bg=c["nav"], highlightthickness=0)
                logo.pack(anchor="w", padx=22, pady=(22, 8))
                logo.create_oval(6, 6, 58, 58, fill=c["accent"], outline="")
                logo.create_text(32, 32, text="CS", fill="white", font=self.font(15, "bold"))
        except Exception:
            logo = tk.Canvas(sidebar, width=64, height=64, bg=c["nav"], highlightthickness=0)
            logo.pack(anchor="w", padx=22, pady=(22, 8))
            logo.create_oval(6, 6, 58, 58, fill=c["accent"], outline="")
            logo.create_text(32, 32, text="CS", fill="white", font=self.font(15, "bold"))

        tk.Label(sidebar, text="It\'s Time to Explore the World of Computer Science!", bg=c["nav"], fg="#dfe7f5", justify="left", wraplength=250, font=self.font(10)).pack(anchor="w", padx=22, pady=(4, 14))

        nav_wrap = tk.Frame(sidebar, bg=c["nav"])
        nav_wrap.pack(fill="x", padx=16)
        nav_labels = {"Home": "🏠  Home", "Learn": "📘  Learn", "Play": "🎮  Play", "Quiz": "⚡  Quiz", "About": "✨  About"}
        for name in ["Home", "Learn", "Play", "Quiz", "About"]:
            btn = tk.Button(nav_wrap, text=nav_labels[name], font=self.font(11, "bold"), relief="flat", bd=0, fg="white", bg=c["nav_alt"], activebackground=c["primary"], activeforeground="white", padx=18, pady=12, anchor="w", command=lambda n=name: self.show_frame(n))
            btn.pack(fill="x", pady=5)
            self.sidebar_buttons[name] = btn

        tools = tk.Frame(sidebar, bg=c["nav"])
        tools.pack(fill="x", padx=16, pady=(10, 8))
        tk.Label(tools, text="Profile & accessibility", bg=c["nav"], fg="white", font=self.font(11, "bold")).pack(anchor="w", pady=(4, 8))
        self.profile_choice = ttk.Combobox(tools, values=list(self.master_state["profiles"].keys()), state="readonly", font=self.font(10))
        self.profile_choice.set(self.current_profile)
        self.profile_choice.pack(fill="x", pady=(0, 6))
        tk.Button(tools, text="Switch profile", command=self.switch_profile_ui, relief="flat", bd=0, bg=c["primary"], fg="white", font=self.font(10, "bold"), pady=9).pack(fill="x", pady=(0, 6))
        self.profile_var = tk.StringVar(value=self.state_data.get("profile_name", self.current_profile))
        entry = tk.Entry(tools, textvariable=self.profile_var, relief="flat", bd=0, font=self.font(10), bg="white", fg=c["text"], takefocus=1)
        entry.pack(fill="x", pady=(0, 6), ipady=8)

        tk.Label(tools, text="Avatar", bg=c["nav"], fg="#dfe7f5", font=self.font(9, "bold")).pack(anchor="w", pady=(6, 3))
        self.avatar_choice = ttk.Combobox(tools, values=AVATAR_CHOICES, state="readonly", font=self.font(10), width=8)
        self.avatar_choice.set(self.state_data.get("avatar", "🚀"))
        self.avatar_choice.pack(fill="x", pady=(0, 6))

        tk.Button(tools, text="Upload avatar image", command=self.upload_avatar_image, relief="flat", bd=0, bg=c["nav_alt"], fg="white", font=self.font(10, "bold"), pady=9).pack(fill="x", pady=(0, 6))
        tk.Button(tools, text="Use emoji avatar", command=self.clear_avatar_image, relief="flat", bd=0, bg=c["nav_alt"], fg="white", font=self.font(10, "bold"), pady=9).pack(fill="x", pady=(0, 6))
        tk.Button(tools, text="Save avatar", command=self.save_profile_style, relief="flat", bd=0, bg=c["primary"], fg="white", font=self.font(10, "bold"), pady=9).pack(fill="x", pady=(0, 6))
        tk.Button(tools, text="Create new profile", command=self.create_profile, relief="flat", bd=0, bg=c["nav_alt"], fg="white", font=self.font(10, "bold"), pady=9).pack(fill="x", pady=(0, 6))
        tk.Button(tools, text="Rename current profile", command=self.save_profile_name, relief="flat", bd=0, bg=c["nav_alt"], fg="white", font=self.font(10, "bold"), pady=9).pack(fill="x", pady=(0, 6))
        tk.Button(tools, text="Delete current profile", command=self.delete_current_profile, relief="flat", bd=0, bg=c["danger"], fg="white", font=self.font(10, "bold"), pady=9).pack(fill="x", pady=(0, 6))
        tk.Button(tools, text="Export progress report", command=self.export_progress_report, relief="flat", bd=0, bg=c["accent"], fg="white", font=self.font(10, "bold"), pady=9).pack(fill="x", pady=(0, 8))
        self._toggle_button(tools, f"Large text: {'On' if self.state_data['large_text'] else 'Off'}", self.toggle_large_text).pack(fill="x", pady=3)
        self._toggle_button(tools, f"High contrast: {'On' if self.state_data['high_contrast'] else 'Off'}", self.toggle_high_contrast).pack(fill="x", pady=3)
        self._toggle_button(tools, f"Dark mode: {'On' if self.state_data.get('dark_mode', False) else 'Off'}", self.toggle_dark_mode).pack(fill="x", pady=3)

        note = tk.Frame(sidebar, bg=c["nav_soft"], highlightbackground="#35527f", highlightthickness=1)
        note.pack(fill="x", padx=16, pady=(8, 12))
        tk.Label(note, text="Quick controls", bg=c["nav_soft"], fg="white", font=self.font(11, "bold")).pack(anchor="w", padx=14, pady=(12, 6))
        tk.Label(note, text="Alt+1 Home  Alt+2 Learn\nAlt+3 Play  Alt+4 Quiz\nAlt+5 About\nTab = move focus", bg=c["nav_soft"], fg="#dfe7f5", justify="left", font=self.font(9)).pack(anchor="w", padx=14, pady=(0, 12))

        footer = tk.Frame(sidebar, bg=c["nav_soft"], highlightbackground="#35527f", highlightthickness=1)
        footer.pack(fill="x", padx=16, pady=16)
        tk.Label(footer, text="Built for learners", bg=c["nav_soft"], fg="white", font=self.font(11, "bold")).pack(anchor="w", padx=14, pady=(12, 6))
        tk.Label(footer, text="Profiles, badges, progress reports, and accessibility tools all work together to make the experience smoother and easier to use.", bg=c["nav_soft"], fg="#dfe7f5", wraplength=230, justify="left", font=self.font(9)).pack(anchor="w", padx=14, pady=(0, 12))

        self.content = tk.Frame(self, bg=c["bg"])
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        for page in [HomePage(self.content, self), LearnPage(self.content, self), PlayPage(self.content, self), QuizPage(self.content, self), AboutPage(self.content, self)]:
            self.frames[page.page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

    def _toggle_button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, relief="flat", bd=0, bg=self.colors["nav_alt"], fg="white", activebackground=self.colors["primary"], activeforeground="white", font=self.font(10, "bold"), pady=10, takefocus=1)

    def _apply_focus_styles(self, widget):
        focusable = (tk.Button, tk.Entry, tk.Listbox, tk.Text, tk.Scale, ttk.Combobox)
        if isinstance(widget, focusable):
            try:
                widget.configure(highlightthickness=2, highlightbackground=self.colors["border"], highlightcolor=self.colors["accent"], takefocus=1)
            except Exception:
                pass
        for child in widget.winfo_children():
            self._apply_focus_styles(child)

    def rebuild_ui(self, target_page=None):
        current = target_page or self.active_page
        for child in self.winfo_children():
            child.destroy()
        self.frames = {}
        self.sidebar_buttons = {}
        self.colors = SCHEMES[self._scheme_name()]
        self.scale = 1.18 if self.state_data.get("large_text") else 1.0
        self.configure(bg=self.colors["bg"])
        self._configure_styles()
        self._build_layout()
        self._apply_focus_styles(self)
        self.show_frame(current)

    def announce(self):
        return

    def switch_profile_ui(self):
        chosen = self.profile_choice.get().strip()
        if chosen and chosen in self.master_state["profiles"] and chosen != self.current_profile:
            self.current_profile = chosen
            self.state_data = self.master_state["profiles"][chosen]
            self.save_state()
            self.rebuild_ui("Home")

    def save_profile_style(self):
        self.state_data["avatar"] = self.avatar_choice.get().strip() or "🚀"
        self.log_event("Updated the profile avatar.")
        self.save_state()
        self.rebuild_ui("Home")

    def upload_avatar_image(self):
        file_path = filedialog.askopenfilename(
            title="Choose avatar image",
            filetypes=[
                ("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp"),
                ("PNG images", "*.png"),
                ("JPEG images", "*.jpg;*.jpeg"),
                ("GIF images", "*.gif"),
                ("BMP images", "*.bmp"),
                ("WEBP images", "*.webp"),
                ("All files", "*.*"),
            ],
        )
        if not file_path:
            return

        suffix = os.path.splitext(file_path)[1].lower() or ".png"
        target = self._avatar_path_for_profile(self.current_profile, suffix=suffix)
        try:
            os.makedirs(AVATAR_DIR, exist_ok=True)
            shutil.copy2(file_path, target)
            self.state_data["avatar_image"] = target
            self.log_event("Uploaded a custom avatar image.")
            self.save_state()
            self.rebuild_ui("Home")
        except Exception as exc:
            messagebox.showerror("Avatar upload failed", f"Could not save that image.\n\n{exc}")

    def clear_avatar_image(self):
        current = self.state_data.get("avatar_image", "")
        self.state_data["avatar_image"] = ""
        try:
            if current and os.path.exists(current):
                os.remove(current)
        except Exception:
            pass
        self.log_event("Switched back to the emoji avatar.")
        self.save_state()
        self.rebuild_ui("Home")

    def create_profile(self):
        name = self.profile_var.get().strip() or "Student Explorer"

        if name in self.master_state["profiles"]:
            if messagebox.askyesno("Switch profile", f"A profile called '{name}' already exists. Switch to it?"):
                self.current_profile = name
                self.state_data = self.master_state["profiles"][name]
                self.save_state()
                self.rebuild_ui("Home")
            return

        self.master_state["profiles"][name] = self._default_profile_state(name)
        self.master_state["profiles"][name]["avatar"] = self.avatar_choice.get().strip() or "🚀"
        self.master_state["profiles"][name]["avatar_image"] = ""
        self.current_profile = name
        self.state_data = self.master_state["profiles"][name]
        self.log_event("Created a new learner profile.")
        self.save_state()
        self.rebuild_ui("Home")

    def save_profile_name(self):
        name = self.profile_var.get().strip() or "Student Explorer"

        if name == self.current_profile:
            self.state_data["profile_name"] = name
            self.save_state()
            self.rebuild_ui("Home")
            return

        if name in self.master_state["profiles"]:
            messagebox.showinfo(
                "Name already in use",
                f"A profile called '{name}' already exists. Choose a different name or switch to that profile."
            )
            return

        old_name = self.current_profile
        old_avatar_image = self.state_data.get("avatar_image", "")
        self.state_data["profile_name"] = name
        if old_avatar_image and os.path.exists(old_avatar_image):
            suffix = os.path.splitext(old_avatar_image)[1].lower() or ".png"
            new_avatar_path = self._avatar_path_for_profile(name, suffix=suffix)
            try:
                if old_avatar_image != new_avatar_path:
                    shutil.copy2(old_avatar_image, new_avatar_path)
                    os.remove(old_avatar_image)
                self.state_data["avatar_image"] = new_avatar_path
            except Exception:
                self.state_data["avatar_image"] = old_avatar_image
        self.master_state["profiles"][name] = self.state_data
        if old_name in self.master_state["profiles"]:
            del self.master_state["profiles"][old_name]
        self.current_profile = name
        self.log_event(f"Renamed the profile to {name}.")
        self.save_state()
        self.rebuild_ui("Home")

    def delete_current_profile(self):
        if len(self.master_state["profiles"]) <= 1:
            messagebox.showinfo("Cannot delete profile", "At least one profile must remain in the app.")
            return
        if not messagebox.askyesno("Delete profile", f"Delete the profile '{self.current_profile}'? This cannot be undone."):
            return
        profile_to_delete = self.current_profile
        avatar_to_delete = self.state_data.get("avatar_image", "")
        remaining = [name for name in self.master_state["profiles"] if name != profile_to_delete]
        del self.master_state["profiles"][profile_to_delete]
        try:
            if avatar_to_delete and os.path.exists(avatar_to_delete):
                os.remove(avatar_to_delete)
        except Exception:
            pass
        self.current_profile = remaining[0]
        self.state_data = self.master_state["profiles"][self.current_profile]
        self.save_state()
        self.rebuild_ui("Home")

    def export_progress_report(self):
        safe = "".join(ch for ch in self.current_profile if ch.isalnum() or ch in ('_', '-')).strip() or "profile"
        stamp = datetime.now().strftime('%Y%m%d_%H%M')
        txt_path = os.path.join(BASE_DIR, f"{safe}_progress_report_{stamp}.txt")

        level_info = self.current_level_info()
        mastery_items = list(self.state_data.get("mastery", {}).items())
        mastery_lines = [f"- {topic}: {score}%" for topic, score in mastery_items]
        badges = [content.BADGE_LIBRARY.get(b, (b, ""))[0] for b in self.state_data.get("badges", [])]
        recommendations = self.state_data.get("recommended_focus", [])
        recent_activity = self.state_data.get("session_history", [])[-10:]
        topics_viewed = len(self.state_data.get('topics_viewed', []))
        play_progress = f"{self.total_play_completed()}/{self.total_play_challenges()}"
        best_quiz = self.state_data.get('best_quiz_score', 0)
        last_played = self.state_data.get('last_played', 'N/A')

        text_lines = [
            f"CS Explorer Progress Report for {self.current_profile}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"Topics viewed: {topics_viewed}/{len(content.LEARN_TOPICS)}",
            f"Play progress: {play_progress}",
            f"Best quiz score: {best_quiz}",
            f"XP: {self.state_data.get('xp', 0)}",
            f"Level: {level_info['name']}",
            f"Learning streak: {self.state_data.get('learning_streak', 0)} day(s)",
            f"Last played: {last_played}",
            "",
            "Mastery by topic:",
            *mastery_lines,
            "",
            "Badges:",
            *(badges or ["- None yet"]),
            "",
            "Recommended next steps:",
            *[f"- {item}" for item in recommendations],
            "",
            "Recent activity:",
            *[f"- {item}" for item in recent_activity],
        ]

        with open(txt_path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(text_lines))

        self.state_data["report_count"] = int(self.state_data.get("report_count", 0)) + 1
        self.award_badge("report_exporter")
        self.log_event("Exported a progress report.")
        self.save_state()
        messagebox.showinfo("Report exported", f"Saved text report to:\n{txt_path}")

    def toggle_large_text(self):
        self.state_data["large_text"] = not self.state_data.get("large_text", False)
        self.award_badge("accessible_explorer")
        self.save_state()
        self.rebuild_ui()

    def toggle_high_contrast(self):
        self.state_data["high_contrast"] = not self.state_data.get("high_contrast", False)
        self.award_badge("accessible_explorer")
        self.save_state()
        self.rebuild_ui()

    def toggle_dark_mode(self):
        self.state_data["dark_mode"] = not self.state_data.get("dark_mode", False)
        self.award_badge("accessible_explorer")
        self.save_state()
        self.rebuild_ui()

    def toggle_audio(self):
        self.state_data["audio_enabled"] = not self.state_data.get("audio_enabled", True)
        self.save_state()
        self.rebuild_ui()

    def toggle_easy_read(self):
        self.state_data["easy_read"] = not self.state_data.get("easy_read", False)
        self.save_state()
        self.rebuild_ui()

    def show_frame(self, name):
        self.active_page = name
        frame = self.frames[name]
        frame.tkraise()
        for key, btn in self.sidebar_buttons.items():
            btn.configure(bg=self.colors["primary"] if key == name else self.colors["nav_alt"])
        if hasattr(frame, "on_show"):
            frame.on_show()

    def log_event(self, text):
        stamp = datetime.now().strftime("%d/%m %H:%M")
        self.state_data.setdefault("session_history", []).append(f"{stamp} — {text}")
        self.state_data["session_history"] = self.state_data["session_history"][-20:]

    def award_badge(self, badge_id):
        if badge_id not in self.state_data.get("badges", []):
            self.state_data.setdefault("badges", []).append(badge_id)
            self.state_data.setdefault("badge_timestamps", {})[badge_id] = datetime.now().strftime("%Y-%m-%d %H:%M")

    def _refresh_badges_for_profile(self, profile):
        topics_count = len(profile.get("topics_viewed", []))
        play_state = profile.get("play_state", {})
        if topics_count >= 1:
            self._award_on_profile(profile, "curious_start")
        if topics_count >= len(content.LEARN_TOPICS):
            self._award_on_profile(profile, "knowledge_builder")
        if topics_count >= 3:
            self._award_on_profile(profile, "pathway_planner")
        if play_state.get("builder", {}).get("completed"):
            self._award_on_profile(profile, "builder_badge")
        if play_state.get("debug", {}).get("completed"):
            self._award_on_profile(profile, "debug_badge")
        if play_state.get("cyber", {}).get("completed"):
            self._award_on_profile(profile, "cyber_badge")
        if profile.get("best_quiz_score", 0) >= 6:
            self._award_on_profile(profile, "quiz_star")
        if profile.get("best_quiz_score", 0) >= 8:
            self._award_on_profile(profile, "quiz_master")
        if all(play_state.get(key, {}).get("completed") for key in content.PLAY_GAMES) and profile.get("best_quiz_score", 0) >= 6:
            self._award_on_profile(profile, "all_rounder")
        if profile.get("large_text") or profile.get("high_contrast") or profile.get("dark_mode") or profile.get("easy_read"):
            self._award_on_profile(profile, "accessible_explorer")

    def _award_on_profile(self, profile, badge_id):
        profile.setdefault("badges", [])
        if badge_id not in profile["badges"]:
            profile["badges"].append(badge_id)
            profile.setdefault("badge_timestamps", {})[badge_id] = datetime.now().strftime("%Y-%m-%d %H:%M")

    def _update_unlocked_games_for_profile(self, profile):
        unlocked = set(["builder"])
        viewed = set(profile.get("topics_viewed", []))
        if "Algorithms" in viewed or len(viewed) >= 2:
            unlocked.add("flowchart")
        if "Programming" in viewed or len(viewed) >= 2:
            unlocked.add("debug")
            unlocked.add("binary")
        if "Computational Thinking" in viewed or len(viewed) >= 3:
            unlocked.add("logic")
        if "Problem Solving" in viewed or len(viewed) >= 3:
            unlocked.add("bugrace")
        if "Cybersecurity" in viewed or len(viewed) >= 3:
            unlocked.add("cyber")
            unlocked.add("phishing")
        order = ["builder", "flowchart", "debug", "binary", "logic", "bugrace", "cyber", "phishing"]
        profile["unlocked_games"] = [key for key in order if key in unlocked]

    def update_mastery(self, topic, amount):
        current = int(self.state_data.setdefault("mastery", {}).get(topic, 0))
        self.state_data["mastery"][topic] = max(0, min(100, current + amount))

    def mark_topic_viewed(self, topic):
        if topic not in self.state_data["topics_viewed"]:
            self.state_data["topics_viewed"].append(topic)
            self.update_mastery(topic, 15)
            self.update_streak()
            self.add_xp(20)
            self.log_event(f"Viewed learning topic: {topic}.")
        self._update_unlocked_games_for_profile(self.state_data)
        self._update_recommendations()
        self.save_state()
        home = self.frames.get("Home")
        if home:
            home.refresh_stats()

    def update_play_record(self, game_key, challenge_id, stars, topic=None):
        play_state = self.state_data["play_state"][game_key]
        if challenge_id not in play_state["completed"]:
            play_state["completed"].append(challenge_id)
        previous_star = int(play_state["stars"].get(str(challenge_id), 0))
        play_state["stars"][str(challenge_id)] = max(previous_star, stars)
        play_state["best_score"] = max(play_state["best_score"], len(play_state["completed"]))
        if topic:
            self.update_mastery(topic, 12 if stars >= 2 else 8)
        self.update_streak()
        self.add_xp(12 + (stars * 6))
        self.log_event(f"Completed {game_key} challenge: {challenge_id} ({stars} star(s)).")
        self._update_recommendations()
        self.save_state()
        home = self.frames.get("Home")
        if home:
            home.refresh_stats()

    def increment_play_attempt(self, game_key):
        self.state_data["play_state"][game_key]["attempts"] += 1
        self.save_state()

    def _update_recommendations(self):
        recs = []
        viewed = len(self.state_data.get("topics_viewed", []))
        if viewed < 3:
            recs.append("View at least three Learn topics to open more of the roadmap and unlock all game modes.")
        if not self.state_data["play_state"]["debug"]["completed"] and "debug" in self.state_data.get("unlocked_games", []):
            recs.append("Try Debug Detective to build stronger code-reading confidence.")
        weak_topics = sorted(self.state_data.get("mastery", {}).items(), key=lambda item: item[1])[:2]
        if weak_topics:
            recs.append("Focus next on: " + ", ".join(topic for topic, _ in weak_topics) + ".")
        if self.state_data.get("best_quiz_score", 0) < 6:
            recs.append("Use the quiz feedback and weak-area retry mode to improve the overall score.")
        self.state_data["recommended_focus"] = recs[:4] or ["Keep going — your progress summary is strong."]

    def update_quiz_stats(self, score, total, topic_breakdown=None, wrong_topics=None):
        self.state_data["quiz_attempts"] += 1
        self.state_data["last_quiz_score"] = score
        self.state_data["best_quiz_score"] = max(self.state_data["best_quiz_score"], score)
        self.state_data.setdefault("quiz_history", []).append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "score": score, "total": total})
        self.state_data["quiz_history"] = self.state_data["quiz_history"][-10:]
        if topic_breakdown:
            for topic, values in topic_breakdown.items():
                hits, asked = values
                delta = int((hits / max(1, asked)) * 10) if asked else 0
                self.update_mastery(topic, delta)
        if wrong_topics:
            for topic in wrong_topics:
                self.update_mastery(topic, -2)
        self.update_streak()
        self.add_xp(max(10, score * 8))
        self.log_event(f"Completed a quiz attempt: {score}/{total}.")
        self._update_recommendations()
        self.save_state()
        home = self.frames.get("Home")
        if home:
            home.refresh_stats()


def main():
    app = CSExplorerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
