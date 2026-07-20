import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
from unittest.mock import patch

import frontmatter

import article
from article import (
    Article,
    ArticleMetadata,
    ArticleType,
    Author,
    article_type_to_template,
    extract_metadata,
    get_article_type,
    parse_authors,
    parse_published_datetime,
    parse_updated_datetime,
)


class ArticleTestCase(unittest.TestCase):
    """Shared metadata fixtures for article.py tests."""

    def valid_metadata(self, **overrides):
        metadata = {
            "title": "Building an RSS Feed",
            "description": "Notes on adding RSS support to a static site generator.",
            "type": "blog_post",
            "published_at": "2026-07-20T08:30:00-06:00",
            "updated_at": "2026-07-21T09:45:00-06:00",
            "authors": [
                {
                    "name": "Andrew Example",
                    "email": "andrew@example.com",
                }
            ],
            "slug": "building-an-rss-feed",
            "article_id": "urn:example:article:rss-feed",
            "tags": ["python", "rss", "static-site-generator"],
            "draft": True,
            "language": "en-US",
            "image": "/images/rss-feed.png",
        }
        metadata.update(overrides)
        return metadata


class TestArticleType(unittest.TestCase):
    def test_get_article_type_converts_each_supported_string(self):
        cases = {
            "index": ArticleType.INDEX,
            "blog_post": ArticleType.BLOG_POST,
            "article": ArticleType.ARTICLE,
            "contact": ArticleType.CONTACT,
            "about": ArticleType.ABOUT,
        }

        for raw_value, expected in cases.items():
            with self.subTest(raw_value=raw_value):
                self.assertEqual(get_article_type(raw_value), expected)

    def test_get_article_type_rejects_unknown_value(self):
        with self.assertRaisesRegex(ValueError, "invalid article type"):
            get_article_type("news")

    def test_article_type_to_template_uses_specialized_templates(self):
        cases = {
            ArticleType.INDEX: "index_template.html",
            ArticleType.BLOG_POST: "blog_template.html",
            ArticleType.CONTACT: "contact_template.html",
        }

        for article_type, expected in cases.items():
            with self.subTest(article_type=article_type):
                self.assertEqual(
                    article_type_to_template(article_type, "default.html"),
                    expected,
                )

    def test_article_type_to_template_uses_default_for_other_types(self):
        for article_type in (ArticleType.ARTICLE, ArticleType.ABOUT, None):
            with self.subTest(article_type=article_type):
                self.assertEqual(
                    article_type_to_template(article_type, "default.html"),
                    "default.html",
                )


class TestDatetimeParsing(unittest.TestCase):
    def test_parse_published_datetime_accepts_timezone_offset(self):
        parsed = parse_published_datetime("2026-07-20T08:30:00-06:00")

        self.assertEqual(
            parsed,
            datetime(
                2026,
                7,
                20,
                8,
                30,
                tzinfo=timezone(timedelta(hours=-6)),
            ),
        )

    def test_parse_published_datetime_rejects_invalid_iso_datetime(self):
        with self.assertRaisesRegex(ValueError, "Invalid publication datetime"):
            parse_published_datetime("July 20, 2026")

    def test_parse_published_datetime_requires_timezone(self):
        with self.assertRaisesRegex(ValueError, "must include a timezone offset"):
            parse_published_datetime("2026-07-20T08:30:00")

    def test_parse_updated_datetime_returns_none_for_missing_value(self):
        self.assertIsNone(parse_updated_datetime(None))
        self.assertIsNone(parse_updated_datetime(""))

    def test_parse_updated_datetime_accepts_timezone_offset(self):
        parsed = parse_updated_datetime("2026-07-21T09:45:00+00:00")

        self.assertEqual(
            parsed,
            datetime(2026, 7, 21, 9, 45, tzinfo=timezone.utc),
        )

    def test_parse_updated_datetime_requires_timezone(self):
        with self.assertRaisesRegex(ValueError, "must include a timezone offset"):
            parse_updated_datetime("2026-07-21T09:45:00")


class TestParseAuthors(unittest.TestCase):
    def test_parse_authors_builds_author_objects(self):
        result = parse_authors(
            [
                {"name": "Ada Lovelace", "email": "ada@example.com"},
                {"name": "Grace Hopper"},
            ]
        )

        self.assertEqual(
            result,
            [
                Author("Ada Lovelace", "ada@example.com"),
                Author("Grace Hopper"),
            ],
        )

    def test_parse_authors_skips_entries_without_a_name(self):
        result = parse_authors(
            [
                {"name": "Ada Lovelace"},
                {"email": "missing-name@example.com"},
            ]
        )

        self.assertEqual(result, [Author("Ada Lovelace")])

    def test_parse_authors_uses_default_when_first_entry_has_no_name(self):
        output = StringIO()

        with (
            patch.object(article, "DEFAULT_AUTHOR", "Default Author"),
            patch.object(article, "DEFAULT_AUTHOR_EMAIL", "default@example.com"),
            redirect_stdout(output),
        ):
            result = parse_authors([{}])

        self.assertEqual(
            result,
            [Author("Default Author", "default@example.com")],
        )
        self.assertIn("Author not present", output.getvalue())


class TestExtractMetadata(ArticleTestCase):
    def test_extract_metadata_rejects_none(self):
        with self.assertRaisesRegex(ValueError, "metadata is required"):
            extract_metadata(None)

    def test_extract_metadata_reports_each_missing_required_field(self):
        for missing_field in ("title", "description", "published_at", "authors"):
            metadata = self.valid_metadata()
            del metadata[missing_field]

            with self.subTest(missing_field=missing_field):
                with self.assertRaisesRegex(
                    ValueError,
                    rf"Missing required fields:.*{missing_field}",
                ):
                    extract_metadata(metadata)

    def test_extract_metadata_builds_complete_article_metadata(self):
        result = extract_metadata(self.valid_metadata())

        self.assertIsInstance(result, ArticleMetadata)
        self.assertEqual(result.title, "Building an RSS Feed")
        self.assertEqual(
            result.description,
            "Notes on adding RSS support to a static site generator.",
        )
        self.assertEqual(result.article_type, ArticleType.BLOG_POST)
        self.assertEqual(
            result.published_at,
            datetime(
                2026,
                7,
                20,
                8,
                30,
                tzinfo=timezone(timedelta(hours=-6)),
            ),
        )
        self.assertEqual(
            result.updated_at,
            datetime(
                2026,
                7,
                21,
                9,
                45,
                tzinfo=timezone(timedelta(hours=-6)),
            ),
        )
        self.assertEqual(
            result.authors,
            [Author("Andrew Example", "andrew@example.com")],
        )
        self.assertEqual(result.slug, "building-an-rss-feed")
        self.assertEqual(result.article_id, "urn:example:article:rss-feed")
        self.assertEqual(result.tags, ["python", "rss", "static-site-generator"])
        self.assertTrue(result.draft)
        self.assertEqual(result.language, "en-US")
        self.assertEqual(result.image, "/images/rss-feed.png")

    def test_extract_metadata_treats_non_boolean_draft_as_false(self):
        for draft_value in ("true", "false", 1, 0, None):
            with self.subTest(draft_value=draft_value):
                result = extract_metadata(self.valid_metadata(draft=draft_value))
                self.assertFalse(result.draft)

    def test_article_holds_metadata_and_markdown_body(self):
        metadata = extract_metadata(self.valid_metadata())
        body = "# Building an RSS Feed\n\nArticle body."

        result = Article(metadata=metadata, body=body)

        self.assertIs(result.metadata, metadata)
        self.assertEqual(result.body, body)

    # @unittest.expectedFailure
    def test_extract_metadata_defaults_missing_type_to_article(self):
        metadata = self.valid_metadata()
        del metadata["type"]

        result = extract_metadata(metadata)

        self.assertEqual(result.article_type, ArticleType.ARTICLE)

    # @unittest.expectedFailure
    def test_extract_metadata_defaults_missing_tags_to_empty_list(self):
        metadata = self.valid_metadata()
        del metadata["tags"]

        result = extract_metadata(metadata)

        self.assertEqual(result.tags, [])


class TestFrontmatterIntegration(unittest.TestCase):
    def test_extract_metadata_accepts_frontmatter_with_quoted_datetimes(self):
        document = """---
title: Frontmatter Test
description: Metadata parsed from a Markdown document
type: article
published_at: "2026-07-20T08:30:00-06:00"
authors:
  - name: Andrew Example
    email: andrew@example.com
tags:
  - python
---
# Body
"""
        metadata, body = frontmatter.parse(document)

        result = extract_metadata(metadata)
        article_result = Article(result, body)

        self.assertEqual(article_result.metadata.title, "Frontmatter Test")
        self.assertEqual(article_result.metadata.article_type, ArticleType.ARTICLE)
        self.assertEqual(
            article_result.metadata.authors,
            [Author("Andrew Example", "andrew@example.com")],
        )
        self.assertEqual(article_result.body.strip(), "# Body")

    # @unittest.expectedFailure
    def test_extract_metadata_accepts_frontmatter_datetime_objects(self):
        """Unquoted YAML timestamps are parsed as datetime objects."""
        document = """---
title: Frontmatter Datetime Test
description: Test unquoted YAML timestamps
type: article
published_at: 2026-07-20T08:30:00-06:00
updated_at: 2026-07-21T09:45:00-06:00
authors:
  - name: Andrew Example
tags: []
---
# Body
"""
        metadata, _ = frontmatter.parse(document)

        result = extract_metadata(metadata)

        self.assertIsInstance(result.published_at, datetime)
        self.assertIsInstance(result.updated_at, datetime)
        self.assertIsNotNone(result.published_at.tzinfo)
        self.assertIsNotNone(result.updated_at.tzinfo)


if __name__ == "__main__":
    unittest.main()
