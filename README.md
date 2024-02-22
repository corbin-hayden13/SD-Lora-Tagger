# SD Lora Tagger

This extension allows searching extra netwroks by tag files that can be created and edited for all of your checkpoints and extra networks (not exclusive to just Loras).

### Features
 - __Search by Tags__:  Using the regular checkpoint/embedding/lora/etc. search bar, search for your extra networks using custom tags (the default tags are the extra network file names).
 - __Refresh Tags__:  Using the regular extra network refresh button, register new tags with the webui and search like normal without having to restart your server.
 - __Edit Tag Files Through webui__:  Through the SD Lora Tagger tab, you can search for all of the tag files of your extra networks, edit the tag files, and save the current state of the tags you edit.
 - __Filter NSFW Extra Networks__:  Any extra network that you tag with "nsfw" or "NSFW" can now be hidden from the extra networks tab through an option in settings.
   - The checkbox is in Setting > Uncategorized/SD Lora Tagger > "Hide NSFW-tagged extra networks"
   - After toggling "Hide NSFW-tagged extra networks", click the "Apply settings" button then refresh your extra networks for the option to take effect, no need to restart your server!


This extension is built to work with the major distributions of the `AUTOMATIC1111/stable-diffusion-webui` including the popular `vladmandic/automatic` fork.
 - If the extension is bugged on your specific fork of the `AUTOMATIC1111/stable-diffusion-webui`, please create an issue and I will try to address it as soon as possible


### For Reported Issues
If an issue is reported either through the model page on CivitAI or directly through issues on this repo, the issue will be marked as a "bug" and "unconfirmed" until it can be recreated, at which point it will be marked "confirmed".

If an issue remains "unconfirmed" for more than 48 hours it will be closed just to keep the issues page clean and avoid reported bugs where the issue was the extension was out of date.
