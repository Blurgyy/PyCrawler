# episodes

## Features

- 搜索
- 下载 `m3u8`

> 改天补充 (or not)

## Usage

- 用法： (详见 [`test.py`](https://github.com/Blurgyy/PyCrawler/blob/master/episodes/test.py))

```python
import epi
```


- 选择下载项目时
    - 可以输入多个空格分隔的数字，非法输入将被丢弃
    - 输入 `*` 以全选

- 命令行参数（只接受第一个参数）
    - `-d` 删除文件夹
    - `-n` 以新的文件名保存
    - `-s` 跳过 （默认）
    - `-o` 覆盖文件名重复的文件
    - `-c <n>` 设置最大同时下载数为 `n` ，默认最大同时下载数为 `8` 
    - `-r <filepath>` 将文件 `$filepath` 中的内容作为的 `search term` （仅读取前 `30` 个字符， `-r` 启用时不从键盘读取搜索内容） 
    - `-w <filepath>` 将选择下载项时的 list 输出到文件 `$filepath` 
        - [`globalfunctions.py`](https://github.com/Blurgyy/PyCrawler/blob/master/episodes/epi/globalfunctions.py) 中，函数 `read_terminal_args()` 返回一个字典，作为crawl的参数，具体用法见 [`test.py`](https://github.com/Blurgyy/PyCrawler/blob/master/episodes/test.py). 例：
        - ```bash
          ./test.py -n \
          -c 16 \
          -r input_filepath \
          -w output_filepath 
          ```

-  `*.m3u8` ：下载 [`vlc player`](https://www.videolan.org/vlc/) 本地播放，或安装 `chrome` 插件 [`Native HLS Playback`](https://chrome.google.com/webstore/detail/emnphkkblegpebimobpbekeedfgemhof) 在浏览器内播放


