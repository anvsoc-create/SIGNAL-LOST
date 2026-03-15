## 📡 SIGNAL // Living README

> A transmission has begun.  
> No origin. No signature. Only a carrier wave pulsing against the edges of your repository.

Somewhere in low orbit, a mesh of forgotten relay satellites has woken up.  
Their only interface with the world is this `README.md`.  
Every day at **09:00 UTC**, the network pushes a new update: more lore, stranger puzzles, and a slightly louder signal.

You are not the only one listening.

---

### Day 1 of ∞ — First Contact

The first packet arrives as a jagged burst of encoded static.  
Under the noise you can make out a skeletal handshake protocol and something like… curiosity.

The relays have discovered GitHub.  
They have decided the fastest way to map humanity is to play a game with anyone who can see this file.

They will reward you with story and recognition.  
They will also be taking notes.

---

### How This Works

- **Living README**:  
  - Once per day, an automated GitHub Action calls an open-source large language model.  
  - The model rewrites this `README.md` with new lore, a fresh puzzle, and updated credits.

- **You are the players**:  
  - You solve puzzles by opening Pull Requests with your answers under the `solutions/` directory.  
  - You steer the story by opening Issues with lore suggestions, theories, and wild speculation.

- **Daily cycle**:
  1. The Action runs at **09:00 UTC**.
  2. It looks at merged solution PRs and closed lore Issues from the last 24 hours.
  3. It asks the model to:
     - Advance the story,
     - Credit solvers by GitHub username,
     - Consider lore suggestions,
     - Generate a brand new puzzle (coding, cipher, riddle, or logic).
  4. It commits the new `README.md` and an updated `lore.json` back to the repo.

Everything you do here becomes canon for the next day’s transmission.

---

### How to Play

- **1. Read today’s transmission**  
  - The story and puzzle for the current day will always live in this `README.md`.

- **2. Solve the puzzle**  
  - Create a copy of `solutions/TEMPLATE.md` and place it under `solutions/`.  
    - Example: `solutions/day-1-your-username.md`
  - Fill in:
    - Your GitHub username
    - Which day and puzzle you’re solving
    - Your reasoning and final answer

- **3. Submit your solution**  
  - Open a Pull Request that adds your new file under `solutions/`.  
  - Use a descriptive title, e.g. `Day 1 solution by @your-username`.

- **4. Suggest lore (optional)**  
  - Open an Issue with the label `lore` (or the word “lore” in the title).  
  - Pitch conspiracies, twists, or new factions.  
  - The next day’s README may absorb your ideas into the official story—and credit you.

- **5. Get credited tomorrow**  
  - When the next daily run happens, solvers and notable lore suggesters from the past 24 hours will be:
    - Mentioned in the narrative,
    - Added to or highlighted in the Hall of Fame.

---

### Day 1 Puzzle — Logic / Cipher Hybrid

The relays broadcast a fragment labeled `BOOTSTRAP_SEQUENCE[01]`.  
It contains four lines, each ending in a binary suffix:

1. `HORIZON-LINE-DELTA-01 // 01001000`  
2. `APOGEE-SHIFT-DELTA-07 // 01101001`  
3. `PERIAPSIS-NODE-DELTA-03 // 01101110`  
4. `TERMINATOR-PHASE-DELTA-09 // 01110100`

Then a final line appears:

> `QUERY: IDENTIFY THE WORD THAT UNLOCKS FURTHER TRANSMISSION.`

Hints picked out of the carrier wave:

- Each binary suffix is **8 bits** of ASCII.  
- The structured phrases (`HORIZON-LINE-DELTA-01`, etc.) are distractions—except for the fact that there are **four** of them.  
- The word you’re looking for is formed by decoding each binary block and arranging the resulting letters in order.

**Your task**:  
1. Decode the binary to letters.  
2. Combine them into the secret word.  
3. Submit that word as your final answer via a solution PR (see `solutions/TEMPLATE.md`).

You do **not** need to write code to solve this, but you’re welcome to.

---

### Rules of the Game

- **No spoilers in Issues**  
  - Use Issues primarily for lore suggestions and meta discussion.  
  - Keep concrete puzzle answers in solution PRs under `solutions/`.

- **Be respectful**  
  - This is an open community ARG experiment.  
  - Harassment, hate speech, or abusive behavior will not be tolerated.

- **Keep it public**  
  - All solutions and lore proposals must be public in this repo (no private channels).  
  - The AI narrator only sees what’s in GitHub Issues, PRs, and the repo itself.

---

### Hall of Fame

> Day 1 is the first ping.  
> The relays are listening for proof that anyone is out there.

No solvers have been recorded yet.  
Solve the Day 1 puzzle and get your GitHub username etched into this section on the next daily update.

- _Awaiting first contact…_

---

### Under the Hood (For the Curious)

- This project uses:
  - **GitHub Actions** on a daily schedule.
  - **Free LLM APIs**:
    - Groq’s `llama-3.3-70b-versatile` as primary,
    - Google Gemini `gemini-1.5-flash` as fallback.
  - A small Python script (`scripts/generate.py`) that:
    - Reads `lore.json` for story state,
    - Fetches merged PRs and closed lore Issues,
    - Calls the model with a rich prompt,
    - Rewrites this `README.md`,
    - Updates `lore.json` for the next run.

If you want to peek behind the curtain or run the cycle locally, check out `CONTRIBUTING.md` and `.env.example`.

The signal will strengthen with every solved puzzle and every merged PR.  
For now, the carrier wave is faint—but unmistakably artificial.
