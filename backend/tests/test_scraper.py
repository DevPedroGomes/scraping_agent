"""O catalogo de modelos precisa existir no provider.

REGRESSAO REAL (2026-08-18): a Groq descomissionou `llama-3.3-70b-versatile` e
o modo gratuito do scraper passou a devolver "Unable to complete scrape" para
todo visitante que tentasse um scrape real. O log mostrava
`404 model_not_found`, mas nada no CI comparava o catalogo publicado com o que
o provider ainda serve.

Nome de modelo de terceiro e contrato que muda sem aviso. Este teste nao chama
a rede: ele prende o que da para prender offline, que e a coerencia interna do
catalogo e a ausencia do nome morto.
"""

from app.models.schemas import ModelType, MODEL_PROVIDER, MODEL_PRICING


MODELOS_DESCOMISSIONADOS = {
    "llama-3.3-70b-versatile",   # Groq, saiu do catalogo em ago/2026
    "llama-3.1-70b-versatile",   # Groq, saiu antes
    "mixtral-8x7b-32768",        # Groq, saiu antes
}


def test_nenhum_modelo_descomissionado_no_catalogo():
    ativos = {m.value for m in ModelType}
    mortos = ativos & MODELOS_DESCOMISSIONADOS
    assert not mortos, f"modelo fora do catalogo do provider: {mortos}"


def test_todo_modelo_tem_provider_e_preco():
    # Modelo declarado sem provider vira KeyError na hora de escolher o cliente,
    # e sem preco a estimativa de custo mente.
    for m in ModelType:
        assert m in MODEL_PROVIDER, f"{m.value} sem provider"
        assert m in MODEL_PRICING, f"{m.value} sem preco"
