from article import Article, ArticleType
from constants import TIME_ZONE
from datetime import datetime
from zoneinfo import ZoneInfo
from collections.abc import Iterable
from html import escape


def article_to_card(article: Article) -> str:
    metadata = article.metadata

    title = escape(metadata.title)
    description = escape(metadata.description)
    author_name = escape(metadata.authors[0].name)
    url = f"/blog/{article.metadata.slug}.html"

    published_text = metadata.published_at.strftime("%Y-%m-%d")
    published_datetime = metadata.published_at.isoformat()

    return f"""
<li class="post-card">
  <article>
    <a class="post-card__link" href="{url}">
      <div class="post-card__meta">
        <time datetime="{published_datetime}">
          {published_text}
        </time>
        <span>{author_name}</span>
      </div>

      <h2 class="post-card__title">{title}</h2>

      <p class="post-card__description">
        {description}
      </p>

      <span class="post-card__action" aria-hidden="true">
        read article -&gt;
      </span>
    </a>
  </article>
</li>
""".strip()


def articles_to_card_list(articles: list[Article]) -> str:
    cards = "\n".join(article_to_card(article) for article in articles)

    return f"""
<ul class="post-list">
{cards}
</ul>
""".strip()


def get_visible_articles(
    articles: Iterable[Article],
    *,
    now: datetime | None = None,
    ignored_type: list[ArticleType] = [],
) -> list[Article]:
    if now is None:
        now = datetime.now(ZoneInfo(TIME_ZONE))

    return sorted(
        (
            article
            for article in articles
            if not article.metadata.draft
            and article.metadata.published_at <= now
            and article.metadata.article_type not in ignored_type
        ),
        key=lambda article: article.metadata.published_at,
        reverse=True,
    )


def generate_blog_cards(html_template: str, card_list: str):
    return html_template.replace("{{ posts }}", card_list)
