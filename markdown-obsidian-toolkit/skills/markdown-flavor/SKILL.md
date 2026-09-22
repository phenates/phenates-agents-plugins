---
name: markdown-flavor
version: 0.1.0
description: Write and edit Markdown following house conventions plus Obsidian Flavored Markdown syntax (wikilinks, embeds, callouts, properties). Use for any Markdown file the agent writes or edits, inside an Obsidian vault or not.
---

# Markdown Flavor

Write and edit valid Markdown for any file, applying house conventions first. When the file lives in (or will be opened by) Obsidian, this skill also covers Obsidian Flavored Markdown: extensions to CommonMark and GFM such as wikilinks, embeds, callouts, properties, and comments. Standard Markdown (headings, bold, italic, lists, quotes, code blocks, tables) is assumed knowledge -- this skill covers house conventions plus Obsidian-specific extensions only.

## House Conventions (always apply)

These rules apply to every Markdown file, regardless of syntax dialect below:

- **No H1 in the body.** The title is carried by the filename or the frontmatter `title` property -- never open a file with `# Title`.
- **No dedicated metadata section.** Metadata lives in YAML frontmatter only -- never add a `## Metadata` / `## Métadonnées` heading in the body.
- **No horizontal rule in the body.** `---` is reserved for the frontmatter delimiters only -- don't use it to separate sections in the body.
- **Fenced code blocks for multi-line code**, always with a language tag for syntax highlighting. Comment in English inside the code, even when the surrounding document is in French.
- **Inline code (backticks) for file names, file paths, commands, and variable names** -- e.g. `server.js`, `/etc/nginx/nginx.conf`, `npm install`, `maxConnections`.
- **Frontmatter fields**: use `title`, `aliases`, `created`, `tags` only. Don't add `modified`, `date`, `status`, or other properties unless the user explicitly asks for them.

## Workflow: Creating a Note

1. **Add frontmatter** with `title`, `aliases`, `created`, `tags` at the top of the file -- see House Conventions above. See [PROPERTIES.md](references/PROPERTIES.md) for property syntax.
2. **Write content** using standard Markdown for structure, plus Obsidian-specific syntax below.
3. **Link related notes** using wikilinks (`[[Note]]`) for internal vault connections, or standard Markdown links for external URLs.
4. **Embed content** from other notes, images, or PDFs using the `![[embed]]` syntax. See [EMBEDS.md](references/EMBEDS.md) for all embed types.
5. **Add callouts** for highlighted information using `> [!type]` syntax. See [CALLOUTS.md](references/CALLOUTS.md) for all callout types.
6. **Verify** the note renders correctly in Obsidian's reading view.

> When choosing between wikilinks and Markdown links: use `[[wikilinks]]` for notes within the vault (Obsidian tracks renames automatically) and `[text](url)` for external URLs only.

## Internal Links (Wikilinks)

```markdown
[[Note Name]]                          Link to note
[[Note Name|Display Text]]             Custom display text
[[Note Name#Heading]]                  Link to heading
[[Note Name#^block-id]]                Link to block
[[#Heading in same note]]              Same-note heading link
```

Define a block ID by appending `^block-id` to any paragraph:

```markdown
This paragraph can be linked to. ^my-block-id
```

For lists and quotes, place the block ID on a separate line after the block:

```markdown
> A quote block

^quote-id
```

## Embeds

Prefix any wikilink with `!` to embed its content inline:

```markdown
![[Note Name]]                         Embed full note
![[Note Name#Heading]]                 Embed section
![[image.png]]                         Embed image
![[image.png|300]]                     Embed image with width
![[document.pdf#page=3]]               Embed PDF page
```

See [EMBEDS.md](references/EMBEDS.md) for audio, video, search embeds, and external images.

## Callouts

```markdown
> [!note]
> Basic callout.

> [!warning] Custom Title
> Callout with a custom title.

> [!faq]- Collapsed by default
> Foldable callout (- collapsed, + expanded).
```

Common types: `note`, `tip`, `warning`, `info`, `example`, `quote`, `bug`, `danger`, `success`, `failure`, `question`, `abstract`, `todo`.

See [CALLOUTS.md](references/CALLOUTS.md) for the full list with aliases, nesting, and custom CSS callouts.

## Properties (Frontmatter)

```yaml
---
title: My Note
date: 2024-01-15
tags:
  - project
  - active
aliases:
  - Alternative Name
cssclasses:
  - custom-class
---
```

Default properties: `tags` (searchable labels), `aliases` (alternative note names for link suggestions), `cssclasses` (CSS classes for styling).

See [PROPERTIES.md](references/PROPERTIES.md) for all property types, tag syntax rules, and advanced usage.

## Tags

```markdown
#tag                    Inline tag
#nested/tag             Nested tag with hierarchy
```

Tags can contain letters, numbers (not first character), underscores, hyphens, and forward slashes. Tags can also be defined in frontmatter under the `tags` property.

## Comments

```markdown
This is visible %%but this is hidden%% text.

%%
This entire block is hidden in reading view.
%%
```

## Obsidian-Specific Formatting

```markdown
==Highlighted text==                   Highlight syntax
```

## Math (LaTeX)

```markdown
Inline: $e^{i\pi} + 1 = 0$

Block:
$$
\frac{a}{b} = c
$$
```

## Diagrams (Mermaid)

````markdown
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Do this]
    B -->|No| D[Do that]
```
````

Line breaks inside node/label text: use `<br/>`, never a literal `\n`.

To link Mermaid nodes to Obsidian notes, add `class NodeName internal-link;`.

## Footnotes

```markdown
Text with a footnote[^1].

[^1]: Footnote content.

Inline footnote.^[This is inline.]
```

## Complete Example

````markdown
---
title: Project Alpha
aliases:
  - Alpha
created: 2024-01-15
tags:
  - project
  - active
---

This project aims to [[improve workflow]] using modern techniques.

> [!important] Key Deadline
> The first milestone is due on ==January 30th==.

## Tasks

- [x] Initial planning
- [ ] Development phase
  - [ ] Backend implementation
  - [ ] Frontend design

## Notes

The algorithm uses $O(n \log n)$ sorting. See [[Algorithm Notes#Sorting]] for details.

![[Architecture Diagram.png|600]]

Reviewed in [[Meeting Notes 2024-01-10#Decisions]].
````

## See Also

For vault access mechanics (MCP tools, default save folder, Folder Notes, plugin quirks), see the `obsidian-vault` skill -- this skill covers syntax and house conventions only, not how to read/write the vault.

## References

- [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown)
- [Internal links](https://help.obsidian.md/links)
- [Embed files](https://help.obsidian.md/embeds)
- [Callouts](https://help.obsidian.md/callouts)
- [Properties](https://help.obsidian.md/properties)
