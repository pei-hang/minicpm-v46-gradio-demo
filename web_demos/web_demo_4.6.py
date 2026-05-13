#!/usr/bin/env python
# encoding: utf-8
#
# This file was added in this derivative repository for a simplified
# MiniCPM-V 4.6 Gradio demo. The project is based on OpenBMB/MiniCPM-V
# and is distributed under the Apache License 2.0.
import argparse
import os
import tempfile
import traceback
import types

import gradio as gr
import torch
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor
from transformers.video_utils import load_video


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm", ".m4v"}
DEFAULT_PROMPT = "请详细描述输入内容，并回答我接下来的问题。"


def parse_args():
    parser = argparse.ArgumentParser(description="MiniCPM-V 4.6 Gradio demo")
    parser.add_argument(
        "--model",
        type=str,
        default="openbmb/MiniCPM-V-4.6",
        help="Hugging Face model id or local model path",
    )
    parser.add_argument("--server-name", type=str, default="127.0.0.1")
    parser.add_argument("--server-port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Load only from the local Hugging Face cache or a local model path.",
    )
    parser.add_argument(
        "--attn-implementation",
        type=str,
        default=None,
        choices=["sdpa", "flash_attention_2"],
        help="Optional attention backend. flash_attention_2 requires flash-attn.",
    )
    return parser.parse_args()


def ensure_localhost_no_proxy():
    local_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
    for key in ("NO_PROXY", "no_proxy"):
        current = os.environ.get(key, "")
        entries = [item.strip() for item in current.split(",") if item.strip()]
        for host in local_hosts:
            if host not in entries:
                entries.append(host)
        os.environ[key] = ",".join(entries)


def force_pyav_video_backend(processor):
    def fetch_videos_with_pyav(self, video_url_or_urls, sample_indices_fn=None):
        if isinstance(video_url_or_urls, list):
            return list(
                zip(
                    *[
                        self.fetch_videos(item, sample_indices_fn=sample_indices_fn)
                        for item in video_url_or_urls
                    ]
                )
            )
        return load_video(
            video_url_or_urls,
            backend="pyav",
            sample_indices_fn=sample_indices_fn,
        )

    if hasattr(processor, "video_processor"):
        processor.video_processor.fetch_videos = types.MethodType(
            fetch_videos_with_pyav,
            processor.video_processor,
        )


def file_path(file_obj):
    if file_obj is None:
        return None
    if isinstance(file_obj, dict):
        return file_obj.get("path") or file_obj.get("name")
    if isinstance(file_obj, str):
        return file_obj
    return getattr(file_obj, "name", None) or getattr(file_obj, "path", None)


def suffix(path):
    return os.path.splitext(path or "")[1].lower()


def is_image(path):
    return suffix(path) in IMAGE_EXTENSIONS


def is_video(path):
    return suffix(path) in VIDEO_EXTENSIONS


def save_image_for_processor(image):
    if image is None:
        return None
    if isinstance(image, str):
        return image
    if not isinstance(image, Image.Image):
        image = Image.open(image).convert("RGB")
    image = image.convert("RGB")
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    image.save(tmp.name)
    return tmp.name


def build_message(prompt, image, image_files, video):
    content = []
    single_image_path = save_image_for_processor(image)
    if single_image_path:
        content.append({"type": "image", "url": single_image_path})

    for item in image_files or []:
        path = file_path(item)
        if path and is_image(path):
            content.append({"type": "image", "url": path})

    video_path = file_path(video)
    if video_path and is_video(video_path):
        content.append({"type": "video", "url": video_path})

    text = (prompt or "").strip() or DEFAULT_PROMPT
    content.append({"type": "text", "text": text})
    return [{"role": "user", "content": content}]


def trim_generated_ids(inputs, generated_ids):
    return [
        out_ids[len(in_ids):]
        for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]


def normalize_output_text(text):
    return (
        text.replace("\\r\\n", "\n")
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .strip()
    )


def make_infer_fn(model, processor):
    def infer(
        image,
        image_files,
        video,
        prompt,
        downsample_mode,
        max_new_tokens,
        temperature,
        top_p,
        max_slice_nums,
        max_num_frames,
        stack_frames,
    ):
        try:
            messages = build_message(prompt, image, image_files, video)
            has_video = any(item.get("type") == "video" for item in messages[0]["content"])
            template_kwargs = {
                "downsample_mode": downsample_mode,
                "max_slice_nums": int(max_slice_nums),
            }
            if has_video:
                template_kwargs.update(
                    {
                        "max_num_frames": int(max_num_frames),
                        "stack_frames": int(stack_frames),
                        "use_image_id": False,
                    }
                )

            inputs = processor.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt",
                **template_kwargs,
            ).to(model.device)

            generation_kwargs = {
                "downsample_mode": downsample_mode,
                "max_new_tokens": int(max_new_tokens),
            }
            if temperature > 0:
                generation_kwargs.update(
                    {
                        "do_sample": True,
                        "temperature": float(temperature),
                        "top_p": float(top_p),
                    }
                )
            else:
                generation_kwargs["do_sample"] = False

            with torch.inference_mode():
                generated_ids = model.generate(**inputs, **generation_kwargs)

            output_text = processor.batch_decode(
                trim_generated_ids(inputs, generated_ids),
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )
            return normalize_output_text(output_text[0])
        except Exception:
            traceback.print_exc()
            return "推理失败，请查看终端日志中的异常信息。"

    return infer


def build_demo(model, processor, model_name):
    infer = make_infer_fn(model, processor)
    css = """
    .container {max-width: 1180px; margin: 0 auto;}
    .status {font-size: 13px; color: #555;}
    """
    with gr.Blocks(css=css, title="MiniCPM-V 4.6 Gradio") as demo:
        gr.Markdown(f"## MiniCPM-V 多模态推理\n<span class='status'>当前模型：{model_name}</span>")
        with gr.Row(elem_classes="container"):
            with gr.Column(scale=1):
                image = gr.Image(type="pil", label="单张图片")
                image_files = gr.Files(
                    label="多图上传",
                    file_count="multiple",
                    file_types=sorted(IMAGE_EXTENSIONS),
                )
                video = gr.File(label="视频上传", file_types=sorted(VIDEO_EXTENSIONS))
                prompt = gr.Textbox(
                    label="问题",
                    lines=5,
                    value="请描述这张图片/这个视频，并给出关键细节。",
                )
                submit = gr.Button("开始推理", variant="primary")
                clear = gr.ClearButton([image, image_files, video, prompt])
            with gr.Column(scale=1):
                output = gr.Textbox(label="模型回答", lines=24)
                with gr.Accordion("推理参数", open=False):
                    downsample_mode = gr.Radio(
                        choices=["16x", "4x"],
                        value="16x",
                        label="视觉 token 下采样",
                    )
                    max_new_tokens = gr.Slider(
                        minimum=64,
                        maximum=4096,
                        value=1024,
                        step=64,
                        label="最大生成 token",
                    )
                    temperature = gr.Slider(
                        minimum=0,
                        maximum=1.5,
                        value=0.2,
                        step=0.05,
                        label="Temperature，0 表示贪心解码",
                    )
                    top_p = gr.Slider(
                        minimum=0.1,
                        maximum=1.0,
                        value=0.9,
                        step=0.05,
                        label="Top-p",
                    )
                    max_slice_nums = gr.Slider(
                        minimum=1,
                        maximum=64,
                        value=36,
                        step=1,
                        label="图片最大切片数",
                    )
                    max_num_frames = gr.Slider(
                        minimum=1,
                        maximum=128,
                        value=64,
                        step=1,
                        label="视频最大采样帧数",
                    )
                    stack_frames = gr.Slider(
                        minimum=1,
                        maximum=5,
                        value=1,
                        step=1,
                        label="视频每秒采样点数",
                    )

        submit.click(
            infer,
            inputs=[
                image,
                image_files,
                video,
                prompt,
                downsample_mode,
                max_new_tokens,
                temperature,
                top_p,
                max_slice_nums,
                max_num_frames,
                stack_frames,
            ],
            outputs=output,
        )
    return demo


def main():
    ensure_localhost_no_proxy()
    args = parse_args()
    model_kwargs = {
        "torch_dtype": "auto",
        "device_map": "auto",
        "local_files_only": args.local_files_only,
    }
    if args.attn_implementation:
        model_kwargs["attn_implementation"] = args.attn_implementation

    print(f"Loading processor from {args.model}")
    processor = AutoProcessor.from_pretrained(
        args.model,
        local_files_only=args.local_files_only,
    )
    force_pyav_video_backend(processor)
    print(f"Loading model from {args.model}")
    model = AutoModelForImageTextToText.from_pretrained(args.model, **model_kwargs)
    model.eval()

    demo = build_demo(model, processor, args.model)
    demo.launch(
        share=args.share,
        server_name=args.server_name,
        server_port=args.server_port,
    )


if __name__ == "__main__":
    main()
