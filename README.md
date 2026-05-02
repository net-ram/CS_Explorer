# CS Explorer

CS Explorer is a Python educational application for learners aged 14 to 17. It combines short teaching content, interactive play activities, quiz-based checking, saved learner profiles, and visible progress tracking in one desktop app.

## Run the app

Keep the project folder structure unchanged, open a terminal or Command Prompt in the project root, and run:

```bash
python artefact.py
```

## Project structure

```text
artefact.py
artefact.docx
README.md
cs_explorer_logo_final.png
cs_explorer/
  __init__.py
  app.py
  config.py
  content.py
  pages.py
  widgets.py
```

## Main sections

- **Home** shows progress, the learning path, recent activity, badges, XP, level, and streak information.
- **Learn** explains the six core topics: Programming, Algorithms, Cybersecurity, Artificial Intelligence, Computational Thinking, and Problem Solving.
- **Play** provides interactive practice activities.
- **Quiz** checks understanding with scored questions and topic feedback.
- **About** explains the aim of the app, who it is for, progress tracking, and accessibility features.

## Main features

- Profile creation, switching, renaming, deletion, and local progress saving
- Emoji avatars and optional uploaded image avatars
- A Home progress map showing what is complete, what is unlocked, and what comes next
- XP, levels, badges, recent activity, and learning streak tracking
- Learn pages with:
  - topic overview
  - real-life relevance
  - key points
  - example scenarios
  - key terms with definitions
  - deeper reading
  - career links
- Play activities including:
  - **Algorithm Builder**: drag steps into order, unlock harder sequences, and view a trace animation after success
  - **Flowchart Challenge**: drag the missing symbol into place and follow the visual branches
  - **Binary Puzzle**: match binary and decimal cards in timed Build the Byte rounds
  - **Logic Gate Mini Game**: toggle switches and watch the output lamp change live
  - **Spot-the-Bug Race**: click the buggy line, then choose the best fix
  - **Phishing Email Detective**: inspect a fake inbox, click suspicious clues, then decide safe or unsafe
  - **Debug Detective** and **Cyber Safe Choices** for additional question-based practice
- Quiz score tracking with difficulty levels, shuffled options, and topic-based feedback
- Accessibility support including large text, high contrast, dark mode, keyboard navigation, and visible focus outlines
- Exportable TXT progress reports

## Files created at runtime

- `cs_explorer_state.json` stores profiles and progress locally
- `profile_avatars/` stores uploaded avatar images
- exported TXT progress reports are saved beside the app

## Notes

- Keep `cs_explorer_logo_final.png` in the project root so the sidebar logo loads correctly.
- The project should be extracted before running the app.
