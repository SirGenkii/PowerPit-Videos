from powerpit.simple_yaml import safe_load


def test_list_of_mappings() -> None:
    content = """
teams:
  - name: Alpha
    color: "#FFFFFF"
  - name: Beta
    color: "#000000"
"""
    data = safe_load(content)
    assert isinstance(data, dict)
    assert len(data["teams"]) == 2
    assert data["teams"][0]["name"] == "Alpha"
