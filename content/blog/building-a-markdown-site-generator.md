---
title: "Building a Markdown Site Generator"
description: "Why I replaced simple delimiter splitting with a structured Markdown tree."
type: blog_post

published_at: "2026-07-18T22:13:40-06:00"
updated_at: "2026-07-18T22:13:45-06:00"

slug: building-a-markdown-site-generator
article_id: "urn:uuid:cfd9ad85-8691-4d2d-bfa3-402177a97f9f"

authors:
  - name: Andrew
    email: andrew@example.com

tags:
  - markdown
  - parsing
  - static-site-generators

draft: false
image: /images/markdown-ast.png
---
# Building a Markdown Site Generator

This site you're seeing now started out as a [boot.dev](https://www.boot.dev/) guided project, designed to help students build a markdown file parser that translates them into HTML files, and serves them with python's built in http server. The finished project came with support for **bold** text, _italic_ text, `code` text, [links](https://www.youtube.com/watch?v=XfELJU1mRMg), and [images](https://www.flaticon.com/free-icons/triangles) ![images](/images/arrows.png).

> It supports block quotes

- It also supports
- Unordered lists
- like these

1. As well as
2. Ordered lists
3. like so.

~~~
Code blocks are also supported.
~~~

This was a great start, but one thing that really bothered me about this project is **that it _refused_ to teach me** _how to allow **nested bold** and italic_ text. So I took it upon myself to overengineer the solution, which inspired this project to grow into my own [_jekyll_](https://jekyllrb.com/) _wannabe_.

## But Before I Continue

| Take a look                | At What          | I Have Done              |
|:---------------------------|:----------------:|-------------------------:|
| **Tables** with            | differently      | alligned columns         |
| Markdown frontmatter       | is now supported | Metadata collected       |
| RSS/Atom feeds             | ❌ To Do         | but coming soon          |
| `**support _for_ nested**` | **markdown _text_ styles** | with proper code parsing |




