from autotestdesign.examples.loader import list_examples, load_example


def test_list_examples_returns_expected_entries():
    names = list_examples()
    assert "banking_registration" in names
    assert "shopping_cart" in names


def test_load_example_banking_returns_requirements():
    reqs = load_example("banking_registration")
    assert len(reqs) == 6
    assert reqs[0].id == "REQ-001"


def test_load_example_shopping_returns_requirements():
    reqs = load_example("shopping_cart")
    assert len(reqs) == 4
    # 中文示例:断言包含关键业务术语
    assert "购物车" in reqs[0].raw_text
