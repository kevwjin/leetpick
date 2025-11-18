# LeetPick

LeetPick is a small CLI that helps you work through the NeetCode 250 (Medium/Hard subset). It randomly suggests problems without repetition, lets you manually toggle completion, and tracks progress in a hidden `.state/` directory.

**Terminology:**  
The **problem bank** is initialized with the full list of problems loaded from the dataset found at `datasets/nc250_geMed.json`.
Problems marked complete are removed from the problem bank until they are unmarked or until you run `reset`.

## Dataset
The CLI expects the curated dataset at `datasets/nc250_geMed.json`. Each entry includes the canonical LeetCode `id`, `title`, `difficulty`, `topic`, and `link`. If you move the dataset elsewhere, pass `--dataset /absolute/path/to/file.json` when running commands.

## Quick start
1. Ensure Python 3.10+ is available.
2. (Optional) Symlink the CLI to your PATH for global access:
   ```bash
   ln -s /absolute/path/to/cli.py ~/.local/bin/leetpick
   chmod +x ~/.local/bin/leetpick
   ```
3. Run commands:
   ```bash
   python cli.py pick
   python cli.py status
   python cli.py toggle <problem_id>
   python cli.py remind <problem_id> [--days 3]
   python cli.py reset
   ```

## Commands
- `pick` – Pick a random incomplete problem
- `status` – Show progress (e.g., `X/190 completed (X.X%)`)
- `toggle <problem_id>` – Toggle problem completion given LeetCode problem number
- `remind <problem_id> [--days N]` – Schedule a reminder to revisit a problem (default 3 days)
- `reset` – Unmarks completion for all problems so they can be picked again

### Example
```
$ python cli.py pick
Reminder(s):
 - [Hard] <problem-link>
   Use "leetpick toggle <id>" to mark complete when done.

Suggestion(s):
 - [Medium] https://leetcode.com/problems/minimum-height-trees/
   Use "leetpick toggle 310" to mark complete when done.

$ python cli.py remind 310
Reminder set for problem 310 in 3 day(s).

$ python cli.py toggle 310
Marked 310 as complete.

$ python cli.py status
1/190 completed (0.5%)

$ python cli.py toggle 310
Moved 310 back into the problem bank.

$ python cli.py reset
Progress reset. Problem bank refilled with all problems.
```

## Notes
- State lives at `.state/nc250_geMed_state.json` relative to where you run the CLI; use `--state` to override with an absolute path if you want a single global state file.
- Add `.state/` and `.tmp_leetcode_all.json` to `.gitignore` before committing so personal progress and API dumps stay local.
- On Nix-based setups, you can wrap the CLI in a derivation/flake, or simply use the symlink approach above.
