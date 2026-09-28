#!/usr/bin/env python3
"""
Build the user's vocabulary profile from the writing-style corpus, and check a
draft against it.

Usage:
  vocabulary.py build [--cache DIR]
  vocabulary.py check --draft FILE [--exempt FILE] [--cache DIR]

`build` reads every corpus/*.jsonl file in the cache and writes vocabulary.md.
`check` compares a draft with vocabulary.md and prints anything out of voice.
Only segments with author "user" and kind "body" are ever counted; everything
else in the corpus is context.

English reference frequencies come from wordfreq (https://github.com/rspeer/wordfreq),
installed on first run into <cache>/.venv. See references/cache-files.md for
the corpus and vocabulary.md formats, and for wordfreq's credits.

Environment:
  WRITING_STYLE_VENV  Use this venv for wordfreq instead of <cache>/.venv.
  AI_SKILLS_EVAL      When set, never install anything; run without wordfreq
                      unless WRITING_STYLE_VENV already provides it.
"""

import argparse
import datetime
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import venv
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set, Tuple

WORDFREQ_VERSION = "3.1.1"

TOP_WORDS = 50
MIN_SIGNATURE_COUNT = 3
MIN_SIGNATURE_MESSAGES = 3
MAX_SIGNATURES = 40
MAX_PHRASES = 25
MIN_NEGATIVE_MESSAGES = 5
MEDIUM_MIN_WORDS = 300
MEDIUM_RATE_FACTOR = 2.0
UNCOMMON_ZIPF = 4.0
COMMON_ZIPF = 6.0
FALLBACK_COMMON_WORDS = 20
# 10.83 is the G2 critical value for p < 0.001 at one degree of freedom, the
# usual cutoff for keywords in corpus linguistics.
MIN_KEYNESS = 10.83
DRAFT_OVERUSE_MIN_COUNT = 3
DRAFT_OVERUSE_FACTOR = 3.0
SNIPPET_RADIUS = 40
REFERENCE_FLOOR = 1e-9

# Words that became markedly more frequent in writing after LLM assistants
# spread (Kobak et al. 2024, "Delving into LLM-assisted writing in biomedical
# publications through excess vocabulary", arXiv:2406.07016), plus common
# assistant escalations. Listed as never-used when the user's corpus has none.
AI_LEANING_WORDS = (
    "additionally", "align", "bolster", "commendable", "comprehensive",
    "crucial", "delve", "delves", "delving", "elevate", "embark", "endeavor",
    "foster", "furthermore", "garner", "groundbreaking", "harness", "holistic",
    "insightful", "intricate", "invaluable", "landscape", "leverage",
    "meticulous", "meticulously", "moreover", "multifaceted", "notably",
    "noteworthy", "nuanced", "paramount", "pivotal", "realm", "robust",
    "seamless", "seamlessly", "showcase", "showcasing", "streamline",
    "synergy", "tapestry", "testament", "underscore", "underscores",
    "utilize", "vibrant",
)

STRIP_PATTERNS = (
    re.compile(r"```.*?```", re.DOTALL),          # fenced code
    re.compile(r"`[^`\n]*`"),                      # inline code
    re.compile(r"https?://\S+|www\.\S+"),          # URLs
    re.compile(r"<[@#!][^>\s]*>"),                 # Slack mentions and channels
    re.compile(r"\S+@\S+\.\w+"),                   # email addresses
    re.compile(r"(?<!\w)[@#][\w.-]+"),             # @handles and #channels
)
FALLBACK_TOKEN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")
HAS_DIGIT = re.compile(r"\d")


# ---------------------------------------------------------------------------
# wordfreq bootstrap


def venv_dir(cache: str) -> str:
    return os.environ.get("WRITING_STYLE_VENV") or os.path.join(cache, ".venv")


def site_packages(cache: str) -> str:
    """The venv's site-packages for this interpreter's Python version."""
    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    return os.path.join(venv_dir(cache), "lib", version, "site-packages")


def install_wordfreq(cache: str) -> bool:
    """Create the venv and install the pinned wordfreq. Returns success."""
    target = venv_dir(cache)
    print(f"Installing wordfreq {WORDFREQ_VERSION} into {target} (first run only)...", file=sys.stderr)
    try:
        venv.create(target, clear=True, with_pip=True)
        pip = [os.path.join(target, "bin", "python3"), "-m", "pip", "install", "--quiet", "--disable-pip-version-check"]
        subprocess.run(pip + [f"wordfreq=={WORDFREQ_VERSION}"], check=True)
        return True
    except (OSError, subprocess.CalledProcessError) as err:
        print(f"Could not install wordfreq ({err}); continuing without it.", file=sys.stderr)
        return False


def ensure_wordfreq(cache: str) -> None:
    """Make wordfreq importable from the venv, installing it if allowed.

    The venv is built with this same interpreter, so its compiled dependencies
    match; a venv for another Python version is rebuilt.
    """
    if importlib.util.find_spec("wordfreq"):
        return
    site = site_packages(cache)
    if not os.path.isdir(site):
        if os.environ.get("AI_SKILLS_EVAL") or not install_wordfreq(cache):
            return
    sys.path.insert(0, site)
    if not importlib.util.find_spec("wordfreq"):
        print(f"{venv_dir(cache)} has no wordfreq; delete it to reinstall. Continuing without it.", file=sys.stderr)


class Reference:
    """English word frequencies and tokenization, from wordfreq when present."""

    def __init__(self) -> None:
        try:
            import wordfreq
            self._wf = wordfreq
        except ImportError:
            self._wf = None

    @property
    def available(self) -> bool:
        return self._wf is not None

    def describe(self) -> str:
        if self._wf:
            return f"wordfreq {getattr(self._wf, '__version__', WORDFREQ_VERSION)}, English 'large' list"
        return "none (wordfreq unavailable): keyness and rarity checks skipped"

    def tokenize(self, text: str) -> List[str]:
        text = clean_text(text)
        if self._wf:
            tokens = self._wf.tokenize(text, "en")
        else:
            tokens = [t.replace("’", "'") for t in FALLBACK_TOKEN.findall(text.lower())]
        return [t for t in tokens if not HAS_DIGIT.search(t)]

    def frequency(self, word: str) -> Optional[float]:
        if not self._wf:
            return None
        return self._wf.word_frequency(word, "en", wordlist="large")

    def zipf(self, word: str) -> Optional[float]:
        if not self._wf:
            return None
        return self._wf.zipf_frequency(word, "en", wordlist="large")


def clean_text(text: str) -> str:
    for pattern in STRIP_PATTERNS:
        text = pattern.sub(" ", text)
    return text


# ---------------------------------------------------------------------------
# Corpus


class Segment:
    def __init__(self, record: dict, medium: str) -> None:
        self.msg = record["msg"]
        self.text = record["text"]
        self.match = record["match"]
        self.date = record.get("date", "")
        self.medium = medium


def medium_of(filename: str) -> str:
    return os.path.basename(filename).split("-", 1)[0]


def validate(record: dict) -> Optional[str]:
    """Return why a record can't be counted as the user's, or None if it can."""
    for field in ("msg", "author", "kind", "text"):
        if not isinstance(record.get(field), str):
            return f"missing {field}"
    if record["author"] not in ("user", "other", "unknown"):
        return f"invalid author {record['author']!r}"
    if record["author"] == "user" and record.get("match") not in ("identifier", "name"):
        return "user segment without match"
    return None


def read_corpus(cache: str) -> Tuple[List[Segment], List[str], List[str]]:
    """Return counted user body segments, the files read, and warnings."""
    corpus_dir = os.path.join(cache, "corpus")
    files = sorted(
        os.path.join(corpus_dir, f) for f in os.listdir(corpus_dir) if f.endswith(".jsonl")
    ) if os.path.isdir(corpus_dir) else []
    segments: List[Segment] = []
    warnings: List[str] = []
    seen: Set[Tuple[str, str]] = set()
    for path in files:
        segments.extend(read_file(path, seen, warnings))
    return segments, files, warnings


def read_file(path: str, seen: Set[Tuple[str, str]], warnings: List[str]) -> List[Segment]:
    segments = []
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            where = f"{os.path.basename(path)}:{number}"
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                warnings.append(f"{where}: not valid JSON, skipped")
                continue
            problem = validate(record) if isinstance(record, dict) else "not an object"
            if problem:
                warnings.append(f"{where}: {problem}, not counted")
                continue
            if record["author"] != "user" or record["kind"] != "body":
                continue
            key = (record["msg"], record["text"])
            if key in seen:
                continue
            seen.add(key)
            segments.append(Segment(record, medium_of(path)))
    return segments


# ---------------------------------------------------------------------------
# Profile


class Profile:
    def __init__(self, segments: List[Segment], reference: Reference) -> None:
        self.reference = reference
        self.segments = segments
        self.counts: Counter = Counter()
        self.messages: Dict[str, Set[str]] = defaultdict(set)
        self.by_medium: Dict[str, Counter] = defaultdict(Counter)
        self.name_match_words = 0
        self.message_ids: Set[str] = set()
        self.ngrams: Counter = Counter()
        self.ngram_messages: Dict[Tuple[str, ...], Set[str]] = defaultdict(set)
        for segment in segments:
            self._add(segment)
        self.total = sum(self.counts.values())

    def _add(self, segment: Segment) -> None:
        tokens = self.reference.tokenize(segment.text)
        self.message_ids.add(segment.msg)
        self.counts.update(tokens)
        self.by_medium[segment.medium].update(tokens)
        if segment.match == "name":
            self.name_match_words += len(tokens)
        for token in tokens:
            self.messages[token].add(segment.msg)
        for size in (2, 3):
            for i in range(len(tokens) - size + 1):
                gram = tuple(tokens[i:i + size])
                self.ngrams[gram] += 1
                self.ngram_messages[gram].add(segment.msg)

    def rate(self, word: str, counts: Optional[Counter] = None) -> float:
        counts = counts or self.counts
        total = sum(counts.values())
        return 1000.0 * counts[word] / total if total else 0.0

    def top_words(self) -> List[str]:
        return [w for w, _ in self.counts.most_common(TOP_WORDS)]

    def keyness(self, word: str) -> Optional[float]:
        """Log-likelihood (G2) of the user's count against the English rate."""
        freq = self.reference.frequency(word)
        if freq is None:
            return None
        observed = self.counts[word]
        expected = max(freq, REFERENCE_FLOOR) * self.total
        if observed <= expected:
            return 0.0
        return 2.0 * (observed * math.log(observed / expected) - (observed - expected))

    def signatures(self) -> List[Tuple[str, float]]:
        scored = []
        for word, count in self.counts.items():
            if count < MIN_SIGNATURE_COUNT or len(self.messages[word]) < MIN_SIGNATURE_MESSAGES:
                continue
            score = self.keyness(word)
            if score and score >= MIN_KEYNESS:
                scored.append((word, score))
        scored.sort(key=lambda item: -item[1])
        return scored[:MAX_SIGNATURES]

    def is_common(self, word: str) -> bool:
        """Very common English words, which make phrases like "of the" noise."""
        zipf = self.reference.zipf(word)
        if zipf is None:
            return word in {w for w, _ in self.counts.most_common(FALLBACK_COMMON_WORDS)}
        return zipf >= COMMON_ZIPF

    def phrases(self) -> List[Tuple[Tuple[str, ...], int]]:
        found = [
            (gram, count) for gram, count in self.ngrams.items()
            if count >= MIN_SIGNATURE_COUNT
            and len(self.ngram_messages[gram]) >= MIN_SIGNATURE_MESSAGES
            and not all(self.is_common(token) for token in gram)
        ]
        found.sort(key=lambda item: (-item[1], -len(item[0])))
        return found[:MAX_PHRASES]

    def medium_differences(self, word: str) -> List[str]:
        overall = self.rate(word)
        notes = []
        for medium, counts in sorted(self.by_medium.items()):
            if sum(counts.values()) < MEDIUM_MIN_WORDS or not overall:
                continue
            medium_rate = self.rate(word, counts)
            if medium_rate >= overall * MEDIUM_RATE_FACTOR or medium_rate <= overall / MEDIUM_RATE_FACTOR:
                notes.append(f"{medium} {medium_rate:.1f}")
        return notes

    def snippet(self, phrase: str) -> str:
        pattern = re.compile(r"(?<!\w)" + r"\W+".join(map(re.escape, phrase.split())) + r"(?!\w)", re.IGNORECASE)
        for segment in self.segments:
            text = " ".join(segment.text.split())
            found = pattern.search(text)
            if found:
                start = max(0, found.start() - SNIPPET_RADIUS)
                end = min(len(text), found.end() + SNIPPET_RADIUS)
                prefix = "..." if start else ""
                suffix = "..." if end < len(text) else ""
                return f"{prefix}{text[start:end].strip()}{suffix}"
        return ""


# ---------------------------------------------------------------------------
# vocabulary.md


def render(profile: Profile, files: List[str], warnings: List[str]) -> str:
    lines = header_lines(profile, files)
    lines += function_word_lines(profile)
    lines += signature_lines(profile)
    lines += phrase_lines(profile)
    lines += never_used_lines(profile)
    if warnings:
        lines += ["", "## Corpus warnings", ""] + [f"- {w}" for w in warnings]
    lines += lexicon_lines(profile)
    return "\n".join(lines) + "\n"


def header_lines(profile: Profile, files: List[str]) -> List[str]:
    dates = sorted(s.date for s in profile.segments if s.date)
    span = f"{dates[0][:10]} -> {dates[-1][:10]}" if dates else "undated"
    share = 100.0 * profile.name_match_words / profile.total if profile.total else 0.0
    return [
        "# Vocabulary",
        "",
        f"Built:       {datetime.date.today().isoformat()}",
        f"Corpus:      {plural(len(files), 'file')}, {len(profile.message_ids)} messages, {profile.total} counted words, {span}",
        f"Name match:  {profile.name_match_words} of {profile.total} counted words ({share:.0f}%) from display-name matches",
        f"Reference:   {profile.reference.describe()}",
        "Counted:     segments with author user and kind body only",
    ]


def function_word_lines(profile: Profile) -> List[str]:
    lines = ["", "## Most frequent words", "", "Rate per 1,000 words, yours vs general English.", "",
             "| word | yours | English | by medium |", "|---|---|---|---|"]
    for word in profile.top_words():
        freq = profile.reference.frequency(word)
        english = f"{1000.0 * freq:.3g}" if freq is not None else "-"
        mediums = ", ".join(profile.medium_differences(word)) or "-"
        lines.append(f"| {word} | {profile.rate(word):.1f} | {english} | {mediums} |")
    return lines


def signature_lines(profile: Profile) -> List[str]:
    lines = ["", "## Signature words", ""]
    if not profile.reference.available:
        return lines + ["Skipped: needs wordfreq for the English baseline."]
    lines += ["Used far more than general English. G2 is the log-likelihood keyness score.", "",
              "| word | count | messages | G2 | snippet |", "|---|---|---|---|---|"]
    for word, score in profile.signatures():
        lines.append(f"| {word} | {profile.counts[word]} | {len(profile.messages[word])} | {score:.0f} | {table_cell(profile.snippet(word))} |")
    return lines


def phrase_lines(profile: Profile) -> List[str]:
    lines = ["", "## Recurring phrases", "",
             "Word combinations in 3 or more messages (co-selection).", "",
             "| phrase | count | messages | snippet |", "|---|---|---|---|"]
    for gram, count in profile.phrases():
        phrase = " ".join(gram)
        lines.append(f"| {phrase} | {count} | {len(profile.ngram_messages[gram])} | {table_cell(profile.snippet(phrase))} |")
    return lines


def never_used_lines(profile: Profile) -> List[str]:
    messages = len(profile.message_ids)
    lines = ["", "## Never used", ""]
    if messages < MIN_NEGATIVE_MESSAGES:
        return lines + [f"Not enough evidence: {messages} messages, needs {MIN_NEGATIVE_MESSAGES}."]
    unused = [w for w in AI_LEANING_WORDS if not profile.counts[w]]
    used = [f"{w} ({profile.counts[w]})" for w in AI_LEANING_WORDS if profile.counts[w]]
    lines.append(f"AI-leaning words with 0 uses in {messages} messages:")
    lines.append("")
    lines.append(", ".join(unused) or "(none)")
    if used:
        lines += ["", "AI-leaning words you do use, so the draft check allows them:", "", ", ".join(used)]
    return lines


def lexicon_lines(profile: Profile) -> List[str]:
    lines = ["", "## Lexicon", "", f"Every counted word, {len(profile.counts)} in all.", "", "```"]
    for word, count in sorted(profile.counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"{word}\t{count}")
    return lines + ["```"]


def plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def table_cell(text: str) -> str:
    return text.replace("|", "\\|")


# ---------------------------------------------------------------------------
# check


def load_vocabulary(cache: str) -> Tuple[Dict[str, int], Dict[str, float], Set[str]]:
    """Return the lexicon, the top-word rates, and the never-used words."""
    path = os.path.join(cache, "vocabulary.md")
    if not os.path.exists(path):
        sys.exit(f"No vocabulary.md in {cache}. Run: vocabulary.py build")
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    lexicon = {}
    block = re.search(r"## Lexicon.*?```\n(.*?)```", text, re.DOTALL)
    for line in (block.group(1).splitlines() if block else []):
        word, _, count = line.partition("\t")
        lexicon[word] = int(count)
    top = re.search(r"## Most frequent words\n(.*?)\n## ", text, re.DOTALL)
    rates = {m.group(1): float(m.group(2))
             for m in re.finditer(r"^\| (\S+) \| ([\d.]+) \| ", top.group(1) if top else "", re.MULTILINE)}
    never = set()
    unused = re.search(r"AI-leaning words with 0 uses[^\n]*\n\n([^\n]*)", text)
    if unused and unused.group(1) != "(none)":
        never = {w.strip() for w in unused.group(1).split(",")}
    return lexicon, rates, never


def check(cache: str, draft_path: str, exempt_path: Optional[str], reference: Reference) -> int:
    lexicon, rates, never = load_vocabulary(cache)
    with open(draft_path, encoding="utf-8") as handle:
        tokens = reference.tokenize(handle.read())
    exempt: Set[str] = set()
    if exempt_path:
        with open(exempt_path, encoding="utf-8") as handle:
            exempt = set(reference.tokenize(handle.read()))
    draft = Counter(t for t in tokens if t not in exempt)
    findings = never_used_findings(draft, never) + unseen_findings(draft, lexicon, never, reference) \
        + overuse_findings(Counter(tokens), rates, len(tokens))
    print(f"Draft: {len(tokens)} words. Reference: {reference.describe()}")
    if not findings:
        print("No vocabulary flags.")
    for finding in findings:
        print(f"- {finding}")
    return 0


def never_used_findings(draft: Counter, never: Set[str]) -> List[str]:
    return [f"never used: \"{w}\" (0 in your corpus)" for w in sorted(draft) if w in never]


def unseen_findings(draft: Counter, lexicon: Dict[str, int], never: Set[str], reference: Reference) -> List[str]:
    findings = []
    for word in sorted(draft):
        if word in lexicon or word in never:
            continue
        zipf = reference.zipf(word)
        if zipf is None:
            findings.append(f"unseen: \"{word}\" (not in your corpus; no English baseline to judge rarity)")
        elif zipf < UNCOMMON_ZIPF:
            findings.append(f"unseen and uncommon: \"{word}\" (not in your corpus; Zipf {zipf:.1f} in English)")
    return findings


def overuse_findings(draft: Counter, rates: Dict[str, float], total: int) -> List[str]:
    findings = []
    for word, rate in sorted(rates.items()):
        count = draft[word]
        draft_rate = 1000.0 * count / total if total else 0.0
        if count >= DRAFT_OVERUSE_MIN_COUNT and draft_rate > rate * DRAFT_OVERUSE_FACTOR:
            findings.append(f"overused: \"{word}\" {draft_rate:.0f} per 1,000 words vs your {rate:.1f}")
    return findings


# ---------------------------------------------------------------------------


def build(cache: str, reference: Reference) -> int:
    segments, files, warnings = read_corpus(cache)
    if not segments:
        sys.exit(f"No counted segments in {os.path.join(cache, 'corpus')}; nothing to build.")
    profile = Profile(segments, reference)
    path = os.path.join(cache, "vocabulary.md")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(render(profile, files, warnings))
    print(f"Wrote {path}: {len(profile.message_ids)} messages, {profile.total} counted words, "
          f"{len(warnings)} warnings. Reference: {reference.describe()}")
    for warning in warnings:
        print(f"  warning: {warning}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cache", default=os.path.join(os.path.expanduser("~"), "writing-style"),
                        help="style cache directory (default: $HOME/writing-style)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build", help="write vocabulary.md from corpus/*.jsonl")
    check_parser = commands.add_parser("check", help="check a draft against vocabulary.md")
    check_parser.add_argument("--draft", required=True, help="file holding the draft text")
    check_parser.add_argument("--exempt", help="file holding the user's request; its words are never flagged")
    args = parser.parse_args()
    cache = os.path.abspath(args.cache)
    if not os.path.isdir(cache):
        sys.exit(f"No style cache at {cache}.")
    ensure_wordfreq(cache)
    reference = Reference()
    if args.command == "build":
        return build(cache, reference)
    return check(cache, args.draft, args.exempt, reference)


if __name__ == "__main__":
    sys.exit(main())
