from __future__ import annotations

import re
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tasks" / "grok_upload_manifest_all_in.md"
OUT_DIR = ROOT / "tasks" / "grok_upload_zips"
MAX_ZIP_BYTES = 5 * 1024 * 1024


def parse_manifest_paths(manifest_path: Path) -> list[Path]:
    paths: list[Path] = []
    pattern = re.compile(r"^-\s+(.+?)\s*$")
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        candidate = match.group(1)
        if candidate.startswith("#"):
            continue
        file_path = ROOT / candidate
        if file_path.exists() and file_path.is_file():
            paths.append(file_path)
    seen = set()
    unique_paths = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            unique_paths.append(path)
    return unique_paths


def build_zip(zip_path: Path, files: list[Path]) -> int:
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for file_path in files:
            archive.write(file_path, arcname=file_path.relative_to(ROOT).as_posix())
    return zip_path.stat().st_size


def split_into_zips(files: list[Path], out_dir: Path, max_bytes: int) -> list[tuple[Path, int, list[Path]]]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[tuple[Path, int, list[Path]]] = []
    current: list[Path] = []
    idx = 1

    temp_zip = out_dir / "_temp.zip"

    for file_path in files:
        trial = current + [file_path]
        trial_size = build_zip(temp_zip, trial)

        if trial_size <= max_bytes:
            current = trial
            continue

        if current:
            final_zip = out_dir / f"grok_pack_{idx:02d}.zip"
            final_size = build_zip(final_zip, current)
            results.append((final_zip, final_size, current.copy()))
            idx += 1
            current = [file_path]
            trial_size = build_zip(temp_zip, current)

        if trial_size > max_bytes:
            final_zip = out_dir / f"grok_pack_{idx:02d}.zip"
            final_size = build_zip(final_zip, current)
            results.append((final_zip, final_size, current.copy()))
            idx += 1
            current = []

    if current:
        final_zip = out_dir / f"grok_pack_{idx:02d}.zip"
        final_size = build_zip(final_zip, current)
        results.append((final_zip, final_size, current.copy()))

    if temp_zip.exists():
        temp_zip.unlink()

    return results


def write_index(results: list[tuple[Path, int, list[Path]]], out_dir: Path) -> Path:
    index_path = out_dir / "index.txt"
    lines: list[str] = []
    lines.append("Grok Upload Zip Index")
    lines.append("")
    for zip_path, size, files in results:
        lines.append(f"{zip_path.name} | {size} bytes | {len(files)} files")
        for file_path in files:
            lines.append(f"  - {file_path.relative_to(ROOT).as_posix()}")
        lines.append("")
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def main() -> None:
    files = parse_manifest_paths(MANIFEST)
    if not files:
        raise SystemExit("No files found in manifest.")

    results = split_into_zips(files, OUT_DIR, MAX_ZIP_BYTES)
    index_path = write_index(results, OUT_DIR)

    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")
    print(f"Files packed: {len(files)}")
    print(f"Zip archives: {len(results)}")
    for zip_path, size, files_in_zip in results:
        print(f" - {zip_path.relative_to(ROOT)} | {size} bytes | {len(files_in_zip)} files")
    print(f"Index: {index_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
