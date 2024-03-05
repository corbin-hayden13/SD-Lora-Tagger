import launch

if not launch.is_installed("ischedule"):
    launch.run_pip("install ischedule==1.2.6", "requirements for SD Lora Tagger")