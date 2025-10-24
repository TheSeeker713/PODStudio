"""
Mock data for testing the pack builder and other core functions.
This simulates database calls until the actual models are implemented.
"""


def get_pack_details_mock(pack_id: int) -> dict:
    """
    Returns mock details for a pack.
    """
    return {
        "id": pack_id,
        "title": "My Awesome Asset Pack",
        "slug": "my-awesome-asset-pack",
        "author": "AI Assistant",
        "description": "A collection of stunning, procedurally generated assets.",
        "version": "1.0.0",
        "assets": [
            {"path": "/assets/images/image1.png"},
            {"path": "/assets/audio/sound1.wav"},
            {"path": "/assets/models/model1.glb"},
        ],
    }


def get_prompt_session_mock(session_id: str) -> dict:
    """
    Returns mock data for a prompt generation session.
    """
    return {
        "id": session_id,
        "source": "agent-assisted",
        "final_prompts": {
            "image1.png": "A beautiful landscape painting, digital art, 4k",
            "sound1.wav": "The sound of a gentle breeze through a forest",
            "model1.glb": "A 3D model of a futuristic sci-fi crate",
        },
        "agent_lineage": [
            {
                "agent_type": "vision",
                "model": "llava-v1.6-34b.Q5_K_M.gguf",
                "prompt": "Analyze this moodboard.",
                "response": "The mood is serene and futuristic.",
            },
            {
                "agent_type": "logic",
                "model": "dolphin-2.9-llama3-8b-256k.Q5_K_M.gguf",
                "prompt": "Generate asset ideas based on 'serene and futuristic'.",
                "response": "Ideas: landscape painting, gentle breeze sound, sci-fi crate model.",
            },
        ],
    }
