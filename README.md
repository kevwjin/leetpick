# Leetpick

Leetpick is a small CLI that helps you work through the NeetCode 250 (Medium/Hard subset). It randomly suggests problems without repetition, lets you manually toggle completion, and tracks progress in a hidden `.state/` directory.

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
   python cli.py reset
   ```

## Commands
- `pick` – Suggests a random problem that is not marked complete.
- `status` – Shows progress in the problem bank (`X/190 completed`).
- `toggle <problem_id>` – Marks/unmarks a problem given its LeetCode ID.
- `reset` – Unmarks everything as incomplete again.

### Example
```
$ python cli.py pick
Suggested: [Medium] Minimum Height Trees — Graphs
https://leetcode.com/problems/minimum-height-trees/
Use "toggle 310" to mark complete when done.

$ python cli.py toggle 310
Marked 310 as completed.

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
