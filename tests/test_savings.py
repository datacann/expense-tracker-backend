import pytest
from pydantic import ValidationError

from app.routes.savings import CategoryTotal, ProposedSuggestion, ProposedSuggestions, SavingsRequest, finalize_suggestions


def payload(**changes):
    data = dict(month='2026-10', totalMinor=1_000_000, recordCount=2, limitMinor=None, historyComplete=False,
                categories=[CategoryTotal(categoryId='cat_dining', amountMinor=1_000_000)])
    data.update(changes)
    return SavingsRequest(**data)


def test_without_limit_and_deterministic_saving():
    result = finalize_suggestions(payload(), ProposedSuggestions(suggestions=[ProposedSuggestion(
        categoryId='cat_dining', reductionPercent=10, basis='Kategori toplamı', change='Gelecekte isteğe bağlı azaltım'
    )]))
    assert result[0]['estimatedSavingMinor'] == 100_000


def test_rejects_inconsistent_totals_unknown_category_and_bad_rate():
    with pytest.raises(ValidationError):
        payload(totalMinor=999_999)
    with pytest.raises(ValidationError):
        ProposedSuggestion(categoryId='unknown', reductionPercent=10, basis='x', change='y')
    with pytest.raises(ValidationError):
        ProposedSuggestion(categoryId='cat_dining', reductionPercent=80, basis='x', change='y')


def test_rejects_duplicate_category_and_never_exceeds_category_amount():
    suggestion = ProposedSuggestion(categoryId='cat_dining', reductionPercent=30, basis='x', change='y')
    with pytest.raises(ValueError):
        finalize_suggestions(payload(), ProposedSuggestions(suggestions=[suggestion, suggestion]))
    result = finalize_suggestions(payload(), ProposedSuggestions(suggestions=[suggestion]))
    assert 0 < result[0]['estimatedSavingMinor'] <= 1_000_000
