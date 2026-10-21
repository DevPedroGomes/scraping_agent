"""O catalogo de modelos precisa existir no provider.

REGRESSAO REAL (2026-08-18): a Groq descomissionou `llama-3.3-70b-versatile` e
o modo gratuito do scraper passou a devolver "Unable to complete scrape" para
todo visitante que tentasse um scrape real. O log do container mostrava
`404 model_not_found`, mas nada no CI comparava o catalogo publicado com o que
o provider ainda serve, entao a demo ficou quebrada em silencio.

Nome de modelo de terceiro e contrato que muda sem aviso. Este teste nao toca a
rede: prende o que da para prender offline, que e a coerencia interna do
catalogo e a ausencia dos nomes ja mortos.
"""

from app.models.schemas import ModelType, MODEL_PROVIDER_MAP, MODEL_PRICING, MODEL_CONTEXT_LIMITS


MODELOS_DESCOMISSIONADOS = {
    "llama-3.3-70b-versatile",   # Groq, saiu do catalogo em ago/2026
    "llama-3.1-70b-versatile",   # Groq, saiu antes
    "llama-3.1-8b-instant",      # Groq, saiu junto com o 70b e passou batido
                                 # na primeira correcao: a lista abaixo agora e
                                 # conferida contra /v1/models a cada auditoria
    "mixtral-8x7b-32768",        # Groq, saiu antes
}


def test_nenhum_modelo_descomissionado_no_catalogo():
    ativos = {m.value for m in ModelType}
    mortos = ativos & MODELOS_DESCOMISSIONADOS
    assert not mortos, f"modelo fora do catalogo do provider: {mortos}"


def test_todo_modelo_tem_provider_e_preco():
    # Modelo declarado sem provider vira KeyError na escolha do cliente, e sem
    # preco a estimativa de custo mostrada ao visitante mente.
    for m in ModelType:
        assert m in MODEL_PROVIDER_MAP, f"{m.value} sem provider"
        assert m in MODEL_PRICING, f"{m.value} sem preco"
        assert m in MODEL_CONTEXT_LIMITS, f"{m.value} sem limite de contexto"


def test_catalogo_do_frontend_bate_com_o_backend():
    # A pagina conta modelos e provedores a partir do MODEL_TO_PROVIDER do
    # frontend. Ja houve selo dizendo "6 providers", chip dizendo "5 modelos" e
    # dropdown com 16: tres numeros para a mesma coisa. Se o mapa do frontend
    # divergir do catalogo servido pela API, o numero exibido volta a mentir.
    import re
    from pathlib import Path

    types_ts = Path(__file__).resolve().parents[2] / "frontend" / "src" / "types" / "index.ts"
    if not types_ts.exists():  # imagem do backend nao carrega o frontend
        import pytest
        pytest.skip("frontend fora deste checkout")

    source = types_ts.read_text(encoding="utf-8")
    block = source.split("MODEL_TO_PROVIDER", 1)[1].split("};", 1)[0]
    pares = dict(re.findall(r'"([^"]+)":\s*"([^"]+)"', block))

    esperado = {m.value: MODEL_PROVIDER_MAP[m].value for m in ModelType}
    assert pares == esperado
