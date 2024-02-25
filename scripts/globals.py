import json
import os

import modules.scripts as scripts
from modules.shared import opts


global hide_nsfw_networks_key, hide_nsfw, network_descriptions_path


hide_nsfw_networks_key = "sd_lora_tagger_hide_nsfw_extra_networks"
network_descriptions_path = os.path.join(scripts.basedir(), "network_descriptions")

print(f"SD Lora Tagger: network_descriptions_path={network_descriptions_path}")


def update_hide_nsfw(extras=None):
    global hide_nsfw_networks_key, hide_nsfw

    hide_nsfw = getattr(opts, hide_nsfw_networks_key, None)
    if hide_nsfw is None:
        hide_nsfw = False
        print(f"SD Lora Tagger: KeyError on shared.opts.data, defaulting to hide_nsfw={hide_nsfw}")

    if extras is not None:
        extras_dict = json.loads(extras)
        extras_dict["hide_nsfw"] = "true" if hide_nsfw else "false"
        return json.dumps(extras_dict)

    else: return extras


update_hide_nsfw()

