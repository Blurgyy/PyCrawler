# episodes

> *Update*: [rework](https://github.com/Blurgyy/summer2019/tree/master/summer2019_episodes)

## Features

- 搜索
- 下载 `m3u8`

> 改天补充 (or not)

## Usage

- 用法： (详见 [`client`](https://github.com/Blurgyy/PyCrawler/blob/master/episodes/client))

```python
import epi
```


- 选择下载项目时
    - 可以输入多个空格分隔的数字，非法输入将被丢弃
    - 输入 `*` 以全选

- 命令行参数（只接受第一个参数）
    - `-c <n>` 设置最大同时下载数为 `${n}` ，默认最大同时下载数为 `8` 
    - `-d` 删除文件夹
    - `-m <n>` 选择第 `${n}` 项搜索结果为下载项 (此时不从键盘读取选择下载项内容，与 `-r` 或 `-load` 配合使用，仅接受一个整数，不可全选)
    - `-n` 以新的文件名保存
    - `-o` 覆盖文件名重复的文件
    - `-s <string>` 以 `${string}` 内容为关键字搜索 
    - `-w <filepath>` 将选择下载项时的 list 输出到文件 `${filepath}`
    - `-x` 抑制输出 
    - `-load <filepath>` 读取 `${filepath}` 文件为一个 `crawler` 对象 (此时不从键盘读取搜索内容) 
    - `-dump <filepath>` 搜索结束后，将自身存为 `${filepath}` (存为二进制文件，可以使用 `-load` 重新读取，此时没有 `选择下载项` 和 `下载` 过程) 并结束
        - [`globalfunctions.py`](https://github.com/Blurgyy/PyCrawler/blob/master/episodes/epi/globalfunctions.py) 中，函数 `read_terminal_args()` 返回一个字典，作为crawl的参数，具体用法见 [`client`](https://github.com/Blurgyy/PyCrawler/blob/master/episodes/client). 例：
        - ```bash
          python3.6 client -n \
          -c 16 \
          -r input_filepath \
          -w output_filepath 
          ```

-  `*.m3u8` ：下载 [`vlc player`](https://www.videolan.org/vlc/) 本地播放，或安装 `chrome` 插件 [`Native HLS Playback`](https://raw.githubusercontent.com/Blurgyy/PyCrawler/master/episodes/Native-HLS-Playback-0.10.1.crx) 在浏览器内播放


