from __future__ import annotations

import shutil
from pathlib import Path
from typing import BinaryIO
from typing import Iterable

from django.conf import settings


# ---------------------------------------------------------
# DEFAULT ROOT
# ---------------------------------------------------------
DEFAULT_STORAGE_ROOT = (
    Path(settings.BASE_DIR)
    / "storage"
)


# ---------------------------------------------------------
# LOCAL STORAGE
# ---------------------------------------------------------
class LocalStorage:
    """
    Local filesystem storage adapter.
    """

    def __init__(
        self,
        root: str | Path | None = None,
    ) -> None:
        self.root = Path(
            root or DEFAULT_STORAGE_ROOT
        )

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    # -----------------------------------------------------
    # PATH
    # -----------------------------------------------------
    def resolve(
        self,
        path: str,
    ) -> Path:
        safe_path = (
            path.strip("/")
        )

        full = (
            self.root
            / safe_path
        ).resolve()

        if not str(full).startswith(
            str(
                self.root.resolve()
            )
        ):
            raise ValueError(
                "invalid storage path"
            )

        return full

    # -----------------------------------------------------
    # EXISTS
    # -----------------------------------------------------
    def exists(
        self,
        path: str,
    ) -> bool:
        return self.resolve(
            path
        ).exists()

    # -----------------------------------------------------
    # MKDIR
    # -----------------------------------------------------
    def mkdir(
        self,
        path: str,
    ) -> Path:
        folder = self.resolve(
            path
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    # -----------------------------------------------------
    # WRITE BYTES
    # -----------------------------------------------------
    def save(
        self,
        path: str,
        content: bytes,
    ) -> Path:
        target = self.resolve(
            path
        )

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            target,
            "wb",
        ) as handle:
            handle.write(
                content
            )

        return target

    # -----------------------------------------------------
    # WRITE TEXT
    # -----------------------------------------------------
    def save_text(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
    ) -> Path:
        return self.save(
            path=path,
            content=content.encode(
                encoding
            ),
        )

    # -----------------------------------------------------
    # DJANGO FILE
    # -----------------------------------------------------
    def save_file(
        self,
        path: str,
        file: BinaryIO,
    ) -> Path:
        target = self.resolve(
            path
        )

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            target,
            "wb",
        ) as handle:
            shutil.copyfileobj(
                file,
                handle,
            )

        return target

    # -----------------------------------------------------
    # READ BYTES
    # -----------------------------------------------------
    def read(
        self,
        path: str,
    ) -> bytes:
        target = self.resolve(
            path
        )

        with open(
            target,
            "rb",
        ) as handle:
            return handle.read()

    # -----------------------------------------------------
    # READ TEXT
    # -----------------------------------------------------
    def read_text(
        self,
        path: str,
        encoding: str = "utf-8",
    ) -> str:
        return self.read(
            path
        ).decode(
            encoding
        )

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------
    def delete(
        self,
        path: str,
    ) -> bool:
        target = self.resolve(
            path
        )

        if not target.exists():
            return False

        if target.is_dir():
            shutil.rmtree(
                target
            )
        else:
            target.unlink()

        return True

    # -----------------------------------------------------
    # COPY
    # -----------------------------------------------------
    def copy(
        self,
        source: str,
        destination: str,
    ) -> Path:
        src = self.resolve(
            source
        )

        dst = self.resolve(
            destination
        )

        dst.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            src,
            dst,
        )

        return dst

    # -----------------------------------------------------
    # MOVE
    # -----------------------------------------------------
    def move(
        self,
        source: str,
        destination: str,
    ) -> Path:
        src = self.resolve(
            source
        )

        dst = self.resolve(
            destination
        )

        dst.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(src),
            str(dst),
        )

        return dst

    # -----------------------------------------------------
    # SIZE
    # -----------------------------------------------------
    def size(
        self,
        path: str,
    ) -> int:
        return (
            self.resolve(
                path
            )
            .stat()
            .st_size
        )

    # -----------------------------------------------------
    # URL
    # -----------------------------------------------------
    def url(
        self,
        path: str,
    ) -> str:
        clean = (
            path.strip("/")
        )

        return (
            f"/storage/"
            f"{clean}"
        )

    # -----------------------------------------------------
    # LIST
    # -----------------------------------------------------
    def list(
        self,
        path: str = "",
        recursive: bool = True,
    ) -> Iterable[str]:
        folder = self.resolve(
            path
        )

        if not folder.exists():
            return []

        pattern = (
            "**/*"
            if recursive
            else "*"
        )

        files: list[str] = []

        for item in folder.glob(
            pattern
        ):
            if item.is_file():
                files.append(
                    str(
                        item.relative_to(
                            self.root
                        )
                    )
                )

        return files

    # -----------------------------------------------------
    # INFO
    # -----------------------------------------------------
    def info(
        self,
        path: str,
    ) -> dict:
        target = self.resolve(
            path
        )

        return {
            "path": path,
            "exists": (
                target.exists()
            ),
            "is_file": (
                target.is_file()
            ),
            "is_dir": (
                target.is_dir()
            ),
            "size": (
                target.stat().st_size
                if target.exists()
                else 0
            ),
            "url": self.url(
                path
            ),
        }