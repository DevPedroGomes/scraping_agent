"""
Amostras pre-gravadas para o modo showcase.

Elas existem para o visitante ver o FORMATO da saida sem gastar chave nem
esperar um scrape real. NAO sao scrape ao vivo: cada resposta carrega
`is_sample=True` e a interface rotula o resultado como amostra. Antes disso
os exemplos vinham com dados inventados (`https://example.com/1`) servidos com
"Cache Hit" e "0.01s", o que fazia a primeira interacao do visitante parecer
um scraper quebrado ou fake.
"""

from datetime import datetime, timezone

EXAMPLE_SCRAPES = [
    {
        "id": "hacker-news",
        "name": "Hacker News - Top Stories",
        "url": "https://news.ycombinator.com",
        "prompt": "Extract the top 5 stories with their title, URL, score, and author",
        "model": "llama-3.3-70b-versatile",
        "cached_response": {
            "success": True,
            "data": {
                "stories": [
                    {"title": "Show HN: A new open-source database engine", "url": "https://news.ycombinator.com/item?id=41205384", "score": 342, "author": "pg"},
                    {"title": "The Future of WebAssembly", "url": "https://news.ycombinator.com/item?id=41198722", "score": 287, "author": "dang"},
                    {"title": "Understanding Transformer Architecture", "url": "https://news.ycombinator.com/item?id=41187055", "score": 256, "author": "jl"},
                    {"title": "Rust vs Go: Performance Benchmarks 2025", "url": "https://news.ycombinator.com/item?id=41176390", "score": 198, "author": "tptacek"},
                    {"title": "Why SQLite is the Most Deployed Database", "url": "https://news.ycombinator.com/item?id=41168841", "score": 175, "author": "cperciva"},
                ]
            },
            "execution_time": 0.01,
            "model_used": "llama-3.3-70b-versatile",
            "provider_used": "groq",
            "tokens_used": 850,
            "estimated_cost": 0.0,
            "cache_hit": True,
            "is_sample": True,
            "markdown_used": True,
            "token_reduction": 72.3,
            "content_truncated": False,
            "fetch_time": 0.0,
            "parse_time": 0.0,
            "llm_time": 0.0,
        },
    },
    {
        "id": "github-trending",
        "name": "GitHub Trending - Top Repos",
        "url": "https://github.com/trending",
        "prompt": "Extract the top 5 trending repositories with name, description, language, and stars today",
        "model": "llama-3.3-70b-versatile",
        "cached_response": {
            "success": True,
            "data": {
                "repositories": [
                    {"name": "awesome-llm-apps", "description": "A curated list of awesome LLM-powered applications", "language": "Python", "stars_today": 1250},
                    {"name": "next-saas-starter", "description": "SaaS starter template with Next.js 15 and Supabase", "language": "TypeScript", "stars_today": 890},
                    {"name": "rustlings", "description": "Small exercises to get you used to reading and writing Rust code", "language": "Rust", "stars_today": 654},
                    {"name": "ollama", "description": "Get up and running with large language models locally", "language": "Go", "stars_today": 543},
                    {"name": "ui", "description": "Beautifully designed components built with Radix UI and Tailwind CSS", "language": "TypeScript", "stars_today": 432},
                ]
            },
            "execution_time": 0.01,
            "model_used": "llama-3.3-70b-versatile",
            "provider_used": "groq",
            "tokens_used": 920,
            "estimated_cost": 0.0,
            "cache_hit": True,
            "is_sample": True,
            "markdown_used": True,
            "token_reduction": 68.5,
            "content_truncated": False,
            "fetch_time": 0.0,
            "parse_time": 0.0,
            "llm_time": 0.0,
        },
    },
    {
        "id": "product-hunt",
        "name": "Product Hunt - Today's Top",
        "url": "https://www.producthunt.com",
        "prompt": "Extract the top 5 products launched today with name, tagline, and vote count",
        "model": "llama-3.3-70b-versatile",
        "cached_response": {
            "success": True,
            "data": {
                "products": [
                    {"name": "AI Code Review", "tagline": "Automated code review powered by GPT-5", "votes": 892},
                    {"name": "DesignKit Pro", "tagline": "Design system generator for React", "votes": 654},
                    {"name": "DataPipe", "tagline": "No-code ETL pipelines for startups", "votes": 543},
                    {"name": "ScreenCast AI", "tagline": "Turn screen recordings into tutorials", "votes": 432},
                    {"name": "APIForge", "tagline": "Generate REST APIs from database schemas", "votes": 321},
                ]
            },
            "execution_time": 0.01,
            "model_used": "llama-3.3-70b-versatile",
            "provider_used": "groq",
            "tokens_used": 780,
            "estimated_cost": 0.0,
            "cache_hit": True,
            "is_sample": True,
            "markdown_used": True,
            "token_reduction": 71.2,
            "content_truncated": False,
            "fetch_time": 0.0,
            "parse_time": 0.0,
            "llm_time": 0.0,
        },
    },
]


def get_example_by_match(url: str, prompt: str) -> dict | None:
    """Find an example that matches the given URL and prompt."""
    for example in EXAMPLE_SCRAPES:
        if example["url"] == url and example["prompt"] == prompt:
            return example
    return None


def get_examples_list() -> list[dict]:
    """Lista as amostras disponiveis (sem o corpo pre-gravado)."""
    return [
        {
            "id": ex["id"],
            "name": ex["name"],
            "url": ex["url"],
            "prompt": ex["prompt"],
            "model": ex["model"],
        }
        for ex in EXAMPLE_SCRAPES
    ]
