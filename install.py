import launch


def install_req(check_name, install_name=None):
    if not install_name: install_name = check_name
    if not launch.is_installed(f"{check_name}"):
        launch.run_pip(f"install {install_name}", "requirements for CivitAI Browser")


install_req("fake_useragent")

