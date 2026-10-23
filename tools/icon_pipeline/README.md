# Icon pipeline (dev only)

V scripts that regenerate trait icons with a local ComfyUI. Moved out of `gfx/` so the game doesn't see them; the `.dds` icons the game loads stay in `gfx/interface/icons/traits/`.

- Run the `.v` files from inside their step folder (`distinct_generation`, `ancestor_generation`, `paragon_generation`). Paths are resolved from the mod root three levels up (`tools/icon_pipeline/<step>`).
- **Set your ComfyUI path before use:** `distinct_generation/generation_setup.json` (`comfyui_directory`) and `iconkit/finish.v` (`default_model`, the u2net.onnx location) hold `SET_ME` placeholders.
- `paragon_generation/deploy_active_mod.v` and its README still mention the original author's Windows paths; edit before use.
- Step folders expect their working folders (`inputs/`, `generated/`, `results/`), which are not in the repo.
