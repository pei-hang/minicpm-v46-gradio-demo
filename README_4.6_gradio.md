# MiniCPM-V 4.6 Gradio 本地推理

这个说明用于运行 `web_demos/web_demo_4.6.py`，提供 MiniCPM-V 4.6 的图片、多图和视频多模态推理 WebUI。

## 1. 创建环境

建议在项目根目录使用独立虚拟环境：

```bash
cd minicpm-v46-gradio-demo
python -m venv .venv-minicpmv
source .venv-minicpmv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements_v4.6.txt
```

## 2. 首次启动

首次启动需要联网从 Hugging Face 下载模型文件：

```bash
cd minicpm-v46-gradio-demo
source .venv-minicpmv/bin/activate
python web_demos/web_demo_4.6.py
```

启动成功后打开：

```text
http://127.0.0.1:7860
```

## 3. 已缓存后的离线启动

模型下载完成后，可以使用本地缓存启动，避免每次检查 Hugging Face：

```bash
cd minicpm-v46-gradio-demo
source .venv-minicpmv/bin/activate
python web_demos/web_demo_4.6.py --local-files-only
```

## 4. 使用方式

页面支持：

- 单张图片输入
- 多图上传
- 视频上传
- 文本问题输入
- `16x` / `4x` 视觉 token 下采样切换
- 最大生成 token、temperature、top-p 等推理参数调整

推荐参数：

- 普通图片问答：`downsample_mode=16x`，速度更快
- OCR、小字、细节观察：`downsample_mode=4x`
- 高分辨率图片：适当提高 `图片最大切片数`
- 视频理解：先用较小 `视频最大采样帧数` 测试，确认效果后再调大

## 5. 常见问题

如果 Gradio 启动时报 localhost 相关 502，通常是本机代理影响了本地回环地址，启动命令里保留这些环境变量：

```bash
export NO_PROXY=localhost,127.0.0.1,0.0.0.0,::1
export no_proxy=localhost,127.0.0.1,0.0.0.0,::1
python web_demos/web_demo_4.6.py
```

如果想强制离线运行，可以加 Hugging Face 离线环境变量：

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
python web_demos/web_demo_4.6.py --local-files-only
```

如果 Hugging Face 下载慢或限流，可以登录后设置 token：

```bash
export HF_TOKEN=你的_HuggingFace_Token
```

如果端口被占用，换一个端口即可：

```bash
python web_demos/web_demo_4.6.py --server-port 7861
```

如果需要让局域网其他机器访问：

```bash
python web_demos/web_demo_4.6.py --server-name 0.0.0.0
```

如果只想确认服务是否启动：

```bash
curl -I http://127.0.0.1:7860/
```

返回 `HTTP/1.1 200 OK` 表示页面服务正常。
