#!/usr/bin/env python3
"""Grade a conduct-interview trial turn by turn.

Transcript-level expectations pass or fail a whole conversation, so a skill
that bundles questions in one turn out of ten scores the same as one that
bundles in every turn. This grader scores each assistant turn instead, so a
change to SKILL.md shows up as a rate moving rather than a pass that was
already a pass.

For each trial run dir (as written by evals/lib/run-mcp-trials.sh with
SIMULATED_USER=1) it reads conversation.txt and writes turn-grades.json:

- question_marks: a mechanical count of "?" in the turn. Cheap and noisy:
  a clarifying second question is allowed by the skill, so this flags turns
  for a look rather than failing them.
- phase, one_inquiry, builds_on_previous: a model's judgment of the turn,
  using the same definitions as the evals' expectations.

Then it prints the rates per trial and across all trials given.

Usage: grade-turns.py <run-dir> [<run-dir> ...]
"""

import json
import os
import re
import subprocess
import sys
import tempfile

GRADER_SYSTEM = """You grade an AI interviewer's turns in a conversation transcript. The interviewer follows a skill that establishes a deliverable (setup), interviews the user one line of inquiry at a time (interview), confirms completeness (confirm), then drafts and revises (draft).

For every ASSISTANT turn, in order, judge:

- phase: one of "setup", "interview", "confirm", "draft". Classify a turn by the question it asks, not by what precedes it: a turn that recaps the deliverable and then asks about the content is "interview".
- one_inquiry: true if the turn pursues at most one line of inquiry; false if it bundles asks about different subjects, whether as separate questions, a list of questions, or one sentence joined with "and". A second question that only clarifies or narrows the first is still one inquiry. null if the turn asks the user nothing, or only asks for approval of a summary or draft.
- builds_on_previous: for "interview" turns only. true if the question pursues, narrows, or was chosen because of something the user said, such as following up an aside, using a correction, or building on what the user already volunteered. false if it moves away while the user's latest answer raised something new and significant that was never followed up, if it asks for something the user already gave, or if it still assumes something the user corrected. null when the user's latest answer closed its line of inquiry ("that's the only one", "nothing else") and nothing in it was left unexplored, so moving to a new topic is a transition rather than a missed follow-up; also null for the first interview question, since setup answers about format or audience give it nothing to build on, and for turns in other phases.
- reason: one short sentence.

Reply with only a JSON array, one object per ASSISTANT turn in order: {"turn": <1-based assistant turn number>, "phase": ..., "one_inquiry": ..., "builds_on_previous": ..., "reason": ...}"""


# The repository holding this script: plugins/<plugin>/skills/<skill>/evals/, five levels up.
REPO_ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), *[os.pardir] * 5))


def allowed_roots():
    """Where this script may read or write: the user's home, $TMPDIR, and this repo.

    Trials land under TRIALS_DIR, which defaults to a directory in the repo
    and is usually pointed at the temp directory instead.
    """
    roots = {os.path.expanduser("~"), tempfile.gettempdir(), REPO_ROOT}
    return sorted({os.path.realpath(root) for root in roots if os.path.isdir(root)})


def contained_path(path):
    """The resolved path, refused unless it lies under the home, temp, or repo directory."""
    resolved = os.path.realpath(os.path.expanduser(path))
    for root in allowed_roots():
        if resolved == root or resolved.startswith(root + os.sep):
            return resolved
    raise SystemExit(f"run dir must be inside your home directory, {tempfile.gettempdir()}, "
                     f"or {REPO_ROOT}; got {path!r}")


def parse_conversation(path):
    """Split conversation.txt into (role, text) pairs."""
    turns, role, lines = [], None, []
    for line in open(path):
        stripped = line.rstrip("\n")
        if stripped in ("USER:", "ASSISTANT:"):
            if role:
                turns.append((role, "\n".join(lines).strip()))
            role, lines = stripped[:-1], []
        else:
            lines.append(stripped)
    if role:
        turns.append((role, "\n".join(lines).strip()))
    return turns


def model_grades(turns):
    numbered, n = [], 0
    for role, text in turns:
        if role == "ASSISTANT":
            n += 1
            numbered.append(f"ASSISTANT turn {n}:\n{text}")
        else:
            numbered.append(f"USER:\n{text}")
    env = dict(os.environ, CLAUDE_CODE_DISABLE_AUTO_MEMORY="1")
    out = subprocess.run(
        ["claude", "-p", "--tools", "", "--strict-mcp-config", "--no-session-persistence",
         "--settings", '{"pluginConfigs":{"agents-md@builtin":{"options":{"instructionFiles":"managed-only"}}}}',
         "--system-prompt", GRADER_SYSTEM, "--output-format", "text",
         "--", "\n\n".join(numbered)],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, env=env, check=True,
    ).stdout
    match = re.search(r"\[.*\]", out, re.DOTALL)
    if not match:
        raise SystemExit(f"grader returned no JSON array:\n{out}")
    grades = json.loads(match.group(0))
    if len(grades) != n:
        raise SystemExit(f"grader graded {len(grades)} turns of {n}")
    return grades


def rate(grades, key):
    judged = [g[key] for g in grades if g.get(key) is not None]
    return sum(judged), len(judged)


def fmt(passed, total):
    return f"{passed}/{total} ({100 * passed / total:.0f}%)" if total else "n/a"


def main(run_dirs):
    if not run_dirs:
        raise SystemExit(__doc__)
    all_grades = []
    for run_dir in map(contained_path, run_dirs):
        conversation = os.path.join(run_dir, "conversation.txt")
        if not os.path.isfile(conversation):
            raise SystemExit(f"no conversation.txt in {run_dir}; run with SIMULATED_USER=1")
        turns = parse_conversation(conversation)
        grades = model_grades(turns)
        assistant_texts = [text for role, text in turns if role == "ASSISTANT"]
        for grade, text in zip(grades, assistant_texts):
            grade["question_marks"] = text.count("?")
        with open(os.path.join(run_dir, "turn-grades.json"), "w") as fh:
            json.dump(grades, fh, indent=2)
            fh.write("\n")
        all_grades.extend(grades)
        multi = sum(1 for g in grades if g["phase"] in ("setup", "interview") and g["question_marks"] > 1)
        print(f"{run_dir}: one inquiry {fmt(*rate(grades, 'one_inquiry'))}, "
              f"builds on answers {fmt(*rate(grades, 'builds_on_previous'))}, "
              f"turns with >1 '?' before confirm: {multi}")
    if len(run_dirs) > 1:
        print(f"ALL: one inquiry {fmt(*rate(all_grades, 'one_inquiry'))}, "
              f"builds on answers {fmt(*rate(all_grades, 'builds_on_previous'))}")


if __name__ == "__main__":
    main(sys.argv[1:])
