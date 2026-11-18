import json

import pytest

import validate_report as vr


def run(text, **kwargs):
    report = vr.Report()
    vr.validate_report(text, report, **kwargs)
    return report


def codes(report):
    return {issue.code for issue in report.errors}


def warning_codes(report):
    return {issue.code for issue in report.warnings}


def replace_once(text, old, new):
    assert old in text
    return text.replace(old, new, 1)


def valid_text(fixtures):
    return (fixtures / "valid_report.md").read_text(encoding="utf-8")


def test_valid_fixture_passes(fixtures):
    report = run(valid_text(fixtures))

    assert report.ok
    assert report.errors == []
    assert report.warnings == []


def test_missing_artifact_marker(fixtures):
    text = valid_text(fixtures).replace("<!-- angular-expert:artifact type=implementation version=1 -->", "")

    assert "missing-artifact-marker" in codes(run(text))


def test_duplicate_artifact_marker(fixtures):
    marker = "<!-- angular-expert:artifact type=implementation version=1 -->"
    text = replace_once(valid_text(fixtures), marker, f"{marker}\n{marker}")

    assert "duplicate-artifact-marker" in codes(run(text))


def test_wrong_artifact_type(fixtures):
    text = replace_once(valid_text(fixtures), "type=implementation", "type=review")

    assert "wrong-artifact-type" in codes(run(text))


def test_artifact_version_must_be_one(fixtures):
    text = replace_once(valid_text(fixtures), "version=1", "version=2")

    assert "artifact-version" in codes(run(text))


def test_duplicate_section_marker(fixtures):
    text = replace_once(
        valid_text(fixtures),
        "<!-- angular-expert:section id=tests -->",
        "<!-- angular-expert:section id=analysis -->\n<!-- angular-expert:section id=tests -->",
    )

    assert "duplicate-section" in codes(run(text))


def test_missing_section_marker(fixtures):
    text = valid_text(fixtures).replace("<!-- angular-expert:section id=evidence -->", "")

    assert "missing-section" in codes(run(text))


def test_coverage_below_gate(fixtures):
    text = replace_once(valid_text(fixtures), "Coverage: 88%", "Coverage: 70%")
    text = replace_once(text, "value=88", "value=70")

    assert "coverage-below-gate" in codes(run(text))


def test_missing_metadata_field(fixtures):
    text = valid_text(fixtures).replace("- Build Tool: npm\n", "")

    assert "missing-metadata" in codes(run(text))


def test_stack_mismatch_for_angular_version(fixtures):
    text = replace_once(valid_text(fixtures), "Angular Version: 20.3.0", "Angular Version: 21.0.0")

    assert "stack-mismatch" in codes(run(text))


def test_invalid_build_tool(fixtures):
    text = replace_once(valid_text(fixtures), "Build Tool: npm", "Build Tool: make")
    text = replace_once(text, "build=npm", "build=make")

    assert "invalid-build-tool" in codes(run(text))


def test_invalid_status(fixtures):
    text = replace_once(valid_text(fixtures), "Status: Final", "Status: pending")

    assert "invalid-status" in codes(run(text))


def test_invalid_date(fixtures):
    text = replace_once(valid_text(fixtures), "Date: 2026-11-18", "Date: 18-11-2026")

    assert "invalid-date" in codes(run(text))


def test_invalid_angular_version(fixtures):
    text = replace_once(valid_text(fixtures), "Angular Version: 20.3.0", "Angular Version: twenty")

    assert "invalid-angular-version" in codes(run(text))


def test_non_jest_runner_is_only_a_warning(fixtures):
    text = replace_once(valid_text(fixtures), "Test Runner: jest", "Test Runner: karma")
    text = replace_once(text, "test-runner=jest", "test-runner=karma")

    report = run(text)

    assert "non-jest-runner" in warning_codes(report)
    assert report.ok


def test_changes_count_mismatch(fixtures):
    text = replace_once(valid_text(fixtures), "Changes Applied: 1", "Changes Applied: 2")

    assert "count-mismatch" in codes(run(text))


def test_invalid_change_id(fixtures):
    text = replace_once(valid_text(fixtures), "id=CHG-001", "id=CHG-1")

    assert "invalid-change-id" in codes(run(text))


def test_missing_change_entry(fixtures):
    text = valid_text(fixtures).replace("<!-- angular-expert:change id=CHG-001 status=implemented -->", "")

    assert "missing-change" in codes(run(text))


def test_invalid_change_status(fixtures):
    text = replace_once(valid_text(fixtures), "status=implemented", "status=draft")

    assert "invalid-change-status" in codes(run(text))


def test_missing_test_entry(fixtures):
    marker = "<!-- angular-expert:test id=T-001 framework=jest testbed=true context=unit -->"
    text = valid_text(fixtures).replace(marker, "")

    assert "missing-test" in codes(run(text))


def test_testbed_required(fixtures):
    text = replace_once(valid_text(fixtures), "testbed=true", "testbed=false")

    assert "testbed-required" in codes(run(text))


def test_unit_context_required(fixtures):
    text = replace_once(valid_text(fixtures), "context=unit", "context=integration")

    assert "unit-context-required" in codes(run(text))


def test_jest_required_for_test_entry(fixtures):
    text = replace_once(valid_text(fixtures), "framework=jest", "framework=karma")

    assert "jest-required" in codes(run(text))


def test_jest_required_in_tests_section(fixtures):
    text = replace_once(valid_text(fixtures), "measured by Jest.", "measured by the framework.")

    assert "jest-required" in codes(run(text))


def test_configurations_require_explicit_no_changes(fixtures):
    text = replace_once(valid_text(fixtures), "No changes.", "Nothing to report.")

    assert "missing-config-declaration" in codes(run(text))


def test_config_entry_requires_property(fixtures):
    text = replace_once(
        valid_text(fixtures),
        "No changes.",
        "<!-- angular-expert:config id=CFG-001 file=src/environments/environment.ts -->\n"
        "- Reason: Bind the API base URL.",
    )

    assert "missing-config-property" in codes(run(text))


def test_invalid_config_file(fixtures):
    text = replace_once(
        valid_text(fixtures),
        "No changes.",
        "<!-- angular-expert:config id=CFG-001 file=/etc/passwd -->\n"
        "- Property: scripts.test\n- Reason: Bind the Jest test command.",
    )

    assert "invalid-config-file" in codes(run(text))


def test_missing_coverage_marker(fixtures):
    text = valid_text(fixtures).replace(
        "<!-- angular-expert:coverage value=88 gate=80 tool=jest -->", ""
    )

    assert "missing-coverage-marker" in codes(run(text))


def test_invalid_coverage_tool(fixtures):
    text = replace_once(valid_text(fixtures), "Coverage Tool: jest", "Coverage Tool: istanbul")

    assert "invalid-coverage-tool" in codes(run(text))


def test_insufficient_validation_checkboxes(fixtures):
    text = valid_text(fixtures)
    for line in [
        "- [x] Unit tests run with Jest.\n",
        "- [x] No manual subscriptions remain in the component.\n",
        "- [x] Artifact validated by validate_report.py.\n",
    ]:
        text = text.replace(line, "")

    assert "insufficient-validation" in codes(run(text))


def test_missing_evidence(fixtures):
    text = valid_text(fixtures).replace(
        "<!-- angular-expert:evidence id=EV-001 status=passed -->", ""
    )

    assert "missing-evidence" in codes(run(text))


def test_evidence_not_passed(fixtures):
    text = replace_once(valid_text(fixtures), "status=passed", "status=partial")

    assert "evidence-not-passed" in codes(run(text))


def test_traceability_gap(fixtures):
    text = replace_once(
        valid_text(fixtures), "| CHG-001 | T-001 | EV-001 |", "| CHG-002 | T-001 | EV-001 |"
    )

    assert "traceability-gap" in codes(run(text))


def test_placeholder_is_rejected(fixtures):
    text = replace_once(
        valid_text(fixtures), "- Design: Keep the component", "- Design: TODO finish mapping: Keep the component"
    )

    assert "placeholder" in codes(run(text))


def test_secret_is_rejected(fixtures):
    text = replace_once(
        valid_text(fixtures),
        "- Zone.js is not imported",
        "- token = ghp_abcdefghijklmnopqrstuvwxyz0123456789\n- Zone.js is not imported",
    )

    assert "secret" in codes(run(text))


def test_redacted_secrets_are_allowed(fixtures):
    text = replace_once(
        valid_text(fixtures),
        "- Zone.js is not imported",
        "- password: [REDACTED]\n- token = ${CI_TOKEN}\n- Zone.js is not imported",
    )

    assert run(text).ok


def test_approval_verdict_is_rejected(fixtures):
    text = replace_once(valid_text(fixtures), "- Zone.js is not imported", "LGTM")

    assert "approval-verdict" in codes(run(text))


def test_suppression_requires_approval(fixtures):
    text = replace_once(
        valid_text(fixtures),
        "- Zone.js is not imported",
        "Added @ts-ignore for the warning.",
    )

    assert "suppression-without-approval" in codes(run(text))


def test_approved_suppression_is_allowed(fixtures):
    text = replace_once(
        valid_text(fixtures),
        "- Zone.js is not imported",
        "Added @ts-ignore for a verified false positive. Suppression approved.",
    )

    assert run(text).ok


def test_custom_min_coverage_gate(fixtures):
    report = run(valid_text(fixtures), min_coverage=95)

    assert "coverage-below-gate" in codes(report)


def test_strict_mode_promotes_warnings(fixtures):
    text = valid_text(fixtures)
    assert run(text, strict=True).ok

    unverified = replace_once(
        text,
        "Detected from `package.json`, `angular.json` and `tsconfig.json`.",
        "Detected from the workspace.",
    )
    report = run(unverified, strict=True)

    assert "unverified-stack" in warning_codes(report)
    assert not report.ok


def test_report_to_dict(fixtures):
    payload = run(valid_text(fixtures)).to_dict("report.md")

    assert payload["path"] == "report.md"
    assert payload["status"] == "PASS"
    assert payload["errors"] == []
    assert payload["warnings"] == []


def test_json_cli_output(fixtures, tmp_path, capsys):
    path = tmp_path / "report.md"
    path.write_text(valid_text(fixtures), encoding="utf-8")

    code = vr.main([str(path), "--json"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"
    assert payload["reports"][0]["status"] == "PASS"


def test_cli_fails_on_invalid_report(fixtures, tmp_path, capsys):
    path = tmp_path / "report.md"
    path.write_text(replace_once(valid_text(fixtures), "Coverage: 88%", "Coverage: 70%"), encoding="utf-8")

    assert vr.main([str(path)]) == 1
    assert "[ERROR]" in capsys.readouterr().out


def test_jest_setup_files_are_allowed_config_files(fixtures):
    text = replace_once(
        valid_text(fixtures),
        "No changes.",
        "<!-- angular-expert:config id=CFG-001 file=setup-jest.ts -->\n"
        "- Property: setupZonelessTestEnv\n"
        "- Reason: Initialize the Jest TestBed environment for Angular unit tests.",
    )

    assert "invalid-config-file" not in codes(run(text))


def test_non_numeric_changes_count_is_rejected(fixtures):
    text = replace_once(valid_text(fixtures), "Changes Applied: 1", "Changes Applied: one")

    assert "invalid-changes-count" in codes(run(text))


def test_traceability_requires_test_and_evidence_in_the_same_row(fixtures):
    text = replace_once(
        valid_text(fixtures),
        "| CHG-001 | T-001 | EV-001 |",
        "| CHG-001 | | |\n| | T-001 | EV-001 |",
    )

    assert "traceability-gap" in codes(run(text))


def test_prerelease_angular_version_is_accepted(fixtures):
    text = valid_text(fixtures).replace("20.3.0", "20.3.0-beta.1")

    assert codes(run(text)) == set()
