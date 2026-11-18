import json
import shutil

import pytest

import detect_stack as ds


def make_project(tmp_path, *, package=None, angular_json=None, tsconfig=None, environment=None, nx=None):
    project = tmp_path / "project"
    project.mkdir()
    if package:
        shutil.copy(package, project / "package.json")
    if angular_json:
        shutil.copy(angular_json, project / "angular.json")
    if tsconfig:
        shutil.copy(tsconfig, project / "tsconfig.json")
    if environment:
        shutil.copy(environment, project / "environment.ts")
    if nx:
        shutil.copy(nx, project / "nx.json")
    return project


def test_detects_angular20_npm_stack(fixtures, tmp_path):
    project = make_project(
        tmp_path,
        package=fixtures / "package-angular20.json",
        angular_json=fixtures / "angular.json",
        tsconfig=fixtures / "tsconfig.json",
        environment=fixtures / "environment.ts",
    )

    data = ds.detect_stack(project)

    assert data["buildTool"] == "npm"
    assert data["descriptor"] == "package.json"
    assert data["angular"] == {"version": "20.3.0", "major": 20}
    assert data["typescript"] == {"version": "5.8.2"}
    assert data["rxjs"] == {"version": "7.8.2"}
    assert data["rendering"] == "standalone"
    assert data["changeDetection"] == "zoneless"
    assert data["testRunner"] == "jest"
    assert data["strict"] is True
    assert data["capabilities"]["jest"] is True
    assert data["capabilities"]["testbed"] is True
    assert data["capabilities"]["signals"] is True
    assert data["capabilities"]["ssr"] is True
    assert data["capabilities"]["zoneless"] is True
    assert data["capabilities"]["material"] is True
    assert data["warnings"] == []
    assert data["blockers"] == []


def test_detects_angular15_ngmodule_stack(fixtures, tmp_path):
    project = make_project(tmp_path, package=fixtures / "package-angular15.json")
    source = project / "src" / "app"
    source.mkdir(parents=True)
    (source / "app.module.ts").write_text(
        "import { NgModule } from '@angular/core';\n"
        "@NgModule({ declarations: [] })\n"
        "export class AppModule {}\n",
        encoding="utf-8",
    )

    data = ds.detect_stack(project)

    assert data["angular"] == {"version": "15.2.10", "major": 15}
    assert data["typescript"] == {"version": "4.9.5"}
    assert data["rxjs"] == {"version": "7.8.1"}
    assert data["rendering"] == "ngmodule"
    assert data["changeDetection"] == "zone"
    assert data["testRunner"] == "karma"
    assert data["strict"] is False
    assert data["capabilities"]["jest"] is False
    assert data["capabilities"]["zoneless"] is False
    assert any(w["code"] == "unsupported-angular-version" for w in data["warnings"])
    assert data["blockers"] == []


def test_config_keys_are_collected_without_values(fixtures, tmp_path):
    project = make_project(
        tmp_path,
        package=fixtures / "package-angular20.json",
        angular_json=fixtures / "angular.json",
        environment=fixtures / "environment.ts",
    )

    data = ds.detect_stack(project)
    payload = json.dumps(data)

    assert "apiBaseUrl" in data["configKeys"]
    assert "apiToken" in data["configKeys"]
    assert "super-secret-value" not in payload
    assert data["configKeys"] == sorted(set(data["configKeys"]))


def test_missing_descriptor_raises_config_error(tmp_path):
    with pytest.raises(ds.ConfigError):
        ds.detect_stack(tmp_path)


def test_malformed_package_json_raises_parse_error(tmp_path):
    project = make_project(tmp_path)
    (project / "package.json").write_text("{ not json", encoding="utf-8")

    with pytest.raises(ds.ParseError):
        ds.detect_stack(project)


def test_missing_versions_are_blockers(tmp_path):
    project = make_project(tmp_path)
    (project / "package.json").write_text(json.dumps({"name": "empty"}), encoding="utf-8")

    data = ds.detect_stack(project)

    assert any(b["code"] == "missing-angular-version" for b in data["blockers"])
    assert any(w["code"] == "missing-typescript-version" for w in data["warnings"])

    (project / "package.json").write_text(
        json.dumps({"dependencies": {"@angular/core": "not-a-version"}}), encoding="utf-8"
    )
    data = ds.detect_stack(project)
    assert any(b["code"] == "unknown-angular-version" for b in data["blockers"])


def test_mixed_test_runners_become_warning(tmp_path):
    project = make_project(tmp_path)
    (project / "package.json").write_text(
        json.dumps(
            {
                "dependencies": {"@angular/core": "20.3.0"},
                "devDependencies": {"jest": "29.7.0", "typescript": "5.8.2"},
            }
        ),
        encoding="utf-8",
    )
    (project / "angular.json").write_text(
        json.dumps(
            {
                "version": 1,
                "projects": {
                    "demo": {"architect": {"test": {"builder": "@angular-devkit/build-angular:karma"}}}
                },
            }
        ),
        encoding="utf-8",
    )

    data = ds.detect_stack(project)

    assert data["testRunner"] == "mixed"
    assert any(w["code"] == "mixed-test-runners" for w in data["warnings"])
    assert data["blockers"] == []


def test_detect_major_for_supported_and_unknown_versions():
    assert ds.detect_major("20.3.0") == 20
    assert ds.detect_major("15.2.10") == 15
    assert ds.detect_major("not-a-version") is None
    assert ds.detect_major(None) is None
    assert ds.normalize_version("^20.3.0") == "20.3.0"


def test_detect_rendering_distinguishes_ngmodule_and_standalone():
    assert ds.detect_rendering(20, False, False) == "standalone"
    assert ds.detect_rendering(15, False, True) == "ngmodule"
    assert ds.detect_rendering(15, False, False) == "unknown"
    assert ds.detect_rendering(20, False, True) == "mixed"
    assert ds.detect_rendering(15, True, True) == "mixed"


def test_detect_change_detection_distinguishes_zone_and_zoneless():
    assert ds.detect_change_detection(False, False, 20) == "zoneless"
    assert ds.detect_change_detection(True, False, 15) == "zone"
    assert ds.detect_change_detection(False, True, 20) == "zoneless"
    assert ds.detect_change_detection(True, True, 20) == "mixed"
    assert ds.detect_change_detection(False, False, 15) == "unknown"


def test_legacy_without_zone_js_is_not_reported_as_zoneless(fixtures, tmp_path):
    package = json.loads((fixtures / "package-angular15.json").read_text(encoding="utf-8"))
    package["dependencies"].pop("zone.js", None)
    project = make_project(tmp_path)
    (project / "package.json").write_text(json.dumps(package), encoding="utf-8")

    data = ds.detect_stack(project)

    assert data["changeDetection"] == "unknown"
    assert data["rendering"] == "unknown"
    assert data["capabilities"]["zoneless"] is False
    assert any(w["code"] == "unknown-change-detection" for w in data["warnings"])
    assert any(w["code"] == "unknown-rendering" for w in data["warnings"])


def test_normalize_config_keys_deduplicates_and_sorts():
    result = ds.normalize_config_keys(["apiToken", "apiBaseUrl", "apiToken", " zone ", ""])

    assert result == ["apiBaseUrl", "apiToken", "zone"]


def test_cli_writes_stack_json(fixtures, tmp_path):
    project = make_project(tmp_path, package=fixtures / "package-angular20.json")
    output = tmp_path / "reports" / "stack.json"

    code = ds.main([str(project), "--output", str(output)])

    assert code == ds.EXIT_OK
    text = output.read_text(encoding="utf-8")
    assert text.endswith("\n")
    payload = json.loads(text)
    assert payload["angular"]["version"] == "20.3.0"


def test_cli_returns_config_code_for_missing_descriptor(tmp_path, capsys):
    code = ds.main([str(tmp_path)])

    assert code == ds.EXIT_CONFIG
    assert "[ERROR] config:" in capsys.readouterr().err


def test_cli_returns_parse_code_for_invalid_package(tmp_path, capsys):
    project = make_project(tmp_path)
    (project / "package.json").write_text("{", encoding="utf-8")

    code = ds.main([str(project)])

    assert code == ds.EXIT_PARSE
    assert "[ERROR] parse:" in capsys.readouterr().err


def test_cli_strict_mode_fails_on_warnings(fixtures, tmp_path):
    project = make_project(tmp_path, package=fixtures / "package-angular15.json")

    assert ds.main([str(project), "--strict"]) == ds.EXIT_STRICT
