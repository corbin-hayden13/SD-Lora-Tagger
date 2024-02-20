import json

import modules.shared as shared


global hide_nsfw_networks_key, hide_nsfw


hide_nsfw_networks_key = "sd_lora_tagger_hide_nsfw_extra_networks"


def update_hide_nsfw(extras=None):
    global hide_nsfw_networks_key, hide_nsfw

    try:
        hide_nsfw = shared.opts.data[hide_nsfw_networks_key]
        print(f"SD Lora Tagger: shared.opts.data={shared.opts.data[hide_nsfw_networks_key]}")
    except KeyError:
        hide_nsfw = False
        print(f"SD Lora Tagger: KeyError on shared.opts.data, shared.opts.data={shared.opts.data}")

    if extras is not None:
        extras_dict = json.loads(extras)
        extras_dict["hide_nsfw"] = "true" if hide_nsfw else "false"
        return json.dumps(extras_dict)

    else: return extras


update_hide_nsfw()

