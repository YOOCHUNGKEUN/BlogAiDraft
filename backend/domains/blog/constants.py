# CLAUDE_MODEL = "claude-opus-4-5"
CLAUDE_MODEL = "claude-fable-5"

CLAUDE_MAX_TOKENS = 6000

GITHUB_API_ACCEPT_HEADER = "application/vnd.github.v3+json"
GITHUB_TREE_BRANCH = "HEAD"
MAX_REPO_FILES = 40
MAX_CODE_CHARS_FOR_PROMPT = 8000

SUPPORTED_SOURCE_EXTENSIONS = (
    ".dart",
    ".kt",
    ".java",
    ".swift",
    ".tsx",
    ".ts",
    ".jsx",
    ".js",
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".md",
)

PRIORITY_FILE_NAMES = (
    "pubspec.yaml",
    "package.json",
    "README.md",
    "main.dart",
    "App.jsx",
    "App.tsx",
    "main.py",
)
