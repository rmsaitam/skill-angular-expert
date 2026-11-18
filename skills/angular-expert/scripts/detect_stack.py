from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_STRICT = 1
EXIT_CONFIG = 2
EXIT_PARSE = 3

DESCRIPTORS = ("package.json", "angular.json")
JEST_PACKAGES = {"jest", "ts-jest", "jest-preset-angular"}
CONFIG_KEY_RE = re.compile(r"^([A-Za-z0-9._-]+)\s*[:=]")
NGMODULE_RE = re.compile(r"@NgModule\s*\(")
ZONELESS_RE = re.compile(r"provideZonelessChangeDetection")
SKIP_DIRS = {"node_modules", ".angular", "dist", ".git"}


class ConfigError(Exception):
    pass


class ParseError(Exception):
    pass


def item(code: str, message: str, source: str) -> dict:
    return {"code": code, "message": message, "source": source}


def find_descriptor(root: Path) -> str:
    for name in DESCRIPTORS:
        if (root / name).is_file():
            return name
    raise ConfigError(
        "No package.json or angular.json found. Provide package.json with the exact "
        "Angular dependency versions before continuing."
    )


def normalize_version(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = str(value).strip().strip("'\"").lstrip("^~><= ")
    match = re.match(r"^v?\d+(?:\.\d+)*(?:[.-][0-9A-Za-z.-]+)?$", cleaned)
    return cleaned if match else None


def detect_major(version: str | None) -> int | None:
    match = re.match(r"^(\d+)", (version or "").strip())
    return int(match.group(1)) if match else None


def normalize_config_keys(values: list[str]) -> list[str]:
    return sorted({value.strip() for value in values if value.strip()})


def strip_json_comments(text: str) -> str:
    result: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            result.append(char)
            index += 1
            continue
        if text.startswith("//", index):
            while index < len(text) and text[index] not in "\r\n":
                index += 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            index = len(text) if end < 0 else end + 2
            continue
        result.append(char)
        index += 1
    return "".join(result)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(strip_json_comments(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError) as exc:
        raise ParseError(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ParseError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ParseError(f"Invalid JSON object in {path}")
    return data


def parse_package(path: Path) -> dict:
    if not path.is_file():
        return {"dependencies": {}, "cliVersion": None}
    raw = load_json(path)
    dependencies: dict[str, str] = {}
    for section in ("dependencies", "devDependencies"):
        values = raw.get(section) or {}
        if isinstance(values, dict):
            dependencies.update({str(name): str(version) for name, version in values.items()})
    return {
        "dependencies": dependencies,
        "cliVersion": dependencies.get("@angular/cli"),
    }


def parse_angular_json(path: Path, cli_version: str | None = None) -> dict:
    empty = {
        "builders": [],
        "testBuilders": [],
        "ssr": False,
        "standaloneDefault": False,
        "cliVersion": cli_version,
    }
    if not path.is_file():
        return empty

    raw = load_json(path)
    builders: list[str] = []
    test_builders: list[str] = []
    ssr = False
    projects = raw.get("projects") or {}
    if isinstance(projects, dict):
        for project in projects.values():
            if not isinstance(project, dict):
                continue
            targets = project.get("architect") or project.get("targets") or {}
            if not isinstance(targets, dict):
                continue
            build = targets.get("build") or {}
            test = targets.get("test") or {}
            if isinstance(build, dict):
                if build.get("builder"):
                    builders.append(str(build["builder"]))
                options = build.get("options") or {}
                if isinstance(options, dict):
                    ssr = ssr or bool(options.get("ssr"))
            if isinstance(test, dict) and test.get("builder"):
                test_builders.append(str(test["builder"]))

    schematics = raw.get("schematics") or {}
    component: dict = {}
    if isinstance(schematics, dict):
        candidate = schematics.get("@schematics/angular:component") or {}
        if isinstance(candidate, dict):
            component = candidate

    return {
        "builders": builders,
        "testBuilders": test_builders,
        "ssr": ssr,
        "standaloneDefault": bool(component.get("standalone")),
        "cliVersion": cli_version or dependencies_cli_version(raw),
    }


def dependencies_cli_version(raw: dict) -> str | None:
    for section in ("dependencies", "devDependencies"):
        values = raw.get(section) or {}
        if isinstance(values, dict) and values.get("@angular/cli"):
            return str(values["@angular/cli"])
    return None


def parse_tsconfig(path: Path) -> dict:
    empty = {"strict": False, "baseUrl": None, "paths": []}
    if not path.is_file():
        return empty
    raw = load_json(path)
    options = raw.get("compilerOptions") or {}
    if not isinstance(options, dict):
        options = {}
    paths = options.get("paths") or {}
    path_keys = list(paths.keys()) if isinstance(paths, dict) else []
    return {
        "strict": bool(options.get("strict")),
        "baseUrl": options.get("baseUrl"),
        "paths": normalize_config_keys([str(key) for key in path_keys]),
    }


def detect_test_runner(dependencies: dict[str, str], builders: list[str]) -> str:
    names = set(dependencies)
    joined = " ".join(builders).lower()
    jest = bool(names & JEST_PACKAGES) or "jest" in joined
    karma = "karma" in names or "karma" in joined
    vitest = "vitest" in names or "vitest" in joined
    detected = [
        name
        for name, present in (("jest", jest), ("karma", karma), ("vitest", vitest))
        if present
    ]
    if len(detected) > 1:
        return "mixed"
    return detected[0] if detected else "unknown"


def detect_rendering(major: int | None, standalone_default: bool, has_ngmodule: bool) -> str:
    modern = standalone_default or (major is not None and major >= 19)
    if modern and has_ngmodule:
        return "mixed"
    if has_ngmodule:
        return "ngmodule"
    if modern:
        return "standalone"
    return "unknown"


def detect_change_detection(
    zone_present: bool, zoneless_provider: bool, major: int | None
) -> str:
    if zone_present and zoneless_provider:
        return "mixed"
    if zoneless_provider:
        return "zoneless"
    if zone_present:
        return "zone"
    if major is not None and major >= 20:
        return "zoneless"
    return "unknown"


def source_files(root: Path, pattern: str) -> list[Path]:
    return [
        path
        for path in root.rglob(pattern)
        if path.is_file() and not SKIP_DIRS.intersection(path.parts)
    ]


def scan_sources(root: Path) -> tuple[bool, bool]:
    has_ngmodule = False
    has_zoneless = False
    for path in source_files(root, "*.ts"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        has_ngmodule = has_ngmodule or bool(NGMODULE_RE.search(text))
        has_zoneless = has_zoneless or bool(ZONELESS_RE.search(text))
        if has_ngmodule and has_zoneless:
            break
    return has_ngmodule, has_zoneless


def scan_config_keys(root: Path) -> list[str]:
    paths: set[Path] = set()
    for pattern in ("environment*.ts", "*.config.ts", "angular.json"):
        paths.update(source_files(root, pattern))

    keys: set[str] = set()
    for path in sorted(paths):
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip().lstrip("\"'")
            if not stripped or stripped.startswith(("//", "/*", "*")):
                continue
            match = CONFIG_KEY_RE.match(stripped)
            if match:
                keys.add(match.group(1))
    return sorted(keys)


def detect_stack(root: Path) -> dict:
    root = Path(root).resolve()
    descriptor = find_descriptor(root)
    warnings: list[dict] = []
    blockers: list[dict] = []

    package = parse_package(root / "package.json")
    angular = parse_angular_json(root / "angular.json", package["cliVersion"])
    tsconfig = parse_tsconfig(root / "tsconfig.json")
    nx_path = root / "nx.json"
    if nx_path.is_file():
        load_json(nx_path)
    build_tool = "nx" if nx_path.is_file() else "npm"

    dependencies = package["dependencies"]
    raw_angular = dependencies.get("@angular/core")
    angular_version = normalize_version(raw_angular)
    angular_major = detect_major(angular_version)
    ts_version = normalize_version(dependencies.get("typescript"))
    rxjs_version = normalize_version(dependencies.get("rxjs"))
    zone_present = "zone.js" in dependencies

    builders = angular["builders"] + angular["testBuilders"]
    test_runner = detect_test_runner(dependencies, builders)
    has_ngmodule, zoneless_provider = scan_sources(root)
    rendering = detect_rendering(angular_major, angular["standaloneDefault"], has_ngmodule)
    change_detection = detect_change_detection(zone_present, zoneless_provider, angular_major)

    if not raw_angular:
        blockers.append(
            item(
                "missing-angular-version",
                "Angular version not found in package.json dependencies.",
                descriptor,
            )
        )
    elif angular_version is None or angular_major is None:
        blockers.append(
            item(
                "unknown-angular-version",
                "Angular version in package.json could not be parsed.",
                "package.json",
            )
        )
    elif angular_major < 20:
        warnings.append(
            item(
                "unsupported-angular-version",
                f"Angular {angular_major} is outside active support; record the constraint.",
                "package.json",
            )
        )

    if not ts_version:
        warnings.append(
            item(
                "missing-typescript-version",
                "TypeScript version not found in package.json dependencies.",
                "package.json",
            )
        )
    if test_runner == "unknown":
        warnings.append(
            item(
                "unknown-test-runner",
                "No supported test runner found in dependencies or angular.json.",
                "package.json",
            )
        )
    elif test_runner == "mixed":
        warnings.append(
            item(
                "mixed-test-runners",
                "Multiple test runners detected; select a single test runner.",
                "angular.json" if (root / "angular.json").is_file() else "package.json",
            )
        )
    if rendering == "mixed":
        warnings.append(
            item(
                "mixed-rendering",
                "Both standalone and NgModule indicators are present.",
                "angular.json",
            )
        )
    elif rendering == "unknown":
        warnings.append(
            item(
                "unknown-rendering",
                "No positive standalone evidence or NgModule source was found.",
                "src",
            )
        )
    if change_detection == "mixed":
        warnings.append(
            item(
                "mixed-change-detection",
                "zone.js and provideZonelessChangeDetection are both present.",
                "src",
            )
        )
    elif change_detection == "unknown":
        warnings.append(
            item(
                "unknown-change-detection",
                "Zoneless support is unavailable for this Angular major and zone.js is absent.",
                "package.json",
            )
        )

    capabilities = {
        "jest": test_runner == "jest",
        "testbed": angular_version is not None and test_runner in {"jest", "karma", "vitest"},
        "signals": angular_major is not None and angular_major >= 16,
        "ssr": angular["ssr"],
        "zoneless": zoneless_provider or (not zone_present and angular_major is not None and angular_major >= 20),
        "material": "@angular/material" in dependencies,
    }

    return {
        "projectRoot": str(root),
        "buildTool": build_tool,
        "descriptor": descriptor,
        "angular": {"version": angular_version, "major": angular_major},
        "typescript": {"version": ts_version},
        "rxjs": {"version": rxjs_version},
        "rendering": rendering,
        "changeDetection": change_detection,
        "testRunner": test_runner,
        "strict": tsconfig["strict"],
        "capabilities": capabilities,
        "configKeys": scan_config_keys(root),
        "warnings": warnings,
        "blockers": blockers,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="detect_stack.py",
        description="Detect Angular versions, rendering mode and capabilities from a project build.",
    )
    parser.add_argument("root", nargs="?", default=".", help="Project root directory.")
    parser.add_argument("--output", help="Write the JSON result to this path.")
    parser.add_argument("--json", action="store_true", help="Print the JSON result to stdout.")
    parser.add_argument("--strict", action="store_true", help="Fail when warnings are present.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = detect_stack(Path(args.root))
    except ConfigError as exc:
        print(f"[ERROR] config: {exc}", file=sys.stderr)
        return EXIT_CONFIG
    except ParseError as exc:
        print(f"[ERROR] parse: {exc}", file=sys.stderr)
        return EXIT_PARSE

    payload = json.dumps(data, indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(payload)

    if data["blockers"]:
        return EXIT_CONFIG
    if args.strict and data["warnings"]:
        return EXIT_STRICT
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
