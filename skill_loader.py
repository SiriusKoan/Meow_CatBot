import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)

# A Skill file must wrap YAML frontmatter between two `---` lines. The named
# groups capture the frontmatter and the Markdown instructions that follow it.
FRONTMATTER_PATTERN = re.compile(
    r"\A---\s*\n(?P<frontmatter>.*?)\n---\s*\n?(?P<instructions>.*)\Z",
    re.DOTALL,
)


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    instructions: str

    @classmethod
    def from_path(cls, path: Path) -> "Skill":
        """Parse a Skill's frontmatter and complete instructions from Markdown."""
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER_PATTERN.match(text)
        if not match:
            raise ValueError(f"Skill must contain YAML frontmatter: {path}")

        metadata = {}
        for line in match.group("frontmatter").splitlines():
            key, separator, value = line.partition(":")
            if separator:
                metadata[key.strip()] = cls._parse_frontmatter_value(value)

        name = metadata.get("name")
        description = metadata.get("description")
        if not name or not description:
            raise ValueError(f"Skill requires name and description: {path}")

        return cls(
            name=name,
            description=description,
            instructions=match.group("instructions").strip(),
        )

    @staticmethod
    def _parse_frontmatter_value(value):
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            try:
                return ast.literal_eval(value)
            except (SyntaxError, ValueError):
                return value[1:-1]
        return value

    @staticmethod
    def find_path(skill_directory: Path) -> Path | None:
        """Find a Skill file using the supported filename conventions."""
        standard_path = skill_directory / "SKILL.md"
        if standard_path.is_file():
            return standard_path

        compatible_path = skill_directory / f"{skill_directory.name}.md"
        if compatible_path.is_file():
            return compatible_path

        return None

    @classmethod
    def load_all(cls, root: str | Path) -> list["Skill"]:
        """Load the complete contents of every Skill under a directory."""
        root_path = Path(root)
        if not root_path.is_dir():
            logger.info("Skills directory does not exist: %s", root_path)
            return []

        skills = []
        for skill_directory in sorted(
            path for path in root_path.iterdir() if path.is_dir()
        ):
            skill_path = cls.find_path(skill_directory)
            if skill_path is None:
                logger.warning(
                    "Skipped skill directory without a skill file: %s",
                    skill_directory,
                )
                continue

            try:
                skills.append(cls.from_path(skill_path))
            except (OSError, UnicodeError, ValueError):
                logger.exception("Failed to load skill: %s", skill_path)

        return skills

    @property
    def prompt(self) -> str:
        """Return the Skill section included in the LLM prompt."""
        return (
            f"## Skill: {self.name}\n"
            f"Description: {self.description}\n\n"
            f"{self.instructions}"
        )
