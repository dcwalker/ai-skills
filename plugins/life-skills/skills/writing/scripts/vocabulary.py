#!/usr/bin/env python3
"""
Keep the writing-style corpus, build the user's vocabulary profile from it, and
check a draft against that profile.

Usage:
  vocabulary.py save --card SLUG --source NAME --input FILE [--me ID ...] [--cache DIR]
  vocabulary.py check --draft FILE --exempt FILE [--cache DIR]
  vocabulary.py build [--cache DIR]

--cache is accepted before or after the subcommand.

`save` labels a batch of messages and appends them to corpus/<SLUG>.jsonl.
Messages from an identifier in identity.md (or --me) are the user's; their
greeting, closing, signature, quoted replies, and forwarded text are split off
into their own segments. Everything else is labeled as someone else's.
`check` rebuilds vocabulary.md when the corpus has changed, then compares a
draft with it and prints anything out of voice.
`build` rebuilds vocabulary.md on its own.
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
DRAFT_OVERUSE_MIN_WORDS = 150
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
    re.compile(r"<[@#!][^>]*>"),                   # Slack mentions and channels
    re.compile(r"\S+@\S+\.\w+"),                   # email addresses
    re.compile(r"(?<!\w)[@#][\w.-]+"),             # @handles and #channels
    re.compile(r":[a-z0-9_+-]+:"),                 # emoji shortcodes
)
AUTHORS = ("user", "other", "unknown")
KINDS = ("body", "greeting", "closing", "signature", "quoted", "forwarded", "pasted", "auto")
IDENTITY_FIELDS = ("Mail:", "Chat:", "Code host:", "Tracker:", "Former:")
IDENTIFIER_PUNCTUATION = ",;()<>\"'`"

GREETING = re.compile(
    r"^(hi|hey|hello|dear|morning|good (morning|afternoon|evening)|yo|hiya)\b[^.?!\n]{0,40}[,!:]?\s*$"
    r"|^[A-Z][\w'-]+( [A-Z][\w'-]+)?,\s*$",
    re.IGNORECASE,
)
SIGN_OFF_WORDS = re.compile(
    r"\b(thanks|thank you|thx|ty|cheers|best|regards|sincerely|talk soon|later|ttyl|love|xo|warmly)\b",
    re.IGNORECASE,
)
REPLY_HEADER = re.compile(r"^On .{4,200}wrote:\s*$")
FORWARD_HEADER = re.compile(r"^(-{3,}\s*Forwarded message|Begin forwarded message:)", re.IGNORECASE)
SIGNATURE_DELIMITER = re.compile(r"^--\s*$")

SLACK_LABELED_LINK = re.compile(r"<(?:https?|mailto):[^|>]*\|([^>]*)>")
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
    text = SLACK_LABELED_LINK.sub(r"\1", text)
    for pattern in STRIP_PATTERNS:
        text = pattern.sub(" ", text)
    return text


# ---------------------------------------------------------------------------
# Corpus


class Segment:
    def __init__(self, record: dict, medium: str) -> None:
        self.counted = record["kind"] == "body"
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
    if record["author"] not in AUTHORS:
        return f"invalid author {record['author']!r}"
    if record["kind"] not in KINDS:
        return f"invalid kind {record['kind']!r}"
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
            if record["author"] != "user":
                continue
            key = (record["msg"], record["text"])
            if key in seen:
                continue
            seen.add(key)
            segments.append(Segment(record, medium_of(path)))
    return segments


# ---------------------------------------------------------------------------
# save


def identifiers(cache: str, extra: List[str]) -> Set[str]:
    """The user's account identifiers, from identity.md plus any --me values."""
    found = {normalize_identifier(value) for value in extra}
    path = os.path.join(cache, "identity.md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                if line.startswith(IDENTITY_FIELDS):
                    found.update(normalize_identifier(t) for t in line.split(":", 1)[1].split())
    return {value for value in found if value}


def normalize_identifier(value: str) -> str:
    return value.strip(IDENTIFIER_PUNCTUATION).lstrip("@").lower()


def split_own_text(text: str, is_document: bool) -> List[Tuple[str, str, str]]:
    """Split a message the user sent into (author, kind, text) segments."""
    own, tail = split_off_tail(text.split("\n"))
    segments = [("other", kind, "\n".join(lines).strip()) for kind, lines in tail]
    own, signature = split_at(own, lambda line: bool(SIGNATURE_DELIMITER.match(line)))
    own, quoted = separate_quoted(own)
    body = "\n".join(own).strip()
    greeting = closing = ""
    if not is_document:
        greeting, body = take_greeting(body)
        body, closing = take_closing(body)
    ordered = [("user", "greeting", greeting), ("user", "body", body), ("user", "closing", closing),
               ("user", "signature", "\n".join(signature[1:]).strip())]
    ordered += [("other", "quoted", block) for block in quoted]
    return [segment for segment in ordered + segments if segment[2]]


def split_at(lines: List[str], is_marker) -> Tuple[List[str], List[str]]:
    for index, line in enumerate(lines):
        if is_marker(line):
            return lines[:index], lines[index:]
    return lines, []


def split_off_tail(lines: List[str]) -> Tuple[List[str], List[Tuple[str, List[str]]]]:
    """Cut the text at the first forwarded or reply header."""
    for index, line in enumerate(lines):
        joined = line + " " + lines[index + 1] if index + 1 < len(lines) else line
        if FORWARD_HEADER.match(line):
            return lines[:index], [("forwarded", lines[index:])]
        if REPLY_HEADER.match(line) or (line.startswith("On ") and REPLY_HEADER.match(joined)):
            return lines[:index], [("quoted", lines[index:])]
    return lines, []


def separate_quoted(lines: List[str]) -> Tuple[List[str], List[str]]:
    """Move "> " quoted blocks out of the user's own lines."""
    own, blocks, current = [], [], []
    for line in lines:
        if line.lstrip().startswith(">"):
            current.append(line)
            continue
        if current:
            blocks.append("\n".join(current))
            current = []
        own.append(line)
    if current:
        blocks.append("\n".join(current))
    return own, blocks


def take_greeting(body: str) -> Tuple[str, str]:
    first, _, rest = body.partition("\n")
    if rest.strip() and GREETING.match(first.strip()):
        return first.strip(), rest.strip()
    return "", body


def take_closing(body: str) -> Tuple[str, str]:
    """Split off a short final paragraph that is a sign-off, a name, or both."""
    head, _, last = body.rpartition("\n\n")
    if not head.strip():
        return body, ""
    lines = [line.strip() for line in last.strip().split("\n") if line.strip()]
    words = sum(len(line.split()) for line in lines)
    signed = SIGN_OFF_WORDS.search(last) and len(lines) <= 3 and all(len(line.split()) <= 4 for line in lines)
    bare_name = len(lines) == 1 and words <= 3 and not re.search(r"[.?!]$", lines[0])
    if signed or bare_name:
        return head.strip(), last.strip()
    return body, ""


def prefixed(source: str, value: str) -> str:
    """Prefix an id with its source once, even if the caller already added it."""
    bare = re.sub(rf"^{re.escape(source)}[:_-]", "", value)
    return f"{source}:{bare}"


def slugify(card: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", card.strip()).strip("-")
    return slug[len("card-"):] if slug.startswith("card-") else slug


def label_message(message: dict, mine: Set[str], source: str) -> List[dict]:
    sender = str(message.get("from", ""))
    base = {
        "thread": prefixed(source, str(message.get("thread", message["id"]))),
        "msg": prefixed(source, message["id"]),
        "date": str(message.get("date", "")),
        "from": sender,
    }
    if message.get("rev"):
        base["rev"] = str(message["rev"])
    if normalize_identifier(sender) in mine:
        match = "identifier"
    elif message.get("match") == "name":
        match = "name"
    else:
        return [dict(base, author="other", kind="auto" if message.get("auto") else "body", text=message["text"])]
    if message.get("auto"):
        return [dict(base, author="user", match=match, kind="auto", text=message["text"])]
    records = []
    for author, kind, text in split_own_text(message["text"], bool(message.get("rev"))):
        record = dict(base, author=author, kind=kind, text=text)
        if author == "user":
            record["match"] = match
        records.append(record)
    return records


def load_messages(path: str) -> List[dict]:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    messages = data.get("messages", []) if isinstance(data, dict) else data
    for index, message in enumerate(messages):
        missing = [f for f in ("id", "from", "text") if not isinstance(message.get(f), str) or not message[f]]
        if missing:
            sys.exit(f"Message {index} in {path} is missing {', '.join(missing)}; nothing saved.")
    return messages


def save(cache: str, card: str, source: str, input_path: str, extra: List[str]) -> int:
    card = slugify(card)
    if "-" not in card:
        sys.exit(f"--card must be <medium>-<audience-slug>, like email-jordan-blake; got {card!r}.")
    mine = identifiers(cache, extra)
    if not mine:
        sys.exit("No user identifiers: add them to identity.md or pass --me; nothing saved.")
    messages = load_messages(input_path)
    corpus_dir = os.path.join(cache, "corpus")
    os.makedirs(corpus_dir, mode=0o700, exist_ok=True)
    path = os.path.join(corpus_dir, f"{card}.jsonl")
    existing = existing_keys(path)
    added = []
    for message in messages:
        for record in label_message(message, mine, source):
            key = (record["msg"], record["kind"], record["text"])
            if key not in existing:
                existing.add(key)
                added.append(record)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
        for record in added:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    report_saved(path, messages, added)
    return 0


def existing_keys(path: str) -> Set[Tuple[str, str, str]]:
    keys = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                    keys.add((record.get("msg"), record.get("kind"), record.get("text")))
                except json.JSONDecodeError:
                    continue
    return keys


def report_saved(path: str, messages: List[dict], added: List[dict]) -> None:
    print(f"Saved {len(added)} new segments from {len(messages)} messages to {path}")
    by_message: Dict[str, List[str]] = defaultdict(list)
    for record in added:
        words = len(record["text"].split())
        label = f"{record['author']}/{record['kind']}"
        if record.get("match"):
            label += f" ({record['match']})"
        by_message[record["msg"]].append(f"{label} {words}w")
    for msg, labels in by_message.items():
        print(f"  {msg}: " + ", ".join(labels))


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
        # Every word the user wrote, greetings and closings included, so a
        # recipient's name is never flagged as a word the user doesn't use.
        self.lexicon: Counter = Counter()
        for segment in segments:
            self.lexicon.update(self.reference.tokenize(segment.text))
        self.segments = [segment for segment in segments if segment.counted]
        for segment in self.segments:
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
        trigrams = {gram: count for gram, count in found if len(gram) == 3}
        found = [(gram, count) for gram, count in found
                 if len(gram) == 3 or not any(
                     count == tri_count and gram in (tri[:2], tri[1:]) for tri, tri_count in trigrams.items())]
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
    lines += ["A word the user chose in their request is theirs and stays in the draft, even when it is",
              "listed here; `check --exempt` never flags it.", ""]
    lines.append(f"AI-leaning words with 0 uses in {messages} messages:")
    lines.append("")
    lines.append(", ".join(unused) or "(none)")
    if used:
        lines += ["", "AI-leaning words you do use, so the draft check allows them:", "", ", ".join(used)]
    return lines


def lexicon_lines(profile: Profile) -> List[str]:
    lines = ["", "## Lexicon", "",
             f"Every word you wrote, {len(profile.lexicon)} in all, including greetings and closings.", "", "```"]
    for word, count in sorted(profile.lexicon.items(), key=lambda item: (-item[1], item[0])):
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


def corpus_files(cache: str) -> List[str]:
    corpus_dir = os.path.join(cache, "corpus")
    if not os.path.isdir(corpus_dir):
        return []
    return [os.path.join(corpus_dir, f) for f in os.listdir(corpus_dir) if f.endswith(".jsonl")]


def vocabulary_is_stale(cache: str) -> bool:
    path = os.path.join(cache, "vocabulary.md")
    if not os.path.exists(path):
        return True
    built = os.path.getmtime(path)
    return any(os.path.getmtime(f) > built for f in corpus_files(cache))


def check(cache: str, draft_path: str, exempt_path: Optional[str], reference: Reference) -> int:
    if not corpus_files(cache) and not os.path.exists(os.path.join(cache, "vocabulary.md")):
        print("No corpus in the cache yet, so there is no vocabulary to check against. Check skipped.")
        return 0
    if vocabulary_is_stale(cache):
        build(cache, reference)
    lexicon, rates, never = load_vocabulary(cache)
    with open(draft_path, encoding="utf-8") as handle:
        tokens = reference.tokenize(handle.read())
    exempt: Set[str] = set()
    if exempt_path:
        with open(exempt_path, encoding="utf-8") as handle:
            request = handle.read()
        exempt = set(reference.tokenize(request)) | set(FALLBACK_TOKEN.findall(request.lower()))
    draft = Counter(t for t in tokens if t not in exempt)
    findings = never_used_findings(draft, never) + unseen_findings(draft, lexicon, never, reference) \
        + overuse_findings(draft, rates, len(tokens))
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
        # "export's" is "export" plus a possessive, which wordfreq has no entry for.
        base = word[:-2] if word.endswith(("'s", "’s")) else word
        if word in lexicon or base in lexicon or word in never:
            continue
        zipf = reference.zipf(base)
        if zipf is None:
            findings.append(f"unseen: \"{word}\" (not in your corpus; no English baseline to judge rarity)")
        elif zipf < UNCOMMON_ZIPF:
            findings.append(f"unseen and uncommon: \"{word}\" (not in your corpus; Zipf {zipf:.1f} in English)")
    return findings


def overuse_findings(draft: Counter, rates: Dict[str, float], total: int) -> List[str]:
    """Frequent words the draft leans on much harder than the user does.

    Rates are unreliable in short drafts, so drafts under
    DRAFT_OVERUSE_MIN_WORDS are not checked.
    """
    if total < DRAFT_OVERUSE_MIN_WORDS:
        return []
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
        for warning in warnings:
            print(f"  warning: {warning}")
        sys.exit(f"No counted segments in {os.path.join(cache, 'corpus')} "
                 f"({plural(len(warnings), 'line')} rejected, listed above); nothing to build.")
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
    cache_help = "style cache directory (default: $HOME/writing-style)"
    parser.add_argument("--cache", default=os.path.join(os.path.expanduser("~"), "writing-style"), help=cache_help)
    # Also accept --cache after the subcommand; SUPPRESS keeps the top-level value when it's absent there.
    after = argparse.ArgumentParser(add_help=False)
    after.add_argument("--cache", default=argparse.SUPPRESS, help=cache_help)
    commands = parser.add_subparsers(dest="command", required=True)
    save_parser = commands.add_parser("save", parents=[after], help="label messages and append them to the corpus")
    save_parser.add_argument("--card", required=True, help="the card's slug, e.g. email-jordan-blake")
    save_parser.add_argument("--source", required=True, help="id prefix, e.g. gmail, slack, jira, git")
    save_parser.add_argument("--input", required=True,
                             help='JSON file: {"messages": [{"id", "thread", "date", "from", "text"}, ...]}')
    save_parser.add_argument("--me", action="append", default=[], help="a user identifier not in identity.md")
    check_parser = commands.add_parser("check", parents=[after], help="check a draft against vocabulary.md")
    check_parser.add_argument("--draft", required=True, help="file holding the draft text")
    check_parser.add_argument("--exempt", required=True,
                              help="file holding the user's request, verbatim; its words are never flagged")
    commands.add_parser("build", parents=[after], help="rebuild vocabulary.md from corpus/*.jsonl")
    args = parser.parse_args()
    cache = os.path.abspath(args.cache)
    if args.command == "save":
        os.makedirs(cache, mode=0o700, exist_ok=True)
        return save(cache, args.card, args.source, args.input, args.me)
    if not os.path.isdir(cache):
        sys.exit(f"No style cache at {cache}.")
    ensure_wordfreq(cache)
    reference = Reference()
    if args.command == "build":
        return build(cache, reference)
    return check(cache, args.draft, args.exempt, reference)


if __name__ == "__main__":
    sys.exit(main())
