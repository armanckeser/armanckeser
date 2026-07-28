"""Download book cover images from Open Library into `assets/covers/`.

The README pins a small number of covers as its only images. Committing them keeps
the profile page independent of Open Library's uptime and of GitHub's image proxy
cache. Run this script when a book is added to one of the cover rows.

Usage:
    uv run python tools/fetch_covers.py
    uv run python tools/fetch_covers.py --resolve "The SaaS Playbook Rob Walling"

Note: behind a TLS-intercepting proxy this fails with CERTIFICATE_VERIFY_FAILED,
because a pyenv Python does not read the macOS keychain. Drop off the VPN, or fall
back to `curl -sL -o assets/covers/<slug>.jpg <cover url>`, which does.
"""

import argparse
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
COVERS_DIRECTORY = REPOSITORY_ROOT / "assets" / "covers"

COVER_BY_ID_URL = "https://covers.openlibrary.org/b/id/{key}-L.jpg"
COVER_BY_ISBN_URL = "https://covers.openlibrary.org/b/isbn/{key}-L.jpg?default=false"
SEARCH_URL = "https://openlibrary.org/search.json"
REQUEST_TIMEOUT = timedelta(seconds=30)


@dataclass(frozen=True)
class CoverById:
    """An edition addressed by its Open Library cover ID."""

    cover_id: int


@dataclass(frozen=True)
class CoverByIsbn:
    """An edition addressed by ISBN.

    Used where search ranks a poor edition first: search returns whatever Open
    Library scores highest, which for some titles is an audiobook or a boxed set.
    """

    isbn: str


CoverSource = CoverById | CoverByIsbn

# Pinned so a re-run always fetches the same edition rather than whatever currently
# ranks first. Resolve new entries with --resolve, then eyeball the result.
SHELF: dict[str, CoverSource] = {
    "obviously-awesome": CoverById(10194369),
    "shape-up": CoverById(12600273),
    "mom-test": CoverById(10660557),
    # Search returns the 2001 McGraw-Hill Audio cover; this is the 3rd edition.
    "crucial-conversations": CoverByIsbn("9781260474183"),
    "explosive-growth": CoverById(11824198),
    "traction": CoverById(9364675),
    "how-big-things-get-done": CoverById(13247891),
    "saas-playbook": CoverById(14624002),
    "innovators-dilemma": CoverById(9274687),
    "thinking-machine": CoverById(15131358),
}


class CoverUnavailableError(Exception):
    """Raised when Open Library has no cover image for a requested edition."""


class EditionNotFoundError(Exception):
    """Raised when a title query matches no Open Library edition with a cover."""


def resolve_cover_id(query: str) -> int:
    """Look up the Open Library cover ID for a book.

    Args:
        query: Free-text title and author, e.g. "The SaaS Playbook Rob Walling".

    Returns:
        The numeric cover ID of the best-matching edition that has a cover.

    Raises:
        EditionNotFoundError: If no result carries a cover image.
    """
    parameters = urllib.parse.urlencode(
        {"q": query, "fields": "title,author_name,cover_i", "limit": 5}
    )
    request = urllib.request.Request(
        f"{SEARCH_URL}?{parameters}", headers={"User-Agent": "armanckeser-readme"}
    )
    with urllib.request.urlopen(
        request, timeout=REQUEST_TIMEOUT.total_seconds()
    ) as response:
        payload = json.load(response)

    for document in payload.get("docs", []):
        cover_id = document.get("cover_i")
        if cover_id is None:
            continue
        authors = document.get("author_name") or ["unknown"]
        print(f'  matched "{document.get("title")}" by {authors[0]} -> {cover_id}')
        return int(cover_id)

    raise EditionNotFoundError(f"no edition with a cover for: {query}")


def download_cover(slug: str, source: CoverSource) -> Path:
    """Write one cover image to `assets/covers/<slug>.jpg`.

    Args:
        slug: Filename stem used by the README's `<img src>`.
        source: Which Open Library edition to fetch.

    Returns:
        The path written.

    Raises:
        CoverUnavailableError: If Open Library returns a placeholder or non-JPEG body.
    """
    match source:
        case CoverById(cover_id):
            url = COVER_BY_ID_URL.format(key=cover_id)
        case CoverByIsbn(isbn):
            url = COVER_BY_ISBN_URL.format(key=isbn)

    request = urllib.request.Request(url, headers={"User-Agent": "armanckeser-readme"})
    with urllib.request.urlopen(
        request, timeout=REQUEST_TIMEOUT.total_seconds()
    ) as response:
        image_bytes = response.read()

    # Open Library answers a missing cover with a tiny 1x1 GIF rather than a 404.
    if not image_bytes.startswith(b"\xff\xd8"):
        raise CoverUnavailableError(f"{slug}: {source} did not return a JPEG")

    COVERS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = COVERS_DIRECTORY / f"{slug}.jpg"
    destination.write_bytes(image_bytes)
    return destination


def main() -> None:
    """Resolve a single title, or download every cover pinned in `SHELF`."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--resolve",
        metavar="QUERY",
        help="print the cover ID for a title instead of downloading",
    )
    arguments = parser.parse_args()

    if arguments.resolve is not None:
        print(resolve_cover_id(arguments.resolve))
        return

    for slug, source in SHELF.items():
        destination = download_cover(slug, source)
        kilobytes = destination.stat().st_size // 1024
        print(f"{slug:26} {kilobytes:>4}KB  {destination.relative_to(REPOSITORY_ROOT)}")


if __name__ == "__main__":
    main()
