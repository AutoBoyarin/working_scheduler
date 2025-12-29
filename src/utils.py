from __future__ import annotations

import os
import time
from typing import Iterable, List

import requests


def download_files(urls: Iterable[str], target_dir: str, retries: int = 2, timeout: int = 15) -> List[str]:
    os.makedirs(target_dir, exist_ok=True)
    local_paths: List[str] = []
    session = requests.Session()
    for url in urls:
        filename = os.path.basename(url.split("?")[0]) or "file"
        local_path = os.path.join(target_dir, filename)

        attempt = 0
        while True:
            try:
                with session.get(url, stream=True, timeout=timeout) as resp:
                    resp.raise_for_status()
                    with open(local_path, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                local_paths.append(local_path)
                break
            except Exception:
                attempt += 1
                if attempt > retries:
                    # пропускаем нескачанные файлы
                    break
                time.sleep(1.0 * attempt)
    return local_paths


__all__ = ["download_files"]
