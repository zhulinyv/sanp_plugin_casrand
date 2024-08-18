import random

import gradio as gr
from loguru import logger

from src.setting_update import modify_env
from src.text2image_nsfw import t2i_by_hand
from utils.env import env
from utils.utils import format_str, read_json, sleep_for_cool

casrand_random_methods = [
    "全部",
    "单个 - 随机选择",
    "单个 - 顺序遍历",
    "多个 - 指定选中概率",
    "多个 - 指定数量",
]


def return_method(selectionMethod, shuffled):
    if selectionMethod == "all":
        return "全部"
    elif selectionMethod == "single" and shuffled:
        return "单个 - 随机选择"
    elif selectionMethod == "single" and not shuffled:
        return "单个 - 顺序遍历"
    elif selectionMethod == "multiple_num":
        return "多个 - 指定数量"
    elif selectionMethod == "multiple_prob":
        return "多个 - 指定选中概率"


def list_to_prompt(tag_list):
    text = ""
    for tag in tag_list:
        text += f"{tag}, "
    return text


def list_to_text(tag_list):
    text = ""
    for tag in tag_list:
        text += f"{tag}\n"
    return text.strip("\n")


def text_to_list(prompts: str):
    return prompts.split("\n")


casrand_times = {}


def generate(*args):
    sleep_for_cool(env.t2i_cool_time - 3, env.t2i_cool_time + 3)
    # for arg in args:
    #     print(arg)
    new_list = []
    while args:
        new_list.append(args[0:6])
        args = args[6:]
    # print(new_list)

    prompts = ""

    for i in new_list:
        if i[5]:
            if i[2] == "全部":
                prompts += "{}, ".format(list_to_prompt(text_to_list(i[1])))
            elif i[2] == "单个 - 随机选择":
                prompts += "{}, ".format(random.choice(text_to_list(i[1])))
            elif i[2] == "单个 - 顺序遍历":
                global casrand_times
                try:
                    prompts += "{}, ".format(
                        text_to_list(i[1])[casrand_times["{}".format(i[0])]]
                    )
                except Exception:
                    casrand_times["{}".format(i[0])] = 0
                    prompts += "{}, ".format(
                        text_to_list(i[1])[casrand_times["{}".format(i[0])]]
                    )
                casrand_times["{}".format(i[0])] = casrand_times["{}".format(i[0])] + 1
            elif i[2] == "多个 - 指定数量":
                for m in range(i[3]):
                    tag = random.choice(text_to_list(i[1]))
                    if tag not in prompts:
                        prompts += "{}, ".format(tag)
            elif i[2] == "多个 - 指定选中概率":
                for n in text_to_list(i[1]):
                    if random.random() <= i[4]:
                        prompts += "{}, ".format(n)

    logger.info(prompts := format_str(prompts))

    resolution = (
        random.choice(["832x1216", "1024x1024", "1216x832"])
        if env.img_size == -1
        else "{}x{}".format(env.img_size[0], env.img_size[1])
    ).split("x")

    img = t2i_by_hand(
        prompts,
        format_str(
            random.choice(
                read_json("./files/favorite.json")["negative_prompt"]["belief"]
            )
        ),
        resolution[0],
        resolution[1],
        env.scale,
        env.sampler,
        env.noise_schedule,
        env.steps,
        env.sm,
        env.sm_dyn,
        random.randint(1000000000, 9999999999) if env.seed == -1 else env.seed,
        times=1,
    )

    logger.debug(resolution)

    return img


def cas_rand_default_component(name, text, method, prob, num, switch):
    with gr.Row():
        name = gr.Textbox(f"{name}", show_label=False)
        probability = gr.Slider(0.1, 1, prob, step=0.1, label="概率")
        quantity = gr.Slider(1, 20, num, step=1, label="数量")
        switch = gr.Checkbox(switch, label="启用")
    random_method = gr.Dropdown(casrand_random_methods, value=method, label="选取方法")
    text_input = gr.Textbox(text, lines=3, label="字符串内容")
    for i in range(3):
        gr.Markdown("<hr>")
    return name, text_input, random_method, quantity, probability, switch


def modify_plugin_env(casrand_num, casrand_config_file):
    return modify_env(
        casrand_component_num=casrand_num,
        cas_rand_default_config=f'"{casrand_config_file}"',
    )
