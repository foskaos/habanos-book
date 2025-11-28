#!/usr/bin/env python3
"""
Split book.md into mdBook chapter structure.
"""

import re
import shutil
from pathlib import Path


def slugify(title: str) -> str:
    """Convert title to filename-safe slug."""
    # Remove special chars, lowercase, replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug


def split_book():
    base_dir = Path(__file__).parent
    book_md = base_dir.parent / "book.md"
    src_dir = base_dir / "src"

    # Read the full book
    content = book_md.read_text(encoding="utf-8")

    # Skip title and TOC - find first ## header after TOC
    # TOC ends with the "---" separator
    toc_end = content.find("\n---\n")
    if toc_end == -1:
        toc_end = 0
    else:
        toc_end += 5  # Skip past "---\n"

    main_content = content[toc_end:]

    # Split by ## headers (main chapters)
    chapter_pattern = r'^## (.+)$'
    chapters = re.split(chapter_pattern, main_content, flags=re.MULTILINE)

    # chapters[0] is content before first ##, then alternating: title, content, title, content...
    chapters = chapters[1:]  # Skip any content before first chapter

    summary_lines = ["# Summary\n\n"]
    chapter_num = 0

    for i in range(0, len(chapters), 2):
        title = chapters[i].strip()
        chapter_content = chapters[i + 1] if i + 1 < len(chapters) else ""
        chapter_num += 1

        # Check if this is the Brands chapter (has ### subsections for brands)
        if "Habanos Brands" in title or chapter_num == 19:
            # Create brands directory
            brands_dir = src_dir / "brands"
            brands_dir.mkdir(exist_ok=True)

            # Split brands by ### headers
            brand_pattern = r'^### (.+)$'
            brand_parts = re.split(brand_pattern, chapter_content, flags=re.MULTILINE)

            # Write intro content (before first brand)
            intro_content = brand_parts[0].strip()
            brands_index = brands_dir / "index.md"
            brands_index.write_text(f"# {title}\n\n{intro_content}\n", encoding="utf-8")

            summary_lines.append(f"- [{title}](brands/index.md)\n")

            # Process each brand
            brand_parts = brand_parts[1:]
            for j in range(0, len(brand_parts), 2):
                brand_title = brand_parts[j].strip()
                brand_content = brand_parts[j + 1] if j + 1 < len(brand_parts) else ""

                brand_slug = slugify(brand_title)
                brand_file = brands_dir / f"{brand_slug}.md"
                # Fix image paths for nested directory
                fixed_content = brand_content.replace("](book_images/", "](../book_images/")
                brand_file.write_text(f"# {brand_title}\n\n{fixed_content.strip()}\n", encoding="utf-8")

                summary_lines.append(f"  - [{brand_title}](brands/{brand_slug}.md)\n")
        else:
            # Regular chapter
            slug = slugify(title)
            chapter_file = src_dir / f"{slug}.md"
            chapter_file.write_text(f"# {title}\n\n{chapter_content.strip()}\n", encoding="utf-8")

            summary_lines.append(f"- [{title}]({slug}.md)\n")

    # Write SUMMARY.md
    summary_file = src_dir / "SUMMARY.md"
    summary_file.write_text("".join(summary_lines), encoding="utf-8")

    # Copy images
    images_src = base_dir.parent / "book_images"
    images_dst = src_dir / "book_images"
    if images_src.exists():
        if images_dst.exists():
            shutil.rmtree(images_dst)
        shutil.copytree(images_src, images_dst)
        print(f"Copied {len(list(images_dst.glob('*')))} images")

    print(f"Created {chapter_num} chapters")
    print(f"Summary written to {summary_file}")


if __name__ == "__main__":
    split_book()
