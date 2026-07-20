from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from constants import LANGUAGE, DEFAULT_AUTHOR, DEFAULT_AUTHOR_EMAIL


class ArticleType(Enum):
    INDEX = "index"
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    CONTACT = "contact"
    ABOUT = "about"


def get_article_type(type_str: str) -> ArticleType:
    if type_str == "index":
        return ArticleType.INDEX
    if type_str == "blog_post":
        return ArticleType.BLOG_POST
    if type_str == "article":
        return ArticleType.ARTICLE
    if type_str == "contact":
        return ArticleType.CONTACT
    if type_str == "about":
        return ArticleType.ABOUT
    raise ValueError("invalid article type")


def article_type_to_template(
    article_type: ArticleType | None, default_template: str
) -> str:
    if article_type == ArticleType.INDEX:
        return "index_template.html"
    if article_type == ArticleType.BLOG_POST:
        return "blog_template.html"
    if article_type == ArticleType.CONTACT:
        return "contact_template.html"
    return default_template


@dataclass
class Article:
    metadata: ArticleMetadata
    body: str


@dataclass(frozen=True)
class Author:
    name: str
    email: str | None = None
    uri: str | None = None


@dataclass
class ArticleMetadata:
    title: str
    description: str
    article_type: ArticleType | None

    published_at: datetime
    authors: list[Author]

    updated_at: datetime | None = None
    slug: str | None = None
    article_id: str | None = None

    tags: list[str] = field(default_factory=list)
    draft: bool = False
    language: str | None = None
    image: str | None = None


def extract_metadata(metadata) -> ArticleMetadata:
    if metadata is None:
        raise ValueError("metadata is required")

    required = ("title", "description", "published_at", "authors")
    missing = [field for field in required if field not in metadata]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    return ArticleMetadata(
        title=metadata["title"],
        description=metadata["description"],
        published_at=parse_published_datetime(metadata["published_at"]),
        updated_at=parse_updated_datetime(metadata.get("updated_at")),
        article_type=get_article_type(metadata.get("type", ArticleType.ARTICLE)),
        authors=parse_authors(metadata.get("authors", [])),
        slug=metadata.get("slug"),
        article_id=metadata.get("article_id"),
        tags=metadata.get("tags"),
        draft=(
            metadata.get("draft", False)
            if isinstance(metadata.get("draft"), bool)
            else False
        ),
        image=metadata.get("image"),
        language=metadata.get("language", LANGUAGE),
    )


def parse_authors(authors_data) -> list[Author]:
    authors: list[Author] = []

    if "name" not in authors_data[0]:
        print(" Author not present in metadata")
        print(f"Using... name: '{DEFAULT_AUTHOR}' email: '{DEFAULT_AUTHOR_EMAIL}'")
        authors.append(Author(DEFAULT_AUTHOR, DEFAULT_AUTHOR_EMAIL))

    for author in authors_data:
        name = author.get("name")
        if not name:
            continue

        email = author.get("email")
        authors.append(Author(name, email) if email else Author(name))

    return authors


def parse_updated_datetime(value: str) -> datetime | None:
    if value is None or value == "":
        return None
    try:
        parsed = datetime.fromisoformat(value)

    except ValueError as error:
        raise ValueError(f"Invalid publication datetime {value!r}") from error

    if parsed.tzinfo is None:
        raise ValueError("Publication datetime must include a timezone offset")

    return parsed


def parse_published_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Invalid publication datetime {value!r}") from error

    if parsed.tzinfo is None:
        raise ValueError("Publication datetime must include a timezone offset")

    return parsed
