# Terminal Video Player

A command-line video player that renders video frames directly in the terminal using ANSI escape codes and 24-bit RGB colors.  
Built with **Python**, **FFmpeg**, and **Pillow**.

![Demo](demo.gif)

---

## Features

- High-quality terminal rendering using block characters and truecolor (24-bit RGB)
- Interactive UI buttons (pause, forward, backward)
- Smooth playback with configurable FPS
- Loop playback support
- Progress bar and time display
- Lightweight and fast (FFmpeg streaming)
- No GUI required — runs entirely in the terminal

---

## Requirements

- Python **3.7+**
- **FFmpeg** (must be available in `PATH`)
- **Pillow**

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/terminal-video-player.git
cd terminal-video-player
```

2. Install Python dependencies
```bash
pip install Pillow
```

3. Install FFmpeg

Ubuntu / Debian
```bash
sudo apt install ffmpeg
```

macOS
```bash
brew install ffmpeg
```

Windows

Download a static build from https://ffmpeg.org
and add ffmpeg.exe to your PATH.

Usage
```bash
python video_to_console.py <video_file> [options]
```

Options

    --width WIDTH — Output width in characters (default: 120)

    --fps FPS — Frames per second (default: 20)

    --loop — Enable loop playback

Examples

# Default playback
```bash
python video_to_console.py video.mp4
```

# Custom width and FPS
```bash
python video_to_console.py video.mp4 --width 80 --fps 30
```

# Loop playback
```bash
python video_to_console.py video.mp4 --loop
```

Controls
Key	Action
Tab	Navigate between buttons
Enter	Activate focused button
Q	Quit player
← / →	Navigate buttons (after Esc)
Buttons

    << 10s — Jump back 10 seconds

    ⏯ Pause — Pause / Resume

    10s >> — Jump forward 10 seconds

How It Works

    Video decoding
    FFmpeg streams video frames as raw RGB data.

    Frame processing
    Pillow resizes frames to match terminal resolution.

    Terminal rendering
    Each pair of vertical pixels is mapped to a single ▀ character with foreground and background colors.

    Differential updates
    Only changed cells are redrawn for performance.

    Raw terminal mode
    Enables real-time keyboard input without pressing Enter.

Limitations

    Requires a terminal with 24-bit RGB color support

    Performance depends on terminal speed and video resolution

    Audio is not supported

    Best results with high-contrast videos

Compatibility

    ✅ Linux (GNOME Terminal, Kitty, Alacritty)

    ✅ macOS (Terminal.app, iTerm2)

    ⚠️ Windows (WSL or Windows Terminal + WSL recommended)

License

MIT
Contributing

Pull requests are welcome.
For major changes, please open an issue first to discuss your proposal.
Acknowledgments

    FFmpeg — video decoding and streaming

    Pillow — image processing

    Inspired by terminal media players like mpv and caca-utils

Видеоплеер для терминала

Видеоплеер, который воспроизводит видео прямо в терминале с использованием ANSI-кодов и 24-битных RGB-цветов.
Написан на Python с использованием FFmpeg и Pillow.
Возможности

    Высококачественный рендеринг в терминале с использованием блоков и truecolor

    Интерактивные кнопки (пауза, перемотка вперёд и назад)

    Плавное воспроизведение с настраиваемым FPS

    Поддержка зацикливания

    Отображение прогресса и времени

    Не требует GUI — работает полностью в терминале

Установка
Зависимости

    Python 3.7+

    FFmpeg

    Pillow

Установка Pillow

```bash
pip install Pillow
```

Установка FFmpeg

Linux
```bash
sudo apt install ffmpeg
```

macOS
```bash
brew install ffmpeg
```

Windows

Скачайте сборку с https://ffmpeg.org


и добавьте ffmpeg.exe в PATH.
Использование
```bash
python video_to_console.py <видеофайл> [опции]
```

Опции

    --width ШИРИНА — ширина вывода (по умолчанию: 120)

    --fps FPS — кадров в секунду (по умолчанию: 20)

    --loop — зациклить воспроизведение

Управление
Клавиша	Действие
Tab	Переключение кнопок
Enter	Активация кнопки
Q	Выход
← / →	Навигация (после Esc)
Ограничения

    Нужен терминал с поддержкой 24-битных цветов

    Звук не поддерживается

    Производительность зависит от терминала и видео

Лицензия

MIT
