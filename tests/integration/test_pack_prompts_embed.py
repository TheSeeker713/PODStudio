import json
import zipfile
from pathlib import Path

import pytest

from app.core.packer import build_pack


@pytest.fixture
def cleanup_pack():
    """A pytest fixture to clean up the created pack file after the test."""
    pack_path = None

    def set_path(path):
        nonlocal pack_path
        pack_path = Path(path)

    yield set_path

    if pack_path and pack_path.exists():
        pack_path.unlink()


def test_pack_creation_without_prompts(cleanup_pack):
    """
    Tests that a pack can be created successfully without any prompt data.
    """
    pack_id = 1
    pack_path = build_pack(pack_id)
    cleanup_pack(pack_path)

    assert Path(pack_path).exists()

    with zipfile.ZipFile(pack_path, "r") as zipf:
        assert "manifest.json" in zipf.namelist()
        assert "README.md" in zipf.namelist()
        assert "prompts/" not in [name for name in zipf.namelist() if name.endswith("/")]


def test_pack_creation_with_prompts_no_disclosure(cleanup_pack):
    """
    Tests that prompt artifacts are correctly embedded when a session ID is provided,
    but without the public disclosure note.
    """
    pack_id = 1
    prompt_session_id = "test_session_123"
    pack_path = build_pack(pack_id, prompt_session_id=prompt_session_id, include_disclosure=False)
    cleanup_pack(pack_path)

    assert Path(pack_path).exists()

    with zipfile.ZipFile(pack_path, "r") as zipf:
        # Check for prompt files
        assert "prompts/final_prompts.json" in zipf.namelist()
        assert "prompts/agent_lineage.json" in zipf.namelist()

        # Check manifest content
        with zipf.open("manifest.json") as f:
            manifest = json.load(f)
            assert manifest["prompt_session_id"] == prompt_session_id
            assert manifest["prompt_source"] == "agent-assisted"

        # Check README content for absence of disclosure
        with zipf.open("README.md") as f:
            readme_content = f.read().decode("utf-8")
            assert "generated with offline AI assistance" not in readme_content.lower()


def test_pack_creation_with_prompts_and_disclosure(cleanup_pack):
    """
    Tests that prompt artifacts are embedded and the public disclosure notes
    are added to README.md and store_copy.txt.
    """
    pack_id = 1
    prompt_session_id = "test_session_123"
    pack_path = build_pack(pack_id, prompt_session_id=prompt_session_id, include_disclosure=True)
    cleanup_pack(pack_path)

    assert Path(pack_path).exists()

    with zipfile.ZipFile(pack_path, "r") as zipf:
        # Check for prompt files
        assert "prompts/final_prompts.json" in zipf.namelist()
        assert "prompts/agent_lineage.json" in zipf.namelist()

        # Check README for disclosure
        with zipf.open("README.md") as f:
            readme_content = f.read().decode("utf-8")
            assert "This pack contains content generated with offline AI assistance." in readme_content

        # Check store_copy.txt for disclosure
        with zipf.open("store_copy.txt") as f:
            store_copy_content = f.read().decode("utf-8")
            assert "**AI Model Disclosure**" in store_copy_content
            assert "llava-v1.6-34b.Q5_K_M.gguf" in store_copy_content
            assert "dolphin-2.9-llama3-8b-256k.Q5_K_M.gguf" in store_copy_content
