import math
from js import document
from pyodide.ffi.wrappers import add_event_listener

# ===== キャンバス取得 =====
off_canvas = document.getElementById("offscreen")
off_ctx = off_canvas.getContext("2d")

view_canvas = document.getElementById("view")
view_ctx = view_canvas.getContext("2d")

vw = off_canvas.width      # 4000
vh = off_canvas.height     # 400

view_w = view_canvas.width
view_h = view_canvas.height

# ===== 周波数関連のパラメータ =====
base_cycles = 4.0          # 基本の周期数
freq_factor = 1.0          # 周波数倍率（1.0 が基準）

# ===== スクロール状態管理（水平スクロールのみ） =====
scroll_x = 0
is_dragging = False
last_mouse_x = 0

def draw_offscreen():
    """現在の freq_factor を使って仮想キャンバスに sin カーブを描く"""
    # 背景
    off_ctx.fillStyle = "white"
    off_ctx.fillRect(0, 0, vw, vh)

    # 軸
    off_ctx.strokeStyle = "#cccccc"
    off_ctx.lineWidth = 1

    # x 軸
    off_ctx.beginPath()
    off_ctx.moveTo(0, vh / 2)
    off_ctx.lineTo(vw, vh / 2)
    off_ctx.stroke()

    # y 軸（左）
    off_ctx.beginPath()
    off_ctx.moveTo(0, 0)
    off_ctx.lineTo(0, vh)
    off_ctx.stroke()

    # sin カーブ
    off_ctx.strokeStyle = "blue"
    off_ctx.lineWidth = 2

    off_ctx.beginPath()

    x_min = 0.0
    x_max = base_cycles * freq_factor * math.pi * 2.0

    for i in range(vw + 1):
        t = i / vw
        x = x_min + (x_max - x_min) * t
        y = math.sin(x)

        canvas_x = i
        canvas_y = vh / 2 - y * (vh / 2 - 20)

        if i == 0:
            off_ctx.moveTo(canvas_x, canvas_y)
        else:
            off_ctx.lineTo(canvas_x, canvas_y)

    off_ctx.stroke()

def redraw_view():
    """現在の scroll_x に基づいて物理キャンバスに転送"""
    global scroll_x

    if scroll_x < 0:
        scroll_x = 0
    if scroll_x > vw - view_w:
        scroll_x = vw - view_w

    view_ctx.clearRect(0, 0, view_w, view_h)

    view_ctx.drawImage(
        off_canvas,
        scroll_x, 0, view_w, vh,
        0, 0, view_w, view_h
    )

# ===== マウスドラッグ（水平スクロールだけ） =====
def on_mousedown(event):
    global is_dragging, last_mouse_x
    is_dragging = True
    last_mouse_x = event.offsetX

def on_mousemove(event):
    global is_dragging, last_mouse_x, scroll_x
    if not is_dragging:
        return

    current_x = event.offsetX
    dx = current_x - last_mouse_x
    last_mouse_x = current_x

    scroll_x -= dx
    redraw_view()

def on_mouseup(event):
    global is_dragging
    is_dragging = False

def on_mouseleave(event):
    global is_dragging
    is_dragging = False

# ===== ホイールでの周期変更（テスト用に簡略） =====
def on_wheel(event):
    global freq_factor

    # ページスクロールを止める
    event.preventDefault()

    # deltaY > 0 が「下スクロール」[web:86][web:92]
    # ここでは 1 ステップごとに固定で変える
    if event.deltaY < 0:
        # 上スクロール: 周期を短く（周波数アップ）
        freq_factor *= 1.1
    else:
        # 下スクロール: 周期を長く（周波数ダウン）
        freq_factor /= 1.1

    # クリップ
    if freq_factor < 0.2:
        freq_factor = 0.2
    if freq_factor > 5.0:
        freq_factor = 5.0

    draw_offscreen()
    redraw_view()

# ===== 初期化 =====
def init():
    draw_offscreen()
    redraw_view()

    add_event_listener(view_canvas, "mousedown", on_mousedown)
    add_event_listener(view_canvas, "mousemove", on_mousemove)
    add_event_listener(view_canvas, "mouseup", on_mouseup)
    add_event_listener(view_canvas, "mouseleave", on_mouseleave)

    # options なしの素の wheel リスナ（まずはこれでテスト）[web:93]
    add_event_listener(view_canvas, "wheel", on_wheel)

init()