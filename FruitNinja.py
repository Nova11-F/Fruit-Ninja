"""
Fruit Ninja berbasis Computer Vision
------------------------------------
Gerakkan jari telunjuk di depan webcam untuk menebas buah.
Waktu bermain 60 detik. Buah yang terlewat tidak apa-apa, game tetap lanjut!
Hindari bom (hitam): kena bom mengurangi skor.

Kontrol:  R = main ulang   |   Q / ESC = keluar

Instalasi:
    pip install opencv-python mediapipe==0.10.14 numpy
"""

import math
import os
import random
import time
from collections import deque

import cv2
import mediapipe as mp
import numpy as np

# ---------------- Konfigurasi ----------------
WIDTH, HEIGHT = 1280, 720
GRAVITY = 0.45
SPAWN_INTERVAL = 0.9        # detik antar lemparan (makin kecil makin sulit)
SLICE_SPEED = 25            # kecepatan minimum jari (piksel/frame) agar dianggap tebasan
TRAIL_LENGTH = 12
ROUND_TIME = 60            # durasi permainan (detik)
COUNTDOWN = 3              # hitung mundur sebelum mulai (detik)
BOMB_PENALTY = 20          # pengurangan skor jika menebas bom
BOMB_CHANCE = 0.18

FRUITS = {  # nama: (warna BGR, warna dalam BGR, radius)
    "apel":    ((60, 60, 230),  (200, 220, 255), 38),
    "jeruk":   ((0, 140, 255),  (120, 200, 255), 40),
    "semangka": ((60, 170, 60), (90, 90, 240),   48),
    "lemon":   ((0, 230, 240),  (180, 245, 250), 34),
    "anggur":  ((160, 50, 140), (210, 150, 200), 30),
}


# ---------------- Objek game ----------------
class Item:
    def __init__(self, bomb=False):
        self.bomb = bomb
        if bomb:
            self.color, self.inner, self.radius = (30, 30, 30), (30, 30, 30), 36
            self.name = "bom"
        else:
            self.name = random.choice(list(FRUITS))
            self.color, self.inner, self.radius = FRUITS[self.name]
        self.x = random.randint(150, WIDTH - 150)
        self.y = HEIGHT + self.radius
        self.vx = random.uniform(-5, 5) * (1 if self.x < WIDTH / 2 else -1) * -1
        # arahkan ke tengah layar
        self.vx = (WIDTH / 2 - self.x) / 120 + random.uniform(-2, 2)
        self.vy = random.uniform(-26, -19)
        self.sliced = False
        self.missed = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY

    def draw(self, frame):
        c = (int(self.x), int(self.y))
        cv2.circle(frame, c, self.radius, self.color, -1, cv2.LINE_AA)
        cv2.circle(frame, c, self.radius, (255, 255, 255), 2, cv2.LINE_AA)
        if self.bomb:
            cv2.putText(frame, "X", (c[0] - 12, c[1] + 12),
                        cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 3, cv2.LINE_AA)
        else:  # kilau kecil
            cv2.circle(frame, (c[0] - self.radius // 3, c[1] - self.radius // 3),
                       self.radius // 6, (255, 255, 255), -1, cv2.LINE_AA)


class Half:
    """Potongan buah setelah ditebas."""
    def __init__(self, item, direction):
        self.x, self.y = item.x, item.y
        self.vx = item.vx + direction * random.uniform(2, 5)
        self.vy = item.vy * 0.3
        self.r = item.radius
        self.color, self.inner = item.color, item.inner
        self.direction = direction
        self.life = 40

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY
        self.life -= 1

    def draw(self, frame):
        center = (int(self.x), int(self.y))
        start = 90 if self.direction < 0 else -90
        cv2.ellipse(frame, center, (self.r, self.r), 0, start, start + 180,
                    self.color, -1, cv2.LINE_AA)
        cv2.ellipse(frame, center, (self.r - 8, self.r - 8), 0, start, start + 180,
                    self.inner, -1, cv2.LINE_AA)


class Splash:
    def __init__(self, x, y, color):
        self.parts = [[x, y, random.uniform(-7, 7), random.uniform(-9, 3)]
                      for _ in range(14)]
        self.color = color
        self.life = 18

    def update(self):
        for p in self.parts:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.5
        self.life -= 1

    def draw(self, frame):
        for p in self.parts:
            cv2.circle(frame, (int(p[0]), int(p[1])), 4, self.color, -1)


# ---------------- Utilitas ----------------
def seg_hits_circle(p1, p2, c, r):
    """Cek apakah segmen garis p1-p2 memotong lingkaran (c, r)."""
    (x1, y1), (x2, y2), (cx, cy) = p1, p2, c
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(cx - x1, cy - y1) <= r
    t = max(0, min(1, ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(cx - (x1 + t * dx), cy - (y1 + t * dy)) <= r


def put_text(frame, text, pos, scale=1.0, color=(255, 255, 255), thick=2):
    cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_DUPLEX, scale, (0, 0, 0),
                thick + 3, cv2.LINE_AA)
    cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_DUPLEX, scale, color,
                thick, cv2.LINE_AA)


# ---------------- Game utama ----------------
class Game:
    def __init__(self):
        self.high_score = 0
        self.reset()

    def reset(self):
        self.items, self.halves, self.splashes = [], [], []
        self.score = 0
        self.combo = 0
        self.flash = 0
        self.new_record = False
        self.state = "countdown"       # countdown -> playing -> over
        self.state_start = time.time()
        self.last_spawn = time.time()

    @property
    def playing(self):
        return self.state == "playing"

    def time_left(self):
        return max(0.0, ROUND_TIME - (time.time() - self.state_start))

    def spawn(self):
        n = random.choice([1, 1, 2, 3])
        for _ in range(n):
            self.items.append(Item(bomb=random.random() < BOMB_CHANCE))

    def slice_check(self, p1, p2):
        sliced_now = 0
        for it in self.items:
            if it.sliced:
                continue
            if seg_hits_circle(p1, p2, (it.x, it.y), it.radius):
                it.sliced = True
                if it.bomb:
                    self.score = max(0, self.score - BOMB_PENALTY)
                    self.flash = 10
                    self.combo = 0
                else:
                    sliced_now += 1
                    self.score += 10
                    self.halves += [Half(it, -1), Half(it, 1)]
                    self.splashes.append(Splash(it.x, it.y, it.color))
        if sliced_now >= 2:  # bonus combo
            bonus = sliced_now * 5
            self.score += bonus
            self.combo = sliced_now

    def update(self):
        now = time.time()
        if self.state == "countdown":
            if now - self.state_start >= COUNTDOWN:
                self.state = "playing"
                self.state_start = now
                self.last_spawn = now
        elif self.state == "playing":
            if now - self.last_spawn > SPAWN_INTERVAL:
                self.spawn()
                self.last_spawn = now
            if self.time_left() <= 0:
                self.state = "over"
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.new_record = True

        for it in self.items:
            it.update()
        self.items = [i for i in self.items if not i.sliced and i.y < HEIGHT + 120]

        for h in self.halves:
            h.update()
        self.halves = [h for h in self.halves if h.life > 0]
        for s in self.splashes:
            s.update()
        self.splashes = [s for s in self.splashes if s.life > 0]


    def draw(self, frame):
        if self.flash > 0:  # kilatan merah saat kena damage
            overlay = frame.copy()
            overlay[:] = (0, 0, 200)
            frame[:] = cv2.addWeighted(overlay, 0.25, frame, 0.75, 0)
            self.flash -= 1
        for s in self.splashes:
            s.draw(frame)
        for h in self.halves:
            h.draw(frame)
        for it in self.items:
            it.draw(frame)

        put_text(frame, f"Skor: {self.score}", (30, 60), 1.4, (0, 255, 255), 3)
        put_text(frame, f"Terbaik: {self.high_score}", (30, 105), 0.9, (200, 200, 200), 2)

        # timer + bar waktu
        if self.state == "playing":
            left = self.time_left()
            urgent = left <= 10
            col = (80, 80, 255) if urgent else (255, 255, 255)
            put_text(frame, f"{int(math.ceil(left))}s", (WIDTH // 2 - 45, 60), 1.6, col, 3)
            frac = left / ROUND_TIME
            cv2.rectangle(frame, (0, 0), (WIDTH, 10), (40, 40, 40), -1)
            cv2.rectangle(frame, (0, 0), (int(WIDTH * frac), 10),
                          (0, 0, 255) if urgent else (0, 220, 120), -1)
        if self.combo >= 2 and self.playing:
            put_text(frame, f"COMBO x{self.combo}!", (WIDTH // 2 - 120, 125),
                     1.5, (0, 255, 0), 3)

        if self.state == "countdown":
            remain = COUNTDOWN - (time.time() - self.state_start)
            put_text(frame, "BERSIAP!", (WIDTH // 2 - 140, HEIGHT // 2 - 100),
                     1.8, (0, 255, 255), 4)
            put_text(frame, str(max(1, math.ceil(remain))),
                     (WIDTH // 2 - 40, HEIGHT // 2 + 50), 4.0, (255, 255, 255), 8)
            put_text(frame, "Tebas buah dengan jari telunjuk",
                     (WIDTH // 2 - 250, HEIGHT // 2 + 120), 1.0, (200, 200, 200))

        if self.state == "over":
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
            frame[:] = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
            put_text(frame, "WAKTU HABIS!", (WIDTH // 2 - 280, HEIGHT // 2 - 40),
                     2.5, (0, 200, 255), 5)
            put_text(frame, f"Skor akhir: {self.score}",
                     (WIDTH // 2 - 160, HEIGHT // 2 + 30), 1.3)
            if self.new_record:
                put_text(frame, "REKOR BARU!", (WIDTH // 2 - 130, HEIGHT // 2 + 90),
                         1.2, (0, 255, 0), 3)
            put_text(frame, "Tekan R untuk main lagi",
                     (WIDTH // 2 - 200, HEIGHT // 2 + 150), 1.0, (200, 200, 200))


def open_camera():
    """Cari kamera yang benar-benar bisa mengirim gambar (Windows: coba DSHOW/MSMF)."""
    if os.name == "nt":
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    else:
        backends = [cv2.CAP_ANY]
    for backend in backends:
        for index in range(4):
            cap = cv2.VideoCapture(index, backend)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
                ok = False
                for _ in range(10):  # beberapa frame pertama kadang kosong
                    ok, _frame = cap.read()
                    if ok:
                        break
                    time.sleep(0.1)
                if ok:
                    print(f"Kamera ditemukan (index {index}, backend {backend}).")
                    return cap
            cap.release()
    return None


def main():
    cap = open_camera()
    if cap is None:
        raise SystemExit(
            "Tidak ada kamera yang bisa dibaca. Tutup aplikasi lain yang memakai "
            "kamera (Zoom, Teams, browser) dan cek izin kamera di Windows: "
            "Settings > Privacy > Camera."
        )

    hands = mp.solutions.hands.Hands(
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )

    game = Game()
    trail = deque(maxlen=TRAIL_LENGTH)
    prev = None
    fps_t, fps = time.time(), 0

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Gagal membaca gambar dari kamera, game dihentikan.")
            break
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.addWeighted(frame, 0.75, np.zeros_like(frame), 0.25, 0)  # redupkan

        # --- deteksi ujung jari telunjuk ---
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        tip = None
        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0].landmark[8]  # INDEX_FINGER_TIP
            tip = (int(lm.x * WIDTH), int(lm.y * HEIGHT))

        if tip is not None:
            trail.append(tip)
            if prev is not None and game.playing:
                speed = math.hypot(tip[0] - prev[0], tip[1] - prev[1])
                if speed > SLICE_SPEED:
                    game.slice_check(prev, tip)
            prev = tip
        else:
            trail.clear()
            prev = None

        game.update()
        game.draw(frame)

        # --- gambar jejak tebasan ---
        pts = list(trail)
        for i in range(1, len(pts)):
            thickness = int(2 + 12 * i / len(pts))
            cv2.line(frame, pts[i - 1], pts[i], (255, 255, 255), thickness, cv2.LINE_AA)
            cv2.line(frame, pts[i - 1], pts[i], (255, 200, 0), max(1, thickness - 4),
                     cv2.LINE_AA)
        if tip:
            cv2.circle(frame, tip, 10, (0, 255, 255), -1, cv2.LINE_AA)

        # --- FPS ---
        now = time.time()
        fps = 0.9 * fps + 0.1 * (1 / max(now - fps_t, 1e-6))
        fps_t = now
        put_text(frame, f"FPS {int(fps)}", (WIDTH - 140, 40), 0.7, (180, 255, 180), 1)

        cv2.imshow("Fruit Ninja CV", frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        if key == ord("r"):
            game.reset()

    cap.release()
    hands.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()