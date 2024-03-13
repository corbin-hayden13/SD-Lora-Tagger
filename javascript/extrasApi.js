function updateContainer(displayText, textarea) {
    var value = displayText == "block" ? "1" : "0";
    
    textarea.value = value;
    textarea.dispatchEvent(new Event("input"));
    return;
  }
  
  function internalSetup(id_prompt) {
    var extras = gradioApp().querySelector("#sd_lora_tagger_extras");
    var textarea = gradioApp().querySelector(
      "#sd_lora_tagger_container textarea"
    );
  
    if (extras) {
      extras.addEventListener("click", () => {
        updateContainer(extras.lastChild.style.display, textarea);
      });
    }
  }
  
  onUiLoaded(() => {
    internalSetup("sd_lora_tagger_extras");
  });
  