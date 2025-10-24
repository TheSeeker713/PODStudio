import json
import shutil
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

# TODO: Replace with actual database models when available
from app.core.models_mock import get_pack_details_mock, get_prompt_session_mock


def build_pack(
    pack_id: int,
    prompt_session_id: str | None = None,
    include_disclosure: bool = False,
) -> str:
    """
    Build a pack, export to ZIP, and embed prompt generation artifacts.

    The pipeline is as follows:
    1. Create a temporary directory for staging the pack contents.
    2. Fetch pack and asset details from the database (mocked for now).
    3. Generate metadata files (manifest.json, README.md, etc.).
    4. Copy all associated asset files into the staging directory.
    5. If a prompt_session_id is provided:
        a. Fetch prompt and lineage data (mocked for now).
        b. Create a /prompts subdirectory.
        c. Write final_prompts.json and agent_lineage.json.
        d. If include_disclosure is True, append AI generation notes.
    6. Create a ZIP archive from the staged contents.
    7. Clean up the temporary directory.
    8. Return the path to the final ZIP file.

    Args:
        pack_id: Database ID of the pack to export.
        prompt_session_id: Optional ID for the prompt generation session.
        include_disclosure: Optional flag to add AI assistance notes.

    Returns:
        Path to the exported ZIP file.
    """
    pack_data = get_pack_details_mock(pack_id)
    if not pack_data:
        raise ValueError(f"Pack with ID {pack_id} not found.")

    temp_dir = Path(tempfile.mkdtemp(prefix="pod_pack_"))

    try:
        # --- 2. Generate manifest.json ---
        manifest = {
            "pack_id": pack_data["id"],
            "title": pack_data["title"],
            "author": pack_data["author"],
            "description": pack_data["description"],
            "version": pack_data["version"],
            "export_date": datetime.now(UTC).isoformat(),
            "files": [],
            "prompt_session_id": prompt_session_id,
            "prompt_source": None,
        }

        # --- 3. Copy assets and update manifest ---
        for asset in pack_data["assets"]:
            # In a real scenario, we'd copy from a source location
            # Here, we'll just create dummy files for structure
            asset_filename = Path(asset["path"]).name
            dummy_asset_path = temp_dir / asset_filename
            dummy_asset_path.write_text(f"This is a placeholder for {asset['path']}.")

            manifest["files"].append(
                {
                    "path": asset_filename,
                    "checksum": "TODO_implement_checksum",  # TODO: Implement checksum
                }
            )

        # --- 4. Handle Prompts and Disclosures ---
        readme_content = f"# {pack_data['title']}\n\n{pack_data['description']}"
        store_copy_content = f"**{pack_data['title']}** by {pack_data['author']}\n\n{pack_data['description']}"

        if prompt_session_id:
            prompt_data = get_prompt_session_mock(prompt_session_id)
            manifest["prompt_source"] = prompt_data["source"]

            prompts_dir = temp_dir / "prompts"
            prompts_dir.mkdir()

            # Write final prompts
            (prompts_dir / "final_prompts.json").write_text(json.dumps(prompt_data["final_prompts"], indent=2))

            # Write agent lineage
            (prompts_dir / "agent_lineage.json").write_text(json.dumps(prompt_data["agent_lineage"], indent=2))

            if include_disclosure:
                ai_note = "\n\n*This pack contains content generated with offline AI assistance.*"
                readme_content += ai_note

                model_disclosure = "\n\n---\n**AI Model Disclosure**\n"
                for agent in prompt_data["agent_lineage"]:
                    model_disclosure += f"- **{agent['agent_type']}**: `{agent['model']}`\n"
                store_copy_content += model_disclosure

        # --- Write metadata files ---
        (temp_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        (temp_dir / "README.md").write_text(readme_content)
        (temp_dir / "store_copy.txt").write_text(store_copy_content)
        (temp_dir / "LICENSE.txt").write_text("TODO: Add actual license text.")

        # --- 5. Create ZIP ---
        pack_filename = f"{pack_data['slug']}_v{pack_data['version']}.zip"

        # Ensure 'Packs' directory exists
        packs_dir = Path.cwd() / "Packs"
        packs_dir.mkdir(exist_ok=True)

        zip_path = packs_dir / pack_filename

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_dir.rglob("*"):
                archive_path = file_path.relative_to(temp_dir)
                zipf.write(file_path, archive_path)

        return str(zip_path)

    finally:
        # --- 6. Clean up temp folder ---
        shutil.rmtree(temp_dir)
