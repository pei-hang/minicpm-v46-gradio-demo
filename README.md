# MiniCPM-V 4.6 Gradio Local Demo

This repository is a simplified local Gradio demo for MiniCPM-V 4.6 multimodal inference. It supports image, multi-image, video, and text-question inputs through a browser UI.

## Attribution

This project is a modified derivative of [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V).

- Original project: [https://github.com/OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)
- Original model: [openbmb/MiniCPM-V-4.6](https://huggingface.co/openbmb/MiniCPM-V-4.6)
- Original copyright: Copyright OpenBMB
- License: Apache License 2.0

This repository is not an official OpenBMB project. It keeps the original Apache-2.0 license and includes a [NOTICE](NOTICE) file describing the derivative changes.

## What Changed

- Added `web_demos/web_demo_4.6.py`, a simplified Gradio WebUI for MiniCPM-V 4.6.
- Added `requirements_v4.6.txt` for the local inference environment.
- Added startup documentation in `README_4.6_gradio.md`.
- Added PyAV video decoding support to avoid macOS `torchvision.io.read_video` failures.
- Added local proxy handling for stable `127.0.0.1` Gradio startup.
- Removed unused legacy demos, evaluation code, and old assets from the original project.

## Repository Layout

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

Key files:

- `web_demos/web_demo_4.6.py`: Gradio inference demo.
- `README_4.6_gradio.md`: Local setup and usage guide.
- `requirements_v4.6.txt`: Dependencies for MiniCPM-V 4.6 inference.
- `finetune/`: Fine-tuning scripts retained from the upstream project for future use.
- `test/`: Small local test images.

## Model Weights

Model weights are not included in this repository.

The demo loads the official Hugging Face model by model ID:

```text
openbmb/MiniCPM-V-4.6
```

By default, Transformers downloads model files to the Hugging Face cache, for example:

```text
~/.cache/huggingface/hub/
```

Do not commit model weights or local cache directories to GitHub.

## Quick Start

```bash
python -m venv .venv-minicpmv
source .venv-minicpmv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements_v4.6.txt
python web_demos/web_demo_4.6.py
```

Open:

```text
http://127.0.0.1:7860
```

After the model has already been cached locally, you can start in local-files-only mode:

```bash
source .venv-minicpmv/bin/activate
python web_demos/web_demo_4.6.py --local-files-only
```

For more details, see [README_4.6_gradio.md](README_4.6_gradio.md).

## License

This repository is distributed under the Apache License 2.0, consistent with the upstream OpenBMB/MiniCPM-V project.

See [LICENSE](LICENSE) and [NOTICE](NOTICE).
