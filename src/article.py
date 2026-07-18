from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


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
    type: ArticleType | None

    published_at: datetime
    authors: list[Author]

    updated_at: datetime | None = None
    slug: str | None = None
    article_id: str | None = None

    tags: list[str] = field(default_factory=list)
    draft: bool = False
    language: str | None = None
    image: str | None = None
