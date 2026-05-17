# Bronze, Silver, Gold PDF Naming

Use ASCII lowercase plus underscores only. Avoid spaces, parentheses, apostrophes, locale-specific characters, and decorative suffixes such as `neu`, `copy`, `final-final`, or dates copied from the download name unless they are part of the document identity.

## Layers

- Bronze: the source file exactly as received.
- Silver: the repaired derivative that preserves provenance and records the transform.
- Gold: the canonical delivery filename meant to survive copying across shells, scripts, sync tools, browsers, and operating systems.

## Silver Pattern

Use:

```text
{source_stem_slug}__silver__{page_mode}_rotate_{angle}_fit.pdf
```

Example:

```text
arthur_zakirov_ausweis_scan_neu__silver__portrait_rotate_90_fit.pdf
```

## Gold Pattern

Use:

```text
{subject_slug}__{document_type_slug}.pdf
```

If the subject name is unknown or should be omitted, use:

```text
{document_type_slug}.pdf
```

Recommended document type slugs:

- `personal_id`
- `passport`
- `drivers_license`

Example:

```text
arthur_zakirov__personal_id.pdf
```

## Slug Rules

- Transliterate to ASCII.
- Lowercase everything.
- Replace every run of non-alphanumeric characters with `_`.
- Collapse repeated underscores.
- Remove leading and trailing underscores.
- Keep the `.pdf` extension lowercase.
