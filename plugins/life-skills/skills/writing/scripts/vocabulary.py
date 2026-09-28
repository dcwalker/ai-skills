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
Messages from an identifier in identity.md (or --me) are the user's, as are
messages the caller marks "match": "name" when the sender has no identifier;
their greeting, closing, signature, footers, quoted replies, forwarded text,
and any "pasted" excerpts are split off into their own segments. A message
with no sender is "unknown". Everything else is labeled as someone else's.
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
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
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
    "leveraged", "leverages", "leveraging", "meticulous", "meticulously",
    "moreover", "multifaceted", "notably", "noteworthy", "nuanced", "paramount",
    "pivotal", "realm", "robust", "seamless", "seamlessly", "showcase",
    "showcased", "showcases", "showcasing", "streamline", "streamlined",
    "streamlining", "synergy", "tapestry", "testament", "underscore",
    "underscored", "underscores", "utilize", "utilized", "utilizes",
    "utilizing", "vibrant", "aligned", "aligning", "fostered", "fostering",
    "elevated", "elevating", "harnessed", "harnessing", "bolstered",
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
IDENTIFIER_PUNCTUATION = ",;()<>\"'`*"

# A greeting word plus at most a name, ending in , ! or : ("hey Jordan,"), or a
# bare capitalized name with a comma ("Priya,"). Case-insensitive only for the
# greeting words, so "Honestly," is not a greeting.
GREETING = re.compile(
    r"^(?i:hi|hey|hello|dear|morning|good morning|good afternoon|good evening|yo|hiya)"
    r"( [\w'.-]+){0,2}\s*[,!:]\s*$"
    r"|^(?i:hi|hey|hello|hiya)( [\w'.-]+)?\s*$"
    r"|^[A-Z][\w'-]+( [A-Z][\w'-]+)?,\s*$"
)
# A sign-off line: the phrase alone, optionally followed by punctuation and a
# name. "best", "later", and "love" are also everyday words ("later today
# works"), so after them only a capitalized name may follow.
SIGN_OFF_LINE = re.compile(
    r"^(?i:thanks|thank you|thanks again|many thanks|thx|ty|cheers|regards|best regards|kind regards|"
    r"warm regards|all the best|sincerely|talk soon|ttyl|xo|warmly)[,.!]?( [\w'.-]+){0,2}$"
    r"|^(?i:best|later|love)[,.!]?( [A-Z][\w'.-]*){0,2}$"
)
REPLY_HEADERS = (
    re.compile(r"^(On|Le|Am|El|Il|Op|Em|Den|Dne) .{4,300}"
               r"(wrote|a écrit|schrieb|escribió|scrisse|schreef|escreveu|skrev|napsal)\s*:\s*$", re.IGNORECASE),
    re.compile(r"^[A-Z][\w'.-]+( [A-Z][\w'.-]+){0,3} wrote:\s*$"),
    re.compile(r"^(Am|Op|Den|Il|El|Le) .{4,200}\b(schrieb|schreef|skrev|scrisse|escribió)\b.{1,200}:\s*$",
               re.IGNORECASE),
    re.compile(r"^.{1,200}\bha scritto:\s*$", re.IGNORECASE),
    re.compile(r"^.{0,120}\d.{0,120}<[^>\s]+@[^>\s]+>\s*:\s*$"),
    re.compile(r"^.{1,200}<[^>\s]+@[^>\s]+>\s*(wrote|a écrit|schrieb|escribió)\s*:\s*$", re.IGNORECASE),
    re.compile(r"^-{2,}\s*Original Message\s*-{2,}\s*$", re.IGNORECASE),
    re.compile(r"^_{10,}\s*$"),
)
OUTLOOK_FROM = re.compile(r"^\*?(From|Von|De|Da|Van|Från|Fra|Od):\*?\s+\S", re.IGNORECASE)
OUTLOOK_FIELDS = re.compile(
    r"^\*?(Sent|Date|To|Subject|Cc|Gesendet|Datum|An|Betreff|Envoyé|Date|À|Objet|Inviato|Data|A|Oggetto|"
    r"Verzonden|Aan|Onderwerp|Skickat|Till|Ämne|Sendt|Til|Emne|Enviado|Para|Assunto|Asunto):\*?\s",
    re.IGNORECASE,
)
FORWARD_HEADER = re.compile(r"^(-{3,}\s*Forwarded message|Begin forwarded message:)", re.IGNORECASE)
SIGNATURE_DELIMITER = re.compile(r"^--\s*$")
MOBILE_FOOTER = re.compile(
    r"^(Sent from (my )?(iPhone|iPad|Android|Samsung|mobile|Outlook|Mail for)|Get Outlook for (iOS|Android)"
    r"|\W*(CONFIDENTIALITY NOTICE|CONFIDENTIAL|DISCLAIMER)\b|This (e-?mail|message)( and any attachments)?"
    r"( \(including any attachments\))? (is|are|may be) (confidential|intended))",
    re.IGNORECASE,
)
GIT_TRAILER = re.compile(r"^(Co-authored-by|Signed-off-by|Reviewed-by|Acked-by|Reported-by):", re.IGNORECASE)
HTML_BODY = re.compile(r"</(div|p|blockquote|span|table)>|<br\s*/?>", re.IGNORECASE)
ADDRESS_IN_BRACKETS = re.compile(r"<([^<>\s]+@[^<>\s]+)>")
CODE_HOST_WORDS = {"github", "gitlab", "bitbucket", "on", "at", "via"}
NOT_A_NAME = {"honestly", "also", "so", "well", "ok", "okay", "yes", "no", "sure", "update", "fyi", "note",
              "quick", "actually", "anyway", "first", "second", "finally", "unfortunately", "luckily"}
COMMON_ONE_WORD_REPLIES = {"yes", "yep", "yeah", "nope", "sure", "thx", "thanks", "done", "agreed", "same",
                           "lgtm", "nice", "great", "cool", "okay", "fine", "noted", "works"}
IDENTIFIER_NOISE = {"until", "since", "from", "to", "and", "or", "the", "old", "new", "former", "work",
                    "personal", "address", "account", "handle", "id", "user", "workspace"}

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
    """Create the cache's own venv and install the pinned wordfreq. Returns success.

    Only <cache>/.venv is ever created or replaced; a venv named by
    WRITING_STYLE_VENV belongs to whoever set it and is never touched. A failed
    install removes the half-built venv so the next run tries again.
    """
    if os.environ.get("WRITING_STYLE_VENV"):
        print(f"WRITING_STYLE_VENV has no wordfreq for Python {sys.version_info.major}.{sys.version_info.minor}; "
              "continuing without it.", file=sys.stderr)
        return False
    target = venv_dir(cache)
    print(f"Installing wordfreq {WORDFREQ_VERSION} into {target} (first run only)...", file=sys.stderr)
    try:
        venv.create(target, clear=True, with_pip=True)
        pip = [os.path.join(target, "bin", "python3"), "-m", "pip", "install", "--quiet", "--disable-pip-version-check"]
        subprocess.run(pip + [f"wordfreq=={WORDFREQ_VERSION}"], check=True)
        return True
    except (OSError, subprocess.CalledProcessError) as err:
        shutil.rmtree(target, ignore_errors=True)
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
        print(f"{venv_dir(cache)} has no wordfreq; continuing without it.", file=sys.stderr)


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
            return f"wordfreq {installed_version('wordfreq')}, English 'large' list"
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


def installed_version(package: str) -> str:
    try:
        from importlib import metadata
        return metadata.version(package)
    except Exception:  # metadata missing or unreadable; the pin is the best guess
        return WORDFREQ_VERSION


def clean_text(text: str) -> str:
    text = SLACK_LABELED_LINK.sub(r"\1", text)
    for pattern in STRIP_PATTERNS:
        text = pattern.sub(" ", text)
    return text


# ---------------------------------------------------------------------------
# Corpus


class Segment:
    def __init__(self, record: dict, medium: str) -> None:
        self.kind = record["kind"]
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
    if not isinstance(record.get("date", ""), str):
        return "date is not a string"
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
        read_file(path, seen, warnings, segments)
    return segments, files, warnings


def bare_id(msg: str) -> str:
    return msg.split(":", 1)[-1]


def read_file(path: str, seen: Set[Tuple[str, str]], warnings: List[str],
              segments: Optional[List[Segment]] = None) -> List[Segment]:
    segments = [] if segments is None else segments
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except UnicodeDecodeError:
        warnings.append(f"{os.path.basename(path)}: not UTF-8, skipped")
        return segments
    for number, line in enumerate(lines, 1):
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
            # The same message saved again (an edit, a relabel, or another
            # card's copy): the latest line for it replaces earlier ones,
            # whoever it says wrote it. Ids are compared without the source
            # prefix, so "gmail:1" and "mail:1" are one message.
            key = (bare_id(record["msg"]), record["kind"])
            if key in seen:
                segments[:] = [s for s in segments if (bare_id(s.msg), s.kind) != key]
            seen.add(key)
            if record["author"] == "user" and record["kind"] != "auto":
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
                found.update(identity_line_identifiers(line))
    return {value for value in found if value}


def identity_line_identifiers(line: str) -> Set[str]:
    """Identifiers on one identity.md field line, without its free-text notes."""
    line = re.sub(r"^[\s>*-]*\**", "", line)
    field = next((f for f in IDENTITY_FIELDS if line.lower().startswith(f.lower())), None)
    if not field:
        return set()
    value = re.split(r"\s(?:until|since)\s|\s[—–]\s", line[len(field):], maxsplit=1)[0]
    found = {normalize_identifier(handle) for handle in re.findall(r"\(@([\w.-]+)\)", value)}
    value = re.sub(r"\([^)]*\)", " ", value)  # other parentheticals are notes, such as a display name
    for entry in re.split(r"[,;]", value):
        if field in ("Chat:", "Code host:"):
            entry = entry.rsplit(":", 1)[-1]  # drop a "<workspace>:" or "<platform>:" label
        tokens = [t.strip(IDENTIFIER_PUNCTUATION) for t in entry.split()]
        tokens = [t for t in tokens if t and t.lower() not in CODE_HOST_WORDS]
        for position, token in enumerate(tokens):
            # On the code host line a bare handle counts, but only as the entry's first word.
            if looks_like_identifier(token, bare_handles=field == "Code host:" and position == 0):
                found.add(normalize_identifier(token))
    return {value for value in found if value}


def is_identifier_shaped(sender: str) -> bool:
    """True for an address or account id, which proves who the author is."""
    return any(looks_like_identifier(t.strip(IDENTIFIER_PUNCTUATION), bare_handles=False)
               for t in re.split(r"[\s<>]+", sender))


def looks_like_identifier(token: str, bare_handles: bool) -> bool:
    """An address, an account id with a digit (U024BE7LH, user-alex-1), or,
    on the code host line only, a bare handle. Plain words on a line, such as
    the parts of a name, are never identifiers."""
    if not token or token.startswith("(@") or token.lower() in IDENTIFIER_NOISE:
        return False
    if re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", token):
        return False
    if "@" in token.lstrip("@") or re.search(r"\d", token):
        return True
    return bare_handles and bool(re.fullmatch(r"@?[\w.-]+", token))


def normalize_identifier(value: str) -> str:
    """Lowercased bare identifier; "Dan Walker <dan@x.com>" becomes "dan@x.com"."""
    bracketed = ADDRESS_IN_BRACKETS.search(value)
    if bracketed:
        value = bracketed.group(1)
    return value.strip().strip(IDENTIFIER_PUNCTUATION).lstrip("@").lower()


def split_own_text(text: str, is_document: bool) -> List[Tuple[str, str, str]]:
    """Split a message the user sent into (author, kind, text) segments."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    own, tail = split_off_tail(text.split("\n"))
    segments = [("other", kind, "\n".join(lines).strip()) for kind, lines in tail]
    own, footer = split_at(own, lambda line: bool(MOBILE_FOOTER.match(line.strip())))
    own, signature = split_at(own, lambda line: bool(SIGNATURE_DELIMITER.match(line)))
    own, quoted = separate_quoted(own)
    own, markup_quoted = separate_markup_quotes(own)
    quoted += markup_quoted
    segments = [("user", "auto", "\n".join(footer).strip())] + segments
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
    """Cut the text at the first forwarded or reply header; the rest is someone else's."""
    for index, line in enumerate(lines):
        if FORWARD_HEADER.match(line.strip()):
            return lines[:index], [("forwarded", lines[index:])]
        if is_reply_header(lines, index):
            return lines[:index], [("quoted", lines[index:])]
    return lines, []


def is_reply_header(lines: List[str], index: int) -> bool:
    """A reply header, wrapped over up to three lines, or an Outlook From:/Sent: block."""
    line = lines[index].strip()
    # Only a line that starts a header may be joined with the next ones, so a
    # wrapped header never swallows the user's own text above it.
    spans = (1, 2, 3) if re.match(r"(On|Le|Am|El|Il|Op|Em|Den|Dne) ", line) else (1,)
    for span in spans:
        joined = " ".join(part.strip() for part in lines[index:index + span])
        if any(pattern.match(joined) for pattern in REPLY_HEADERS):
            return True
    if OUTLOOK_FROM.match(line):
        following = [part.strip() for part in lines[index + 1:index + 5]]
        return any(OUTLOOK_FIELDS.match(part) for part in following)
    return False


def separate_markup_quotes(lines: List[str]) -> Tuple[List[str], List[str]]:
    """Jira {quote}...{quote} and bq. blocks, and git Co-authored-by style
    trailers, which name or carry someone else's text."""
    own, blocks, inside, current = [], [], False, []
    for line in lines:
        stripped = line.strip()
        if inside or stripped.startswith("{quote}"):
            current.append(line)
            opens_and_closes = stripped.startswith("{quote}") and stripped.count("{quote}") >= 2
            if (inside and "{quote}" in stripped) or opens_and_closes:
                blocks.append("\n".join(current))
                current, inside = [], False
            else:
                inside = True
            continue
        if stripped.startswith("bq. ") or GIT_TRAILER.match(stripped):
            blocks.append(line)
            continue
        own.append(line)
    if current:
        blocks.append("\n".join(current))
    return own, blocks


def separate_quoted(lines: List[str]) -> Tuple[List[str], List[str]]:
    """Move quoted blocks out of the user's own lines.

    Covers "> " and "&gt; " line quotes, and Slack's ">>>", which quotes
    everything after it.
    """
    for index, line in enumerate(lines):
        if line.lstrip().startswith((">>>", "&gt;&gt;&gt;")):
            own, quoted = separate_quoted(lines[:index])
            return own, quoted + ["\n".join(lines[index:])]
    own, blocks, current = [], [], []
    for line in lines:
        if line.lstrip().startswith((">", "&gt;")):
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
    if first.strip().rstrip(",").lower() in NOT_A_NAME:
        return "", body
    if rest.strip() and GREETING.match(first.strip()):
        return first.strip(), rest.strip()
    return "", body


def take_closing(body: str) -> Tuple[str, str]:
    """Split off a short final paragraph that is a sign-off, a name, or both."""
    head, _, last = body.rpartition("\n\n")
    if not head.strip():
        return body, ""
    lines = [line.strip() for line in last.strip().split("\n") if line.strip()]
    signed = len(lines) <= 3 and bool(SIGN_OFF_LINE.match(lines[0])) and all(len(line.split()) <= 3 for line in lines)
    bare_name = len(lines) == 1 and looks_like_name(lines[0])
    if signed or bare_name:
        return head.strip(), last.strip()
    return body, ""


def looks_like_name(line: str) -> bool:
    """A sign-off name: "Alex", "Alex Reyes", or one lowercase word like "alex"."""
    words = line.split()
    if not words or len(words) > 3 or re.search(r"[.?!,:;]$", line):
        return False
    if all(re.fullmatch(r"[A-Z][\w'.-]*", word) for word in words):
        return True
    return len(words) == 1 and len(line) >= 3 and line.lower() not in COMMON_ONE_WORD_REPLIES


def prefixed(source: str, value: str) -> str:
    """Prefix an id with its source once, even if the caller already added it."""
    bare = re.sub(rf"^{re.escape(source)}[:_-]", "", value, flags=re.IGNORECASE)
    return f"{source}:{bare}"


def slugify(card: str) -> str:
    """The card's slug: "card-email-sam.ortiz.md" becomes "email-sam-ortiz".

    Case and non-ASCII letters are kept, so the slug matches the card's own
    file name (channel ids such as C024BE91L are upper case).
    """
    name = os.path.basename(card.strip())
    name = re.sub(r"\.(md|jsonl)$", "", name)
    slug = re.sub(r"[\W_]+", "-", name).strip("-")
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
    if not sender.strip():
        return [dict(base, author="unknown", kind="body", text=message["text"])]
    if normalize_identifier(sender) in mine:
        match = "identifier"
    elif message.get("match") == "name" and not is_identifier_shaped(sender):
        match = "name"
    else:
        if message.get("match") == "name":
            print(f"  warning: {base['msg']} is from {sender!r}, an identifier that isn't the user's, "
                  "so it is saved as someone else's despite match: name", file=sys.stderr)
        return [dict(base, author="other", kind="auto" if message.get("auto") else "body", text=message["text"])]
    if message.get("auto"):
        return [dict(base, author="user", match=match, kind="auto", text=message["text"])]
    text = message["text"]
    records = []
    for excerpt in message.get("pasted", []):
        # Text the user pasted in from someone else, marked by the caller: kept as context.
        if excerpt and excerpt in text:
            text = text.replace(excerpt, "\n")
            records.append(dict(base, author="other", kind="pasted", text=excerpt.strip()))
    for author, kind, text in split_own_text(text, bool(message.get("rev"))):
        record = dict(base, author=author, kind=kind, text=text)
        if author == "user":
            record["match"] = match
        records.append(record)
    return records


def load_messages(path: str) -> List[dict]:
    """Read and validate the input: {"messages": [...]} or a bare list, from a file or "-" for stdin."""
    try:
        if path == "-":
            data = json.load(sys.stdin)
        else:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
    except (OSError, json.JSONDecodeError) as err:
        sys.exit(f"Could not read {path}: {err}; nothing saved.")
    if isinstance(data, dict):
        if "messages" not in data:
            sys.exit(f'{path} has no "messages" key; nothing saved.')
        data = data["messages"]
    if not isinstance(data, list):
        sys.exit(f"{path} must hold a list of messages; nothing saved.")
    for index, message in enumerate(data):
        problem = message_problem(message)
        if problem:
            sys.exit(f"Message {index} in {path} {problem}; nothing saved.")
    return data


def message_problem(message: object) -> Optional[str]:
    if not isinstance(message, dict):
        return "is not an object"
    missing = [f for f in ("id", "text") if not isinstance(message.get(f), str) or not message[f]]
    if missing:
        return f"is missing {', '.join(missing)}"
    if not isinstance(message.get("from", ""), str):
        return "has a non-string from"
    if is_html(message["text"]):
        return "has an HTML body; pass the plain-text body instead"
    pasted = message.get("pasted", [])
    if not isinstance(pasted, list) or not all(isinstance(p, str) for p in pasted):
        return "has a pasted value that isn't a list of strings"
    return None


def is_html(text: str) -> bool:
    """An HTML body, not plain text that mentions a tag ("wrap it in a </div>")."""
    head = text.lstrip()[:200].lower()
    return head.startswith(("<html", "<!doctype", "<div", "<p>", "<p ", "<body", "<table")) \
        or len(HTML_BODY.findall(text)) > 3


def save(cache: str, card: str, source: str, input_path: str, extra: List[str]) -> int:
    source = source.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+", source):
        sys.exit(f"--source must be a plain name such as gmail, slack, jira, or git; got {source!r}.")
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
            key = (record["msg"], record["kind"], record["author"], record["text"])
            if key not in existing:
                existing.add(key)
                added.append(record)
    if added:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
            for record in added:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    make_private(cache)
    report_saved(path, messages, added)
    if messages and not any(record["author"] == "user" for record in added) and not existing_user(path):
        print("  warning: none of these messages matched the user's identifiers; check identity.md, --me, "
              "and that 'from' holds the sender's address or id", file=sys.stderr)
    return 0


def make_private(cache: str) -> None:
    """Keep the cache readable by the user alone: remove group and other
    permissions from the cache, corpus/, and the files directly in them.
    Execute bits survive, symlinks are left alone, and nothing deeper (such as
    .venv) is touched."""
    corpus_dir = os.path.join(cache, "corpus")
    for directory in (cache, corpus_dir):
        if not os.path.isdir(directory) or os.path.islink(directory):
            continue
        entries = [directory] + [os.path.join(directory, name) for name in os.listdir(directory)]
        for path in entries:
            if os.path.islink(path) or (path != directory and os.path.isdir(path)):
                continue
            os.chmod(path, os.stat(path).st_mode & ~0o077 & 0o7777)


def existing_user(path: str) -> bool:
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as handle:
        return any('"author": "user"' in line for line in handle)


def existing_keys(path: str) -> Set[Tuple[str, str, str, str]]:
    keys = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                    keys.add((record.get("msg"), record.get("kind"), record.get("author"), record.get("text")))
                except json.JSONDecodeError:
                    continue
    return keys


def report_saved(path: str, messages: List[dict], added: List[dict]) -> None:
    if not added:
        print(f"Nothing new to save from {plural(len(messages), 'message')}; {os.path.basename(path)} is unchanged.")
        return
    print(f"Saved {plural(len(added), 'new segment')} from {plural(len(messages), 'message')} to {path}")
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


def render(profile: Profile, files: List[str], warnings: List[str], fingerprint: str) -> str:
    lines = header_lines(profile, files, fingerprint)
    lines += function_word_lines(profile)
    lines += signature_lines(profile)
    lines += phrase_lines(profile)
    lines += never_used_lines(profile)
    if warnings:
        lines += ["", "## Corpus warnings", ""] + [f"- {w}" for w in warnings]
    lines += lexicon_lines(profile)
    return "\n".join(lines) + "\n"


def header_lines(profile: Profile, files: List[str], fingerprint: str = "") -> List[str]:
    dates = sorted(s.date for s in profile.segments if s.date)
    span = f"{dates[0][:10]} -> {dates[-1][:10]}" if dates else "undated"
    share = 100.0 * profile.name_match_words / profile.total if profile.total else 0.0
    return [
        "# Vocabulary",
        "",
        f"Built:       {datetime.date.today().isoformat()}",
        f"Corpus:      {plural(len(files), 'file')}, {plural(len(profile.message_ids), 'message')}, "
        f"{profile.total} counted words, {span}",
        f"Name match:  {profile.name_match_words} of {profile.total} counted words ({share:.0f}%) from display-name matches",
        f"Reference:   {profile.reference.describe()}",
        "Counted:     segments with author user and kind body only",
        f"Inputs:      {fingerprint}",
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
    def uses(word: str) -> int:
        return sum(count for token, count in profile.counts.items() if same_stem(word, token))
    unused = [w for w in AI_LEANING_WORDS if not uses(w)]
    used = [f"{w} ({uses(w)})" for w in AI_LEANING_WORDS if uses(w)]
    lines += ["A word the user chose in their request is theirs and stays in the draft, even when it is",
              "listed here; `check` flags it if the draft drops it.", ""]
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
        lexicon[word] = int(count) if count.strip().isdigit() else 0
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


def inputs_fingerprint(cache: str, reference: Reference) -> str:
    """What vocabulary.md was built from: every corpus file's name and
    contents, the reference, and this script. Any change, a deleted file,
    wordfreq becoming available, or a new version of the script included,
    means a rebuild. A copied cache keeps its fingerprint."""
    digest = hashlib.sha256(reference.describe().encode())
    with open(os.path.abspath(__file__), "rb") as handle:
        digest.update(handle.read())
    for path in sorted(corpus_files(cache)):
        digest.update(os.path.basename(path).encode())
        with open(path, "rb") as handle:
            digest.update(handle.read())
    return digest.hexdigest()[:16]


def vocabulary_is_stale(cache: str, reference: Reference) -> bool:
    path = os.path.join(cache, "vocabulary.md")
    if not os.path.exists(path):
        return True
    with open(path, encoding="utf-8") as handle:
        recorded = re.search(r"^Inputs:\s+(\S+)", handle.read(), re.MULTILINE)
    return not recorded or recorded.group(1) != inputs_fingerprint(cache, reference)


def check(cache: str, draft_path: str, exempt_path: Optional[str], reference: Reference) -> int:
    if not corpus_files(cache):
        print("No corpus in the cache yet, so there is no vocabulary to check against. Check skipped.")
        return 0
    if vocabulary_is_stale(cache, reference):
        problem = write_vocabulary(cache, reference)
        if problem:
            print(f"{problem} Check skipped.")
            return 0
    lexicon, rates, never = load_vocabulary(cache)
    tokens = reference.tokenize(read_text(draft_path, "--draft"))
    exempt: Set[str] = set()
    if exempt_path:
        request = read_text(exempt_path, "--exempt")
        exempt = set(reference.tokenize(request)) | set(FALLBACK_TOKEN.findall(request.lower()))
    draft = Counter(t for t in tokens if not any(same_stem(t, word) for word in exempt))
    findings = dropped_request_findings(exempt, tokens, never) + never_used_findings(draft, never) \
        + unseen_findings(draft, lexicon, never, reference) + overuse_findings(Counter(tokens), rates, len(tokens))
    print(f"Draft: {len(tokens)} words. Reference: {reference.describe()}")
    if not findings:
        print("No vocabulary flags.")
    for finding in findings:
        print(f"- {finding}")
    return 0


def read_text(path: str, option: str) -> str:
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as err:
        sys.exit(f"Could not read {option} file {path}: {err.strerror}.")


def dropped_request_findings(request: Set[str], draft: List[str], never: Set[str]) -> List[str]:
    """Never-used words the user dictated in the request that the draft doesn't use.

    These are exactly the words a voice match is tempted to swap out. An
    inflection counts as kept ("leveraging" keeps "leverage"). The --exempt
    file should hold only what the user dictated, so a word here is one the
    user chose for the message.
    """
    return [f"request word dropped: \"{w}\" is in the user's words but not the draft; "
            "keep it unless the user asked to change it"
            for w in sorted(request & never) if not any(same_stem(w, token) for token in draft)]


def same_stem(a: str, b: str) -> bool:
    """Inflections of one word: "leverage", "leverages", "leveraged", and
    "leveraging" match; "stream" and "streamline" do not."""
    return inflection_base(a) == inflection_base(b)


def inflection_base(word: str) -> str:
    word = word.replace("’", "'")
    for suffix in ("'s", "ing", "ed", "es", "s", "d"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[:-len(suffix)]
            break
    return word[:-1] if word.endswith("e") else word


def never_used_findings(draft: Counter, never: Set[str]) -> List[str]:
    return [f"never used: \"{w}\" (0 in your corpus)" for w in sorted(draft) if w in never]


def unseen_findings(draft: Counter, lexicon: Dict[str, int], never: Set[str], reference: Reference) -> List[str]:
    findings: List[str] = []
    if not reference.available:
        return findings
    for word in sorted(draft):
        # "export's" is "export" plus a possessive, which wordfreq has no entry for.
        base = word[:-2] if word.endswith(("'s", "’s")) else word
        if word in lexicon or base in lexicon or word in never:
            continue
        zipf = reference.zipf(base)
        if zipf is not None and zipf < UNCOMMON_ZIPF:
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


def write_vocabulary(cache: str, reference: Reference) -> Optional[str]:
    """Rebuild vocabulary.md. Returns why nothing was built, or None."""
    segments, files, warnings = read_corpus(cache)
    for warning in warnings:
        print(f"  warning: {warning}")
    if not any(segment.counted for segment in segments):
        return (f"No counted segments in {os.path.join(cache, 'corpus')} "
                f"({plural(len(warnings), 'line')} rejected); no vocabulary to build.")
    profile = Profile(segments, reference)
    path = os.path.join(cache, "vocabulary.md")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(render(profile, files, warnings, inputs_fingerprint(cache, reference)))
    make_private(cache)
    print(f"Wrote {path}: {plural(len(profile.message_ids), 'message')}, {profile.total} counted words, "
          f"{plural(len(warnings), 'warning')}. Reference: {reference.describe()}")
    return None


def build(cache: str, reference: Reference) -> int:
    problem = write_vocabulary(cache, reference)
    if problem:
        sys.exit(problem)
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
                             help='JSON file, or - for stdin: {"messages": [{"id", "thread", "date", "from", "text"}, ...]}; '
                                  'optional per message: "match": "name", "auto": true, "rev", "pasted": [excerpts]')
    save_parser.add_argument("--me", action="append", default=[], help="a user identifier not in identity.md")
    check_parser = commands.add_parser("check", parents=[after], help="check a draft against vocabulary.md")
    check_parser.add_argument("--draft", required=True, help="file holding the draft text")
    check_parser.add_argument("--exempt", required=True,
                              help="file holding only what the user dictated for the message, in their words "
                                   "(empty when they dictated nothing)")
    # check reads every card's corpus; accept a --card copied from a save command and ignore it.
    check_parser.add_argument("--card", help=argparse.SUPPRESS)
    commands.add_parser("build", parents=[after], help="rebuild vocabulary.md from corpus/*.jsonl")
    args = parser.parse_args()
    cache = os.path.abspath(args.cache)
    if args.command == "save":
        os.makedirs(cache, mode=0o700, exist_ok=True)
        return save(cache, args.card, args.source, args.input, args.me)
    if not os.path.isdir(cache):
        if args.command == "check":
            print(f"No style cache at {cache}, so there is no vocabulary to check against. Check skipped.")
            return 0
        sys.exit(f"No style cache at {cache}.")
    ensure_wordfreq(cache)
    reference = Reference()
    if args.command == "build":
        return build(cache, reference)
    return check(cache, args.draft, args.exempt, reference)


if __name__ == "__main__":
    sys.exit(main())
