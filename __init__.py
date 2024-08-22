import gradio as gr

from plugins.t2i.sanp_plugin_casrand.utils import (
    cas_rand_default_component,
    generate,
    list_to_text,
    modify_plugin_env,
    return_method,
)
from utils.env import env
from utils.utils import read_json


def plugin():
    with gr.Tab("CasRand"):
        with gr.Tab("Prompt 设置"):

            cas_rand_components_list = []

            try:
                cas_rand_default_config_file_path = env.cas_rand_default_config
            except Exception:
                cas_rand_default_config_file_path = (
                    "./plugins/t2i/sanp_plugin_casrand/default.json"
                )

            cas_rand_default_config = read_json(cas_rand_default_config_file_path)

            for prompt in cas_rand_default_config["prompt_config"]["prompts"]:
                cas_rand_components_list.append(
                    cas_rand_default_component(
                        prompt["comment"],
                        list_to_text(
                            prompt["strs"],
                        ),
                        return_method(
                            prompt["selectionMethod"],
                            prompt["shuffled"],
                        ),
                        prompt["prob"],
                        prompt["num"],
                        prompt["enabled"],
                    )
                )

            try:
                casrand_component_num = env.casrand_component_num
            except Exception:
                casrand_component_num = 0

            for component in range(int(casrand_component_num)):
                cas_rand_components_list.append(
                    cas_rand_default_component(
                        "新配置", "", "单个 - 随机选择", "0.5", "5", True
                    )
                )

            new_components_list = []
            for components in cas_rand_components_list:
                for component in components:
                    new_components_list.append(component)

        with gr.Tab("图片生成"):
            with gr.Row():
                generate_button = gr.Button("无限生成")
                stop_button = gr.Button("停止生成")
            image = gr.Image()
            cancel_event = image.change(
                fn=generate,
                inputs=new_components_list,
                outputs=image,
                show_progress="hidden",
            )
            generate_button.click(generate, inputs=new_components_list, outputs=image)
            stop_button.click(None, None, None, cancels=[cancel_event])

        with gr.Tab("插件配置"):
            with gr.Row():
                casrand_save_button = gr.Button("保存")
            casrand_otp_info = gr.Textbox(label="输出信息")
            casrand_num = gr.Slider(
                0, 10, casrand_component_num, step=1, label="新配置添加数量"
            )
            casrand_config_file = gr.Textbox(
                cas_rand_default_config_file_path, label="配置文件路径"
            )
            casrand_save_button.click(
                modify_plugin_env,
                inputs=[casrand_num, casrand_config_file],
                outputs=casrand_otp_info,
            )

        with gr.Tab("插件说明"):
            gr.Markdown(
                "### 本插件是对 Nai_CasRand 文生图功能(即 Nai_CasRand 中的 Prompt 设置)的迁移, 使用了与 Nai_CasRand 一致的 Prompts 组装方式, 实现了不通过修改代码即可自定义随机组装更加个性化的 Prompts *①"
            )
            gr.Markdown("<hr>")
            gr.Markdown(
                "### 插件的生成参数使用项目本体中配置的参数(分辨率, 提示词相关性, 采样器, 噪声计划表, 采样步数, 随机种子以及 sm 和 sm_dyn 等), 负面提示词将选择 favorite.json - negative_prompt - belief 中已填写的内容 *②"
            )
            gr.Markdown("<hr>")
            gr.Markdown(
                "### 支持 Nai_CasRand 配置文件(Nai_CasRand 参数设置界面导出设置到文件)的导入, 实现两者快速切换 *③"
            )
            gr.Markdown("<hr>")
            gr.Markdown(
                '① 在 Nai_CasRand 选取方法选项的下含有的选项"打乱次序"以及"随机括号数量"目前未添加; 由于 Gradio 的局限, 新配置的添加目前通过修改 .env 配置来实现, 后续会尝试加入动态添加'
            )
            gr.Markdown(
                "② 随插件附带的配置文件为 Nai_CasRand 默认的内容, 但仅包含本插件所需的最小内容, 后续会支持配置文件导出; favorite.json 及其相关内容即将重构, 届时请及时更新本插件"
            )
            gr.Markdown(
                r"③ 通过修改插件配置中的配置文件路径可实现 Nai_CasRand 导出的配置文件的导入; 支持相对路径与绝对路径, 填写时, 需要将所有**反斜杠(\\)**替换为**斜杠(/)**"
            )
            gr.Markdown(
                "插件旨在学习交流, 在此感谢 [Nai_CasRand](https://github.com/Exception0x0194/NAI-Generator-Flutter) 开发者提供的出图灵感!"
            )
