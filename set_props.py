# quick script
import yaml, json
from pathlib import Path

models_yaml = Path("models/models.yaml")
out = Path("webui/public/props")

with open(models_yaml) as f:
    data = yaml.safe_load(f)

models = data["models"]
props = {
    "app_name": "WarriorGPT",
    "default_model": list(models.keys())[0],
    "models": [
        {
            "name": name,
            "display_name": cfg.get("display_name", name),
            "type": cfg.get("type", "openai"),
        }
        for name, cfg in models.items()
    ],
}
out.write_text(json.dumps(props, indent=2))
