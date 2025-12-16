import sys
import time
import subprocess
import termios
import tty
import select
from dataclasses import dataclass
from PIL import Image

ESC = "\033"

# =========================
# Terminal raw mode
# =========================

class RawTerminal:
    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, *args):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)


def read_key():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


# =========================
# Utils
# =========================

def fmt_time(sec):
    sec = max(0, int(sec))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02}:{m:02}:{s:02}"


def video_duration(path):
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path
        ]).decode().strip()
        return float(out)
    except Exception:
        return None


# =========================
# Data structures
# =========================

@dataclass(eq=True, frozen=True)
class Cell:
    ch: str
    fg: tuple
    bg: tuple


class Screen:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.buf = [[None for _ in range(w)] for _ in range(h)]

    def set(self, x, y, cell):
        self.buf[y][x] = cell

    def get(self, x, y):
        return self.buf[y][x]


class TerminalRenderer:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.prev = Screen(w, h)

    def clear(self):
        sys.stdout.write(f"{ESC}[2J{ESC}[H")
        sys.stdout.flush()

    def draw_diff(self, curr, y_offset=0):
        out = []
        for y in range(self.h):
            for x in range(self.w):
                a = self.prev.get(x, y)
                b = curr.get(x, y)
                if a != b:
                    out.append(
                        f"{ESC}[{y+1+y_offset};{x+1}H"
                        f"{ESC}[38;2;{b.fg[0]};{b.fg[1]};{b.fg[2]}m"
                        f"{ESC}[48;2;{b.bg[0]};{b.bg[1]};{b.bg[2]}m"
                        f"{b.ch}"
                    )
        out.append(f"{ESC}[0m")
        sys.stdout.write("".join(out))
        sys.stdout.flush()
        self.prev = curr


# =========================
# Frame conversion
# =========================

def render_image_to_screen(img, width):
    img = img.convert("RGB")
    sw, sh = img.size
    aspect = sh / sw

    ow = width
    oh = int(ow * aspect * 0.9)
    if oh % 2:
        oh += 1

    img = img.resize((ow, oh), Image.BILINEAR)
    px = img.load()

    scr = Screen(ow, oh // 2)

    for y in range(0, oh, 2):
        sy = y // 2
        for x in range(ow):
            r1, g1, b1 = px[x, y]
            r2, g2, b2 = px[x, y + 1]
            scr.set(x, sy, Cell("▀", (r1, g1, b1), (r2, g2, b2)))

    return scr


# =========================
# Streaming
# =========================

def start_stream(path, width, seek):
    probe = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        path
    ]).decode().strip()

    ow, oh = map(int, probe.split(","))
    w = width
    h = int(oh * w / ow)

    cmd = [
        "ffmpeg",
        "-loglevel", "quiet",
        "-ss", str(seek),
        "-i", path,
        "-vf", f"scale={w}:{h}",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return proc, w, h


# =========================
# UI buttons
# =========================

@dataclass
class Button:
    label: str
    action: str


def draw_buttons(buttons, focused, y):
    x = 2
    for i, b in enumerate(buttons):
        if i == focused:
            sys.stdout.write(f"{ESC}[{y};{x}H\033[7m [ {b.label} ] \033[0m")
        else:
            sys.stdout.write(f"{ESC}[{y};{x}H [ {b.label} ] ")
        x += len(b.label) + 6
    sys.stdout.flush()


# =========================
# Player
# =========================

def play_video(path, width=120, fps=20, loop=False):
    total = video_duration(path)
    dt = 1.0 / fps

    pos = 0.0
    paused = False

    buttons = [
        Button("<< 10s", "back"),
        Button("⏯ Pause", "pause"),
        Button("10s >>", "forward"),
    ]
    focused = 1

    with RawTerminal():
        while True:
            proc, w, h = start_stream(path, width, pos)
            frame_size = w * h * 3

            raw = proc.stdout.read(frame_size)
            if len(raw) != frame_size:
                if loop:
                    pos = 0.0
                    # Restart stream for seamless loop
                    proc.kill()
                    proc, w, h = start_stream(path, width, pos)
                    frame_size = w * h * 3
                    raw = proc.stdout.read(frame_size)
                    if len(raw) != frame_size:
                        return
                    img = Image.frombytes("RGB", (w, h), raw)
                    scr = render_image_to_screen(img, width)
                    term.clear()
                    term.draw_diff(scr, y_offset=1)
                    continue
                else:
                    return

            img = Image.frombytes("RGB", (w, h), raw)
            scr = render_image_to_screen(img, width)

            term = TerminalRenderer(scr.w, scr.h)
            term.clear()

            term.draw_diff(scr, y_offset=1)

            while True:
                # ----- UI -----
                line = (
                    f"{fmt_time(pos)} / {fmt_time(total)}"
                    if total else fmt_time(pos)
                )
                sys.stdout.write(f"{ESC}[1;1H{line.ljust(scr.w)}")
                draw_buttons(buttons, focused, y=scr.h + 3)

                key = read_key()
                if key:
                    if key == "q":
                        proc.kill()
                        return
                    if key == "\t":
                        focused = (focused + 1) % len(buttons)
                    elif key == "\x1b":  # arrows
                        k = sys.stdin.read(2)
                        if k == "[C":
                            focused = (focused + 1) % len(buttons)
                        elif k == "[D":
                            focused = (focused - 1) % len(buttons)
                    elif key == "\n":  # Enter
                        act = buttons[focused].action
                        if act == "pause":
                            paused = not paused
                        elif act == "back":
                            pos = max(0, pos - 10)
                            proc.kill()
                            break
                        elif act == "forward":
                            pos += 10
                            proc.kill()
                            break

                if paused:
                    time.sleep(0.1)
                    continue

                start = time.perf_counter()
                raw = proc.stdout.read(frame_size)
                if len(raw) != frame_size:
                    if loop:
                        pos = 0.0
                        # Restart stream for seamless loop
                        proc.kill()
                        proc, w, h = start_stream(path, width, pos)
                        frame_size = w * h * 3
                        raw = proc.stdout.read(frame_size)
                        if len(raw) != frame_size:
                            return
                        img = Image.frombytes("RGB", (w, h), raw)
                        scr2 = render_image_to_screen(img, width)
                        term.draw_diff(scr2, y_offset=1)
                        continue
                    else:
                        return

                img = Image.frombytes("RGB", (w, h), raw)
                scr2 = render_image_to_screen(img, width)
                term.draw_diff(scr2, y_offset=1)

                pos += dt

                sleep = dt - (time.perf_counter() - start)
                if sleep > 0:
                    time.sleep(sleep)


# =========================
# Entry
# =========================

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser("Terminal video player with UI buttons")
    p.add_argument("path")
    p.add_argument("--width", type=int, default=120)
    p.add_argument("--fps", type=int, default=20)
    p.add_argument("--loop", action="store_true", help="Enable infinite loop playback")
    args = p.parse_args()

    play_video(args.path, args.width, args.fps, args.loop)
