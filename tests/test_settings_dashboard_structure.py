"""Regression checks for the settings dashboard's backwards-compatible bindings."""
from pathlib import Path

PANEL = Path(__file__).resolve().parents[1] / "custom_components" / "declan_local" / "panel.js"


def test_settings_categories_and_navigation():
    source = PANEL.read_text(encoding="utf-8")
    for category in ("home", "voice", "personality", "media", "advanced"):
        assert f'data-page="{category}"' in source
        assert f'data-settings-page="{category}"' in source
    assert "selectSettingsPage(page)" in source
    assert 'section.hidden=section.dataset.page!==selected' in source


def test_all_entity_settings_are_saved_across_pages():
    source = PANEL.read_text(encoding="utf-8")
    assert "querySelectorAll('.settings-page select[data-key]')" in source
    assert "data[select.dataset.key]=select.value" in source
    assert "this.settingsCategory(key)" in source
    assert "this.settings?.[key]" in source


def test_existing_save_paths_and_voice_profile_controls_retained():
    source = PANEL.read_text(encoding="utf-8")
    for required in (
        "declan_local/save_settings",
        "saveMediaSearchSettings()",
        "saveProfiles()",
        "checkSatelliteMappings()",
        'class="profile-fields"',
        'class="switch-fields"',
        'class="satellite-fields"',
        'class="media-search-settings"',
        'class="save-settings"',
    ):
        assert required in source
