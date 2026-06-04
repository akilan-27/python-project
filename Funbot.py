#!/usr/bin/env python3
"""
  FunBot — Your Simple Fun CLI Chatbot
  No API. No installs. Just Python 3.6+

  RUN:
      python funbot.py
"""

import random
import re
import sys
import time
from datetime import datetime

# ── Data ───────────────────────────────────────────────────────────────────────

JOKES = [
    ("Why don't scientists trust atoms?",         "Because they make up everything!"),
    ("Why did the scarecrow win an award?",        "He was outstanding in his field!"),
    ("Why do programmers prefer dark mode?",       "Because light attracts bugs!"),
    ("What do you call a fake noodle?",            "An impasta!"),
    ("Why did the bicycle fall over?",             "It was two-tired!"),
    ("What do you call cheese that isn't yours?",  "Nacho cheese!"),
    ("Why did the math book look sad?",            "It had too many problems!"),
    ("What do you call a sleeping dinosaur?",      "A dino-snore!"),
    ("Why don't eggs tell jokes?",                 "They'd crack each other up!"),
    ("What do you call a fish without eyes?",      "A fsh!"),
    ("Why can't your nose be 12 inches long?",     "Because then it'd be a foot!"),
    ("I'm reading a book about anti-gravity...",   "It's impossible to put down!"),
]

FUN_FACTS = [
    "A group of flamingos is called a 'flamboyance'.",
    "Honey never spoils — 3000-year-old honey found in Egyptian tombs was still edible!",
    "Octopuses have three hearts and blue blood.",
    "A day on Venus is longer than a year on Venus.",
    "Sharks are older than trees — sharks existed 450M years ago, trees only 350M.",
    "Cleopatra lived closer in time to the Moon landing than to the Great Pyramid.",
    "There are more possible chess games than atoms in the observable universe.",
    "Wombats produce cube-shaped poop — the only animal known to do so!",
    "Crows can recognise human faces and hold grudges for years.",
    "Your nose can detect over 1 trillion different smells.",
]

RIDDLES = [
    {
        "question": "I speak without a mouth and hear without ears. I have no body but come alive with wind. What am I?",
        "answer":   "An echo",
        "hints":    ["It bounces back", "You hear it in mountains or empty rooms"],
    },
    {
        "question": "The more you take, the more you leave behind. What am I?",
        "answer":   "Footsteps",
        "hints":    ["Think about walking", "You make them as you move"],
    },
    {
        "question": "I have cities but no houses, mountains but no trees, water but no fish. What am I?",
        "answer":   "A map",
        "hints":    ["You use it to find your way", "It's flat and shows places"],
    },
    {
        "question": "What has hands but can't clap?",
        "answer":   "A clock",
        "hints":    ["It's on a wall", "It tells you the time"],
    },
    {
        "question": "What has to be broken before you can use it?",
        "answer":   "An egg",
        "hints":    ["You find it in a kitchen", "Chickens lay these"],
    },
    {
        "question": "What gets wetter the more it dries?",
        "answer":   "A towel",
        "hints":    ["You use it after a shower", "It absorbs water"],
    },
    {
        "question": "I have a head and a tail but no body. What am I?",
        "answer":   "A coin",
        "hints":    ["It's used for buying things", "You flip it to make a decision"],
    },
]

WORD_GAME_WORDS = [
    ("elephant", "I am the largest land animal. I never forget."),
    ("volcano",  "I am a mountain that breathes fire."),
    ("compass",  "I always point north even when you're lost."),
    ("rainbow",  "You see me after rain but can never touch me."),
    ("penguin",  "I wear a tuxedo but never fly."),
    ("pyramid",  "I am an ancient wonder with four triangular sides."),
    ("cactus",   "I thrive in the desert and poke you if you get too close."),
    ("thunder",  "I follow lightning but arrive after it."),
]

ROASTS = [
    "You're so slow, you could be lapped by a parked car — but hey, slow and steady! :D",
    "You're like a software update: every time I see you, I think 'not now' — but I always accept you!",
    "You bring everyone such joy... when you leave the room. Just kidding — come back! :)",
    "You're the reason instructions exist on shampoo bottles. Impressive, honestly!",
    "You're a solid 9.99 out of 10. I just failed the maths to confirm it. :D",
]

BOT = "FunBot"

MENU = """
+------------------------------------------+
|  What do you want to do?                 |
|                                          |
|  1. joke      - Hear a joke              |
|  2. fact      - Random fun fact          |
|  3. riddle    - Solve a riddle           |
|  4. game      - Word guessing game       |
|  5. roast     - Get a friendly roast :D  |
|  6. score     - See your score           |
|  7. time      - Current date & time      |
|  8. menu      - Show this menu           |
|  9. bye       - Exit                     |
+------------------------------------------+
"""

# ── State ──────────────────────────────────────────────────────────────────────

mode           = None   # None | "riddle" | "word_game"
current_riddle = None
riddle_hints_used = 0
word_target    = None
word_guesses   = 0
score          = 0
riddles_correct= 0
riddles_total  = 0
used_jokes     = []
used_facts     = []
used_riddles   = []

# ── Helpers ────────────────────────────────────────────────────────────────────

def say(text):
    prefix = f"\n  {BOT}: "
    # Print prefix instantly
    sys.stdout.write(prefix)
    sys.stdout.flush()
    # Type out each character with a small delay
    for i, ch in enumerate(text):
        sys.stdout.write(ch)
        sys.stdout.flush()
        if ch in ".!?":
            time.sleep(0.08)   # slight pause after punctuation
        elif ch == ",":
            time.sleep(0.05)
        elif ch == "\n":
            time.sleep(0.03)
        else:
            time.sleep(0.022)
    sys.stdout.write("\n\n")
    sys.stdout.flush()

def pick(pool, used):
    left = [i for i in range(len(pool)) if i not in used]
    if not left:
        used.clear()
        left = list(range(len(pool)))
    idx = random.choice(left)
    used.append(idx)
    return pool[idx]

# ── Topic handlers ─────────────────────────────────────────────────────────────

def do_joke():
    setup, punchline = pick(JOKES, used_jokes)
    say(f"{setup}\n  Answer: {punchline}")

def do_fact():
    fact = pick(FUN_FACTS, used_facts)
    say(f"Fun fact: {fact}")

def do_riddle():
    global mode, current_riddle, riddle_hints_used, riddles_total
    riddle = pick(RIDDLES, used_riddles)
    current_riddle    = riddle
    riddle_hints_used = 0
    riddles_total    += 1
    mode = "riddle"
    say(
        f"Riddle time!\n\n"
        f"  {riddle['question']}\n\n"
        f"  Type your answer, 'hint' for a clue, or 'skip' to reveal the answer."
    )

def check_riddle(user_input):
    global mode, score, riddles_correct
    low = user_input.lower().strip()

    if low in ("bye", "quit", "exit"):
        mode = None
        do_bye()
        return "quit"

    if low == "skip":
        mode = None
        say(f"No worries! The answer was: {current_riddle['answer']}.\n  Type 'riddle' for another one or 'menu' to pick something else.")
        return

    if low == "hint":
        hints = current_riddle["hints"]
        if riddle_hints_used < len(hints):
            hint_text = hints[riddle_hints_used]
            globals()["riddle_hints_used"] += 1
            say(f"Hint: {hint_text}\n  Keep guessing or type 'skip' to reveal the answer.")
        else:
            say("No more hints! Give it your best guess or type 'skip'.")
        return

    # Check answer
    answer_key = current_riddle["answer"].lower()
    clean_input = re.sub(r"[^a-z ]", "", low)
    matched = any(word in clean_input for word in answer_key.split() if len(word) > 2)

    if matched:
        score          += 10
        riddles_correct += 1
        mode = None
        say(
            f"Correct! Well done!\n"
            f"  Answer: {current_riddle['answer']}\n"
            f"  +10 points! Your score: {score}\n\n"
            f"  Type 'riddle' for another one or 'menu' to pick something else."
        )
    else:
        say(f"Not quite. Try again, type 'hint' for a clue, or 'skip' to reveal the answer.")

def do_word_game():
    global mode, word_target, word_guesses
    word, clue = random.choice(WORD_GAME_WORDS)
    word_target  = word
    word_guesses = 0
    mode = "word_game"
    blanks = "_ " * len(word)
    say(
        f"Word guessing game! You have 6 tries.\n\n"
        f"  Clue: {clue}\n"
        f"  Word: {blanks.strip()}  ({len(word)} letters)\n\n"
        f"  Type your guess or 'skip' to reveal the answer."
    )

def check_word_game(user_input):
    global mode, word_guesses, score
    guess = user_input.lower().strip()

    if guess in ("bye", "quit", "exit"):
        mode = None
        do_bye()
        return "quit"

    if guess == "skip":
        mode = None
        say(f"The word was: {word_target}.\n  Type 'game' to play again or 'menu' for other options.")
        return

    word_guesses += 1

    if guess == word_target:
        pts    = max(5, 20 - (word_guesses - 1) * 3)
        score += pts
        mode   = None
        say(
            f"Correct! The word was '{word_target}'.\n"
            f"  Got it in {word_guesses} guess(es)! +{pts} points!\n"
            f"  Your score: {score}\n\n"
            f"  Type 'game' to play again or 'menu' for other options."
        )
    elif word_guesses >= 6:
        mode = None
        say(f"Out of guesses! The answer was: {word_target}.\n  Type 'game' to try again or 'menu' for other options.")
    else:
        left     = 6 - word_guesses
        revealed = " ".join(c if c in guess else "_" for c in word_target)
        say(f"Wrong guess. Hint: {revealed}  ({left} tries left)\n  Keep guessing or type 'skip' to reveal.")

def do_roast():
    say(random.choice(ROASTS))

def do_score():
    say(
        f"Your score card:\n\n"
        f"  Points  : {score}\n"
        f"  Riddles : {riddles_correct} correct out of {riddles_total}"
    )

def do_time():
    now = datetime.now()
    say(f"{now.strftime('%A, %d %B %Y')} — {now.strftime('%I:%M %p')}")

def do_bye():
    say(f"Goodbye! Thanks for chatting. Final score: {score} points. See you next time!")

# ── Main router ────────────────────────────────────────────────────────────────

def respond(user_input):
    global mode
    low = user_input.lower().strip()

    # If inside a topic, stay in it
    if mode == "riddle":
        check_riddle(user_input)
        return True

    if mode == "word_game":
        check_word_game(user_input)
        return True

    # Top-level commands
    if low in ("bye", "quit", "exit", "/bye", "/quit", "/exit"):
        do_bye()
        return False

    if low in ("joke", "/joke", "1"):
        do_joke()
    elif low in ("fact", "/fact", "2"):
        do_fact()
    elif low in ("riddle", "/riddle", "3"):
        do_riddle()
    elif low in ("game", "/game", "4"):
        do_word_game()
    elif low in ("roast", "/roast", "5"):
        do_roast()
    elif low in ("score", "/score", "6"):
        do_score()
    elif low in ("time", "/time", "7"):
        do_time()
    elif low in ("menu", "/menu", "help", "/help", "8"):
        print(MENU)
    elif re.search(r"\b(hi|hello|hey|howdy)\b", low):
        say("Hey there! Type 'menu' to see what I can do.")
    elif re.search(r"\b(thanks|thank you|thx)\b", low):
        say("You're welcome! :)")
    elif re.search(r"\bhow are you\b", low):
        say("Doing great, thanks for asking! Type 'menu' to pick an activity.")
    else:
        say("I didn't get that. Type 'menu' to see all options.")

    return True


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 46)
    print(f"  Welcome to {BOT}! Your fun offline chatbot.")
    print("=" * 46)
    print(MENU)
    say("Hello! I'm FunBot. Pick an option from the menu above to get started!")

    while True:
        try:
            user_input = input("  You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            do_bye()
            break

        if not user_input:
            continue

        keep_going = respond(user_input)
        if not keep_going:
            break


if __name__ == "__main__":
    main()
