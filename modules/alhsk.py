from func import *  # 导入内置函数
import commands
import requests  # 用于发送 HTTP 请求
import os  # 用于文件操作
from typing import Optional

# 注册命令
_cmds = [
    {
        "cmd": "alhsk_install",
        "alias": ["alhsk-i"],
        "func_name": "alhsk_install_func",
        "help": "从 alhsk API 安装 Mod"
    }
]

commands.registers(get_module_name(__name__), _cmds)

# 获取 Mod 列表
def get_mod_list():
    """
    从 alhsk API 获取 Mod 列表。

    返回值:
        list: Mod 列表，如果请求失败则返回 None。
    """
    api_url = "https://api.alhsk.top/v1/list.mod.json"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"无法获取 Mod 列表: {e}")
        return None

# 下载并安装 Mod
def download_mod(mod_url: str, file_name: str) -> Optional[str]:
    """
    下载 Mod 文件并保存到本地。

    参数:
        mod_url (str): Mod 文件的下载 URL。
        file_name (str): 保存的文件名。

    返回值:
        Optional[str]: 保存的文件路径，如果下载失败则返回 None。
    """
    try:
        mod_response = requests.get(mod_url)
        mod_response.raise_for_status()

        # 确保 mods 目录存在
        mods_dir = "./mods"
        if not os.path.exists(mods_dir):
            os.makedirs(mods_dir)

        # 保存 Mod 文件到 mods 目录
        mod_path = os.path.join(mods_dir, file_name)
        with open(mod_path, "wb") as f:
            f.write(mod_response.content)

        print(f"Mod 已成功下载并保存到 {mod_path}")
        return mod_path
    except requests.exceptions.RequestException as e:
        print(f"下载 Mod 失败: {e}")
        return None

def register_mod_info(mod: dict, mod_path: str):
    """
    将 Mod 或 Plugin 信息注册到管理器中。

    参数:
        mod (dict): Mod/Plugin 信息，包含名称、版本、加载器等。
        mod_path (str): Mod/Plugin 文件的保存路径。
    """
    # 根据加载器类型设置 type 字段
    mod_loader = mod["mod_loader"].lower()
    if mod_loader in ["forge", "fabric", "neoforge"]:
        mod_type = "mod"
    else:
        mod_type = "plugin"

    mod_info = {
        "name": mod["name"],
        "version": mod["version"],
        "loader": mod["mod_loader"],  # 将 mod_loader 改为 loader
        "file": mod_path,  # 保存文件的完整路径
        "type": mod_type  # 动态设置类型
    }

    # 将 Mod/Plugin 信息作为一个软件包添加到配置文件中
    success = add_package_list(mod["name"], mod_info)
    if success:
        print(f"{mod_type.capitalize()} {mod['name']} 已注册到管理器")
    else:
        print(f"{mod_type.capitalize()} {mod['name']} 已存在，未重复注册")


# 主功能函数
def alhsk_install_func(params: list):
    """
    从 alhsk API 安装 Mod 的主功能函数。

    参数:
        params (list): 命令行参数列表。
    """
    # 获取 Mod 列表
    mod_list = get_mod_list()
    if not mod_list:
        return

    # 如果没有传入参数，列出所有 Mod
    if len(params) == 0:
        print("可用 Mod 列表：")
        for mod in mod_list:
            print(f"- {mod['name']} (版本: {mod['version']}, 加载器: {mod['mod_loader']})")
        return

    # 安装指定的 Mod
    mod_name = params[0]
    mod_to_install = None
    for mod in mod_list:
        if mod["name"] == mod_name:
            mod_to_install = mod
            break

    if not mod_to_install:
        print(f"未找到 Mod: {mod_name}")
        return

    # 下载并安装 Mod
    mod_url = f"https://api.alhsk.top{mod_to_install['file']}"
    file_name = mod_url.split("/")[-1]
    print(f"正在下载 Mod: {mod_name}...")
    mod_path = download_mod(mod_url, file_name)

    if mod_path:
        # 注册 Mod 信息到管理器
        register_mod_info(mod_to_install, mod_path)
