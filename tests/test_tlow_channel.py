"""The lower threshold depends on the complaint's channel (tlow_short_text_rule.md)."""
from backend.services import dedup_r1


def test_short_text_sources_use_the_higher_lower_threshold():
    for source in ("google_play_store", "Play_Store", " chat ", "app_review"):
        assert dedup_r1.t_low_for(source) == dedup_r1.T_LOW_SHORT == 0.40


def test_other_channels_keep_the_default():
    for source in ("web_portal", "email", "bugzilla", None, ""):
        assert dedup_r1.t_low_for(source) == dedup_r1.T_LOW == 0.26
