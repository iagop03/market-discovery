from market_discovery.models import Niche

CATEGORY_KEYWORDS = {
    "backend": ["api", "server", "database", "backend", "microservice"],
    "frontend": ["ui", "frontend", "react", "css", "component"],
    "devops": ["deploy", "ci/cd", "docker", "kubernetes", "infra"],
    "data": ["data", "analytics", "etl", "pipeline", "ml"],
    "security": ["auth", "security", "encryption", "vulnerability"],
}


class Categorizer:
    """Assigns a coarse category to a niche using keyword matching — cheap and explainable."""

    def categorize(self, niche: Niche) -> Niche:
        title_lower = niche.title.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in title_lower for keyword in keywords):
                niche.category = category
                return niche
        niche.category = "other"
        return niche
