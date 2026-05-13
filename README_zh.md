# MiniCPM-V 4.6 Gradio 本地演示

本项目是一个基于 MiniCPM-V 4.6 的本地 Gradio 多模态推理演示，支持图片、多图、视频和文本问题输入，可以通过浏览器界面进行交互。

## 来源声明

本项目基于 [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V) 修改而来。

- 原始项目：[https://github.com/OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)
- 原始模型：[openbmb/MiniCPM-V-4.6](https://huggingface.co/openbmb/MiniCPM-V-4.6)
- 原始版权：Copyright OpenBMB
- 开源协议：Apache License 2.0

本项目不是 OpenBMB 官方项目。本项目保留原 Apache-2.0 许可证，并通过 [NOTICE](NOTICE) 说明修改内容。

## 主要修改

- 新增 `web_demos/web_demo_4.6.py`，用于 MiniCPM-V 4.6 的 Gradio 可视化推理。
- 新增 `requirements_v4.6.txt`，用于本地推理环境安装。
- 新增 `README_4.6_gradio.md`，说明本地启动和使用方式。
- 修复 macOS 环境下视频上传推理失败的问题，强制使用 PyAV 解码视频。
- 增加本地代理绕过处理，提高 `127.0.0.1` Gradio 启动稳定性。
- 删除原项目中当前演示不需要的旧版 demo、评测代码和旧素材。

## 目录结构

```text
.
├── LICENSE
├── NOTICE
├── README.md
├── README_zh.md
├── README_4.6_gradio.md
├── requirements_v4.6.txt
├── finetune/
├── test/
└── web_demos/
    └── web_demo_4.6.py
```

核心文件：

- `web_demos/web_demo_4.6.py`：Gradio 推理主程序。
- `README_4.6_gradio.md`：本地运行说明。
- `requirements_v4.6.txt`：MiniCPM-V 4.6 推理依赖。
- `finetune/`：保留的微调训练代码，方便后续扩展。
- `test/`：本地测试图片。

## 模型权重

本仓库不包含模型权重。

程序默认通过模型 ID 加载官方 Hugging Face 模型：

```text
openbmb/MiniCPM-V-4.6
```

Transformers 默认会把模型下载到 Hugging Face 缓存目录，例如：

```text
~/.cache/huggingface/hub/
```

不要把模型权重、缓存目录或本地虚拟环境提交到 GitHub。

## 快速开始

```bash
python -m venv .venv-minicpmv
source .venv-minicpmv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements_v4.6.txt
python web_demos/web_demo_4.6.py
```

打开：

```text
http://127.0.0.1:7860
```

模型已经下载到本地缓存后，可以使用离线缓存模式：

```bash
source .venv-minicpmv/bin/activate
python web_demos/web_demo_4.6.py --local-files-only
```

更多细节见 [README_4.6_gradio.md](README_4.6_gradio.md)。

## 开源协议

本项目沿用上游 OpenBMB/MiniCPM-V 项目的 Apache License 2.0。

请查看 [LICENSE](LICENSE) 和 [NOTICE](NOTICE)。
