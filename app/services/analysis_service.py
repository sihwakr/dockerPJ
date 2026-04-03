import re
from collections import Counter
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def count_tags(soup: BeautifulSoup) -> dict:
    """모든 HTML 태그 카운트"""
    tags = [tag.name for tag in soup.find_all()]
    return dict(Counter(tags))


def analyze_keywords(soup: BeautifulSoup, top_n: int = 50) -> dict:
    """단어 빈도 분석 (상위 N개)"""
    text = soup.get_text()
    # 단어 추출 (한글, 영어 모두 지원)
    words = re.findall(r'[가-힣a-zA-Z]{2,}', text.lower())
    word_counts = Counter(words)
    return dict(word_counts.most_common(top_n))


def analyze_links(soup: BeautifulSoup, base_url: str) -> dict:
    """내부/외부 링크 분류"""
    base_domain = urlparse(base_url).netloc
    internal_links = []
    external_links = []

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        parsed = urlparse(href)

        if not parsed.netloc or parsed.netloc == base_domain:
            internal_links.append(href)
        else:
            external_links.append(href)

    return {
        "internal_count": len(internal_links),
        "external_count": len(external_links),
        "internal_links": internal_links[:20],
        "external_links": external_links[:20]
    }


def analyze_images(soup: BeautifulSoup) -> dict:
    """이미지 태그, alt 속성 분석"""
    images = soup.find_all('img')
    total = len(images)
    missing_alt = sum(1 for img in images if not img.get('alt'))
    with_alt = total - missing_alt

    return {
        "total": total,
        "with_alt": with_alt,
        "missing_alt": missing_alt,
        "images": [
            {
                "src": img.get('src', ''),
                "alt": img.get('alt', '')
            }
            for img in images[:20]
        ]
    }


def analyze_text(soup: BeautifulSoup) -> dict:
    """단어/문장 수, 평균 길이"""
    text = soup.get_text()

    # 단어 분석
    words = text.split()
    word_count = len(words)
    avg_word_length = sum(len(w) for w in words) / max(word_count, 1)

    # 문장 분석
    sentences = re.split(r'[.!?。]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(sentence_count, 1)

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": round(avg_word_length, 2),
        "avg_sentence_length": round(avg_sentence_length, 2),
        "total_characters": len(text)
    }


def analyze_dom_depth(soup: BeautifulSoup) -> int:
    """DOM 트리 깊이 측정"""
    def get_depth(element, current_depth=0):
        max_depth = current_depth
        for child in element.children:
            if hasattr(child, 'children'):
                child_depth = get_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth

    return get_depth(soup)


def analyze_html(html: str, url: str) -> dict:
    """위 모든 기능 통합 호출"""
    soup = BeautifulSoup(html, 'html.parser')

    return {
        "url": url,
        "html_length": len(html),
        "tag_counts": count_tags(soup),
        "keyword_frequency": analyze_keywords(soup),
        "link_stats": analyze_links(soup, url),
        "image_stats": analyze_images(soup),
        "text_stats": analyze_text(soup),
        "dom_depth": analyze_dom_depth(soup)
    }
