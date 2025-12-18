import pygame, sys, random, math, os

# ------------------ 설정 및 초기화 ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

pygame.init()
pygame.mixer.init()

W, H = 1024, 576
SCREEN = pygame.display.set_mode((W, H))
pygame.display.set_caption("매지호 수호신 곤지 - 야옹! 매지호를 부탁해 (Final Boss Hard Mode)")
CLOCK = pygame.time.Clock()

# ------------------ 사운드 로딩 ------------------
SFX_BUFFERS = {}


def load_all_sfx():
    sfx_files = {
        "cast": "낚시(미끼 던졌을 때).mp3",
        "bite": "낚시 중(물고기가 미끼를 물었을 때).mp3",
        "meow1": "고양이 울음소리1.mp3",
        "meow2": "고양이 울음소리2.mp3",
        "step_grass": "발소리1 잔디.mp3",
        "step_dirt": "발소리2 흙.mp3",
        "step_wood": "발소리3 나무.mp3"
    }
    print("--- 효과음 로딩 ---")
    for key, filename in sfx_files.items():
        path = os.path.join("sfx", filename)
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.set_volume(0.5)
                SFX_BUFFERS[key] = sound
        except:
            pass


def play_sfx(key):
    if key in SFX_BUFFERS: SFX_BUFFERS[key].play()


def stop_sfx(key):
    if key in SFX_BUFFERS: SFX_BUFFERS[key].stop()


load_all_sfx()

# BGM 재생
current_bgm = None


def play_bgm(filename):
    global current_bgm
    if current_bgm == filename: return
    path = os.path.join("bgm", filename)
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.4)
            current_bgm = filename
        except:
            pass


# ------------------ 이미지 로딩 함수 ------------------
def load_img_safe(path, size=None, colorkey=None):
    try:
        if not os.path.exists(path):
            if path.endswith(".png") and os.path.exists(path.replace(".png", ".jpg")):
                path = path.replace(".png", ".jpg")
            elif path.endswith(".jpg") and os.path.exists(path.replace(".jpg", ".png")):
                path = path.replace(".jpg", ".png")
        if not os.path.exists(path): return pygame.Surface(size if size else (64, 64))
        img = pygame.image.load(path).convert_alpha()
        if colorkey: img.set_colorkey(colorkey)
        if size: img = pygame.transform.scale(img, size)
        return img
    except:
        return pygame.Surface(size if size else (64, 64))


# 1. 곤지/박사
GONJI_IMG_RAW = load_img_safe(os.path.join("곤지", "gonzi_stand.png"))
scale = 80 / max(1, GONJI_IMG_RAW.get_height())
GONJI_IMG = pygame.transform.scale(GONJI_IMG_RAW,
                                   (int(GONJI_IMG_RAW.get_width() * scale), int(GONJI_IMG_RAW.get_height() * scale)))
GONJI_BIG = pygame.transform.scale(GONJI_IMG_RAW,
                                   (200, int(200 * (GONJI_IMG_RAW.get_height() / max(1, GONJI_IMG_RAW.get_width())))))
DOCTOR_IMG_RAW = load_img_safe("박사님.png")
DOCTOR_BIG = pygame.transform.scale(DOCTOR_IMG_RAW, (220, int(220 * (
        DOCTOR_IMG_RAW.get_height() / max(1, DOCTOR_IMG_RAW.get_width())))))

# 낚싯대 이미지 로딩
ROD_IMGS = {
    2: load_img_safe("낚싯대 level1.jpg", (200, 200)),
    3: load_img_safe("낚싯대 level2.jpg", (200, 200))
}

# 2. 물고기
FISH_IMGS = {}
FISH_IMGS_BIG = {}


def load_fish_images():
    fish_folder = "물고기"
    mapping = {
        "변이 잉어": "병든 잉어.png", "흐릿한 붕어": "금붕어.png", "탁한 송사리": "멸치.png", "의심스런 망둥어": "우럭.png",
        "난폭한 배스": "배스.png", "플라각질 붕어": "금붕어.png", "불규칙 은어": "멸치.png", "줄끊는 강꼬치": "고등어.png",
        "어둠비늘 틸라피아": "광어.png", "이형 코이": "금붕어.png", "잔영 피라냐": "배스.png", "교란 파편": "우럭.png",
        "매지호의 폭군": "보스물고기.png"
    }
    for fish_name, filename in mapping.items():
        full_path = os.path.join(fish_folder, filename)
        FISH_IMGS[fish_name] = load_img_safe(full_path, (64, 64))
        FISH_IMGS_BIG[fish_name] = load_img_safe(full_path, (128, 128))


load_fish_images()

# 3. 배경
BG_FILES = {"lobby": "lobby.png", "center": "환경보건센터.png", 1: "첫 화면.jpg", 2: "정자.jpg", 3: "노천극장 뒤.jpg", 4: "거북섬.jpg"}
WALKABLE_AREAS = {
    "lobby": [pygame.Rect(100, 250, 800, 326), pygame.Rect(460, 130, 120, 130), pygame.Rect(880, 400, 144, 100)],
    1: [pygame.Rect(0, 350, 1024, 226), pygame.Rect(340, 280, 340, 250)],
    2: [pygame.Rect(0, 250, 350, 326)], 3: [pygame.Rect(340, 280, 250, 200)], 4: [pygame.Rect(320, 220, 380, 280)]
}


# ------------------ 공통 변수 및 UI 함수 ------------------
def get_font(size=22):
    fonts = ["malgungothic", "함초롬바탕", "batang", "dotum", "arial"]
    for f in fonts:
        try:
            return pygame.font.SysFont(f, size)
        except:
            continue
    return pygame.font.SysFont(None, size)


FONT = get_font(22);
FONT_S = get_font(16);
FONT_L = get_font(28);
FONT_XL = get_font(48)


def clamp(v, lo, hi): return max(lo, min(hi, v))


coins = 0;
rod_lv = 1;
stage_idx = 1;
bag_global = []
MESSAGE = "";
MSG_T = 0.0


def flash(msg, sec=1.5): global MESSAGE, MSG_T; MESSAGE, MSG_T = msg, sec


STAGES = [{},
          {"name": "STAGE 1 - 호숫가", "fish": ["변이 잉어", "흐릿한 붕어", "탁한 송사리", "의심스런 망둥어"], "weights": [45, 25, 20, 10],
           "goal": {"변이 잉어": 1, "흐릿한 붕어": 1, "탁한 송사리": 1, "의심스런 망둥어": 1}},
          {"name": "STAGE 2 - 정자", "fish": ["난폭한 배스", "플라각질 붕어", "불규칙 은어", "줄끊는 강꼬치"], "weights": [35, 30, 20, 15],
           "goal": {"난폭한 배스": 1, "플라각질 붕어": 1, "불규칙 은어": 1, "줄끊는 강꼬치": 1}},
          {"name": "STAGE 3 - 노천극장 뒤", "fish": ["어둠비늘 틸라피아", "이형 코이", "잔영 피라냐", "교란 파편"], "weights": [30, 30, 20, 20],
           "goal": {"어둠비늘 틸라피아": 1, "이형 코이": 1, "잔영 피라냐": 1, "교란 파편": 1}},
          {"name": "STAGE 4 - 거북섬", "fish": ["매지호의 폭군"], "weights": [100], "goal": {"매지호의 폭군": 1}},
          ]
stage_codex_counts = {i: {f: 0 for f in STAGES[i]["goal"]} for i in range(1, 5)}


def goal_met(i: int): return all(stage_codex_counts[i][n] >= STAGES[i]["goal"][n] for n in STAGES[i]["goal"])


CUTSCENES = {
    0: [("내레이션", "최근 캠퍼스 호수에서 이상한 징후들이 나타나고 있다."), ("내레이션", "물빛은 흐리고, 물고기들의 움직임도 평소와 다르다."), ("곤지", "안녕? 내 말 들리지?"),
        ("플레이어", "...고양이가 말을 한다고?"), ("곤지", "난 이 호수의 수호신 '곤지'야. 지금 호수가 위험해."),
        ("곤지", "일단 호숫가(STAGE 1)로 가보자. 직접 보면 알 수 있을 거야.")],
    1.5: [("박사", "색이 이렇게까지 변하다니... 단순 오염이 아닙니다."), ("곤지", "좋아. 이제 다음 단계로 가자."),
          ("곤지", "호수와 연결된 정자 쪽(STAGE 2)에서 교란이 심해."), ("박사", "자네에게 강화된 낚싯대를 주겠네. 이걸로 버틸 수 있을 거야."),
          ("시스템", "[낚싯대 Lv.2 획득!]")],
    2.5: [("곤지", "잡아온 녀석들 상태가 심각해. 몸에 플라스틱이 박혀 있어."), ("박사", "노이즈가 점점 커지고 있어요. 야간에 외래종 변이가 나타납니다."),
          ("곤지", "다음은 노천극장 뒤(STAGE 3)야. 외래종들이 섞여서 힘이 더 셀 거야.")],
    3.5: [("곤지", "수집한 데이터로 결론이 났어. 자연적인 변화가 아니야."), ("곤지", "호수 어딘가에서 '교란 에너지'가 새고 있어."),
          ("박사", "에너지의 원인은 '거북섬(STAGE 4)' 근처로 보입니다."), ("곤지", "마지막이야. 거북섬에서 교란의 정점이 된 개체를 막아야 해."),
          ("박사", "이건 연구소 최신 기술로 만든 특수 합금 낚싯대일세."), ("시스템", "[최강 낚싯대 Lv.3 획득!]")],
    5: [("내레이션", "(강한 빛이 주변을 감싼다...)"), ("내레이션", "빛이 잦아들자 호수는 다시 맑음을 되찾았다."), ("곤지", "네 덕분이야. 정말... 고마워."),
        ("플레이어", "난 그냥, 물고기를 잡았을 뿐인데..."), ("곤지", "아니야. 너만이 내 말을 듣고, 이 흐름을 읽어낼 수 있었어."), ("곤지", "오늘부로 넌 정식 '생태 지킴이'야."),
        ("내레이션", "플레이어와 곤지는 새로운 시작을 맞이했다."), ("곤지", "앞으로도, 함께 이 생태계를 지켜가자."), ("시스템", "축하합니다! 메인 스토리를 클리어하셨습니다.")]
}
BUBBLE_LINES = {"player": ["오늘도 잘 잡힐까?", "줄 끊기지만 않으면 좋겠다...", "곤지 말대로 여기 포인트 괜찮은데?"],
                "gonji": ["여기서 한 번 던져볼래?", "입질 오면 너무 세게는 당기지 마!", "호수 숨소리, 느껴지지?"]}


# UI 함수
def draw_message():
    global MSG_T
    if MSG_T > 0:
        MSG_T -= CLOCK.get_time() / 1000.0
        msg_surf = FONT.render(MESSAGE, True, (255, 255, 0))
        bg_rect = msg_surf.get_rect(bottomleft=(16, H - 16));
        bg_rect.inflate_ip(20, 10)
        pygame.draw.rect(SCREEN, (0, 0, 0, 180), bg_rect, border_radius=8);
        SCREEN.blit(msg_surf, (26, H - 36))


def draw_header(text):
    s = pygame.Surface((W, 40), pygame.SRCALPHA);
    s.fill((0, 0, 0, 150));
    SCREEN.blit(s, (0, 0))
    SCREEN.blit(FONT.render(text, True, (230, 230, 235)), (16, 8))
    lv_text = f"Rod Lv.{rod_lv}";
    col = (200, 200, 200)
    if rod_lv == 2: col = (100, 200, 255)
    if rod_lv == 3: col = (255, 100, 200)
    SCREEN.blit(FONT.render(lv_text, True, col), (W - 120, 8))


def draw_codex_overlay(st: int):
    panel = pygame.Rect(W - 360, 60, 320, 260)
    pygame.draw.rect(SCREEN, (12, 14, 20), panel, border_radius=10)
    pygame.draw.rect(SCREEN, (90, 90, 120), panel, 2, border_radius=10)
    SCREEN.blit(FONT.render("도감(현재 스테이지)", True, (230, 230, 230)), (panel.x + 12, panel.y + 10))
    y = panel.y + 50
    for name in STAGES[st]["fish"]:
        cnt = stage_codex_counts[st][name]
        base_img = FISH_IMGS.get(name)
        if base_img:
            icon = pygame.transform.scale(base_img, (32, 32))
            if cnt == 0:
                mask = pygame.mask.from_surface(icon)
                icon = mask.to_surface(setcolor=(0, 0, 0, 100), unsetcolor=(0, 0, 0, 0))
            SCREEN.blit(icon, (panel.x + 16, y - 6))
        color = (220, 220, 230) if cnt > 0 else (100, 100, 110)
        SCREEN.blit(FONT_S.render(f"{name} : {cnt}", True, color), (panel.x + 56, y))
        y += 40
    ok = goal_met(st)
    msg = "조건 충족! 센터로 이동" if ok else "목표: 각 1마리 이상"
    SCREEN.blit(FONT_S.render(msg, True, (80, 220, 120) if ok else (230, 210, 90)), (panel.x + 16, panel.bottom - 30))


# ------------------ 클래스 정의 ------------------
class Ripple:
    def __init__(self, x, y): self.x, self.y = x, y; self.t = 0.0; self.life = random.uniform(0.4, 0.8)

    def update(self, dt): self.t += dt

    def dead(self): return self.t >= self.life

    def draw(self, surf):
        a = 1.0 - clamp(self.t / self.life, 0, 1);
        r = int(4 + 18 * (self.t / self.life));
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 230, 255, int(180 * a)), (r + 1, r + 1), r, 2);
        surf.blit(s, (int(self.x - r - 1), int(self.y - r - 1)))


class Splash:
    def __init__(self, x, y):
        self.x, self.y = x, y;
        ang = random.uniform(-2.6, -0.5);
        spd = random.uniform(90, 160)
        self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd;
        self.t = 0.0;
        self.life = random.uniform(0.35, 0.55)

    def update(self, dt): self.t += dt; self.x += self.vx * dt; self.y += self.vy * dt; self.vy += 480 * dt * 0.6

    def dead(self): return self.t >= self.life

    def draw(self, surf): pygame.draw.circle(surf, (230, 245, 255), (int(self.x), int(self.y)), 2)


class StartScreen:
    def __init__(self, game):
        self.game = game;
        self.bg = load_img_safe("시작화면.jpg", (W, H))
        play_bgm("게임 시작화면 bgm.mp3")
        self.btn_rect = pygame.Rect(W // 2 - 202, 425, 360, 90)
        self.hover = False

    def handle(self, e):
        if e.type == pygame.MOUSEMOTION: self.hover = self.btn_rect.collidepoint(e.pos)
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.hover: self.game.change(Cutscene(self.game, 0))

    def update(self):
        pass

    def draw(self):
        SCREEN.blit(self.bg, (0, 0))
        if self.hover:
            s = pygame.Surface((self.btn_rect.w, self.btn_rect.h), pygame.SRCALPHA)
            s.fill((255, 255, 255, 60));
            SCREEN.blit(s, self.btn_rect.topleft)
            pygame.draw.rect(SCREEN, (255, 255, 200), self.btn_rect, 3, border_radius=12)


class Tutorial:
    def __init__(self, game):
        self.game = game

    def handle(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.KEYDOWN: self.game.change(Lobby(self.game))

    def update(self):
        pass

    def draw(self):
        SCREEN.fill((30, 35, 45));
        draw_header("게임 조작법")
        rect = pygame.Rect(150, 80, W - 300, H - 160)
        pygame.draw.rect(SCREEN, (50, 55, 65), rect, border_radius=15);
        pygame.draw.rect(SCREEN, (150, 150, 150), rect, 3, border_radius=15)
        texts = [("이동", "방향키(↑↓←→) 또는 WASD"), ("대화", "곤지 근처에서 SPACE 키"), ("낚시 던지기", "물가에서 마우스 왼쪽 버튼 꾹~ 눌렀다 떼기"),
                 ("물고기 잡기", "찌가 흔들리고 '!'가 뜨면 클릭!"), ("보스전", "스페이스바 연타로 보스를 당겨! (광분 시 중지)")]
        y = 120
        for t, d in texts:
            SCREEN.blit(FONT_L.render(t, True, (255, 215, 0)), (180, y));
            SCREEN.blit(FONT.render(d, True, (230, 230, 230)), (180, y + 35));
            y += 75
        info = FONT_S.render(">>> 아무 키나 눌러서 시작하세요 <<<", True, (100, 200, 255));
        SCREEN.blit(info, (W // 2 - info.get_width() // 2, H - 60))


class Player:
    def __init__(self):
        self.x, self.y, self.s = W // 2, H // 2, 3.6;
        self.w, self.h = 48, 48
        self.imgs = {
            "stand": load_img_safe(os.path.join("플레이어", "player1.png"), (48, 48)),
            "left": load_img_safe(os.path.join("플레이어", "left_walk.png"), (48, 48)),
            "right": load_img_safe(os.path.join("플레이어", "right_walk.png"), (48, 48)),
            "back": load_img_safe(os.path.join("플레이어", "back.png"), (48, 48))
        }
        self.current_img = self.imgs["stand"];
        self.facing_right = True
        self.footstep_timer = 0
        self.current_sound = None

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def center(self):
        r = self.rect();
        return r.centerx, r.centery

    def foot_point(self):
        return self.x + self.w // 2, self.y + self.h - 2

    def update(self, keys, walkable_rects, sound_type="step_wood"):
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])

        if dx != 0 or dy != 0:
            self.footstep_timer -= CLOCK.get_time() / 1000.0
            if self.footstep_timer <= 0:
                if self.current_sound: self.current_sound.stop()
                if sound_type in SFX_BUFFERS:
                    self.current_sound = SFX_BUFFERS[sound_type]
                    self.current_sound.play()
                self.footstep_timer = 0.4
        else:
            if self.current_sound:
                self.current_sound.stop()
                self.current_sound = None

        next_x = clamp(self.x + dx * self.s, 0, W - self.w);
        next_y = clamp(self.y + dy * self.s, 0, H - self.h)
        center_point = (next_x + self.w // 2, next_y + self.h - 2)
        can_walk = False
        if not walkable_rects:
            can_walk = True
        else:
            for r in walkable_rects:
                if r.collidepoint(center_point): can_walk = True; break
        if can_walk: self.x, self.y = next_x, next_y

        if dx > 0:
            self.facing_right = True;
            self.current_img = self.imgs["right"]
        elif dx < 0:
            self.facing_right = False;
            self.current_img = self.imgs["left"]
        elif dy < 0:
            self.current_img = self.imgs["back"]
        elif dy > 0:
            if self.current_img == self.imgs["back"]: self.current_img = self.imgs["right"] if self.facing_right else \
                self.imgs["left"]
        else:
            self.current_img = self.imgs["stand"] if self.facing_right else pygame.transform.flip(self.imgs["stand"],
                                                                                                  True, False)

    def draw(self, surf):
        t = pygame.time.get_ticks() / 1000.0;
        offset = int(math.sin(t * 5.0) * 2)
        surf.blit(self.current_img, (self.x, self.y + offset))


class LobbyGonji:
    def __init__(self):
        self.w, self.h = 40, 40;
        self.x, self.y = W // 2 + 100, H // 2
        self.state = "idle";
        self.target_x, self.target_y = self.x, self.y
        self.timer = 0;
        self.move_speed = 1.5
        self.dialogue_timer = 0;
        self.dialogue_text = ""
        self.lines = ["호수가 걱정이야...", "안녕? 낚시는 잘 돼?", "센터 박사님은 실력이 좋아.", "거북섬에 뭔가 있는 게 분명해.", "야옹!", "오늘 날씨가 좋네."]

        def _load(name): return load_img_safe(os.path.join("곤지", name), (self.w, self.h))

        self.imgs = {}
        self.imgs["idle"] = _load("gonzi_normal.png")
        self.imgs["down"] = [_load("곤지-앞(좌).png"), _load("곤지-앞(우).png")]
        self.imgs["up"] = [_load("곤지-뒤(좌).png"), _load("곤지-뒤(우).png")]
        self.imgs["right"] = [_load("곤지-우(좌).png"), _load("곤지-우(우).png")]
        self.imgs["left"] = [pygame.transform.flip(i, True, False) for i in self.imgs["right"]]
        self.current_img = self.imgs["idle"];
        self.anim_idx = 0;
        self.anim_timer = 0

    def update(self):
        dt = CLOCK.get_time() / 1000.0
        if self.dialogue_timer > 0: self.dialogue_timer -= dt
        if self.state == "idle":
            self.timer -= dt
            if self.timer <= 0:
                self.target_x = random.randint(200, 700);
                self.target_y = random.randint(300, 500)
                self.state = "walk";
                self.timer = random.uniform(2.0, 5.0)
        elif self.state == "walk":
            dx = self.target_x - self.x;
            dy = self.target_y - self.y;
            dist = math.hypot(dx, dy)
            if dist < 5 or self.timer <= 0:
                self.state = "idle";
                self.timer = random.uniform(2.0, 4.0);
                self.current_img = self.imgs["idle"]
            else:
                self.x += (dx / dist) * self.move_speed;
                self.y += (dy / dist) * self.move_speed;
                self.timer -= dt
                self.anim_timer += dt
                if self.anim_timer > 0.2:
                    self.anim_timer = 0;
                    self.anim_idx = (self.anim_idx + 1) % 2
                if abs(dx) > abs(dy):
                    if dx > 0:
                        self.current_img = self.imgs["right"][self.anim_idx]
                    else:
                        self.current_img = self.imgs["left"][self.anim_idx]
                else:
                    if dy > 0:
                        self.current_img = self.imgs["down"][self.anim_idx]
                    else:
                        self.current_img = self.imgs["up"][self.anim_idx]

    def interact(self):
        self.dialogue_text = random.choice(self.lines);
        self.dialogue_timer = 3.0
        self.state = "idle";
        self.timer = 2.0;
        play_sfx(random.choice(["meow1", "meow2"]))

    def draw(self, surf):
        pygame.draw.ellipse(surf, (0, 0, 0, 80), (self.x, self.y + self.h - 5, self.w, 10))
        surf.blit(self.current_img, (self.x, self.y))
        if self.dialogue_timer > 0:
            text_surf = FONT_S.render(self.dialogue_text, True, (0, 0, 0))
            bg_rect = pygame.Rect(self.x - 40, self.y - 35, text_surf.get_width() + 10, text_surf.get_height() + 6)
            if bg_rect.left < 0: bg_rect.left = 0
            if bg_rect.right > W: bg_rect.right = W
            pygame.draw.rect(surf, (255, 255, 255), bg_rect, border_radius=5);
            pygame.draw.rect(surf, (0, 0, 0), bg_rect, 1, border_radius=5)
            surf.blit(text_surf, (bg_rect.x + 5, bg_rect.y + 3))


class FishingGonji:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.img = load_img_safe(os.path.join("곤지", "gonzi_stand.png"), (40, 40))
        self.w, self.h = 40, 40

    def update(self, player):
        target_x = player.x - 40;
        target_y = player.y
        self.x += (target_x - self.x) * 0.1;
        self.y += (target_y - self.y) * 0.1

    def draw(self, surf):
        t = pygame.time.get_ticks() / 1000.0;
        offset_y = int(math.sin(t * 2.0) * 2)
        surf.blit(self.img, (int(self.x), int(self.y + offset_y)))


class Cutscene:
    def __init__(self, game, key):
        self.game = game
        self.lines = CUTSCENES.get(key, ["..."])
        self.i = 0
        self.bg_img = None
        self.key = key

        # BGM 설정
        if key == 0:
            play_bgm("게임 시작화면 bgm.mp3")
        elif key == 5:
            # 엔딩에서도 시작 화면 BGM 혹은 맑은 느낌의 BGM 사용
            play_bgm("게임 시작화면 bgm.mp3")
        else:
            play_bgm("환경보건센터 bgm.mp3")

        # --- [수정된 부분] 배경 이미지 로딩 로직 ---
        if key == 0:
            self.bg_img = load_img_safe(os.path.join("맵", "첫 화면.jpg"), (W, H))
        elif key == 5:
            # 마지막 엔딩(Key 5)일 때 정화된 호수 이미지 로드
            self.bg_img = load_img_safe(os.path.join("맵", "정화된 호수.jpg"), (W, H))
        elif key in (1.5, 2.5, 3.5):
            self.bg_img = load_img_safe(os.path.join("맵", "환경보건센터.png"), (W, H))
        # ----------------------------------------

    def handle(self, e):
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN): self.i += 1
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: self.i += 1

    def update(self):
        if self.i >= len(self.lines):
            if self.key == 0:
                self.game.change(Tutorial(self.game))
            else:
                self.game.change(Lobby(self.game))

    def draw(self):
        if self.bg_img:
            SCREEN.blit(self.bg_img, (0, 0))
            # 배경이 너무 밝으면 글씨가 안 보일 수 있으니 어두운 막 씌우기
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))  # 투명도 조절 (0~255)
            SCREEN.blit(overlay, (0, 0))
        else:
            SCREEN.fill((10, 12, 20))

        draw_header("컷신")

        if self.i < len(self.lines):
            speaker, text = self.lines[self.i]

            # 캐릭터 이미지 출력
            if speaker == "곤지":
                SCREEN.blit(GONJI_BIG, (W // 2 - 100, H // 2 - 150))
            elif speaker == "박사":
                SCREEN.blit(DOCTOR_BIG, (W // 2 - 110, H // 2 - 150))

            # 대화창 출력
            box_rect = pygame.Rect(100, H - 180, W - 200, 140)
            pygame.draw.rect(SCREEN, (30, 30, 40), box_rect, border_radius=15)
            pygame.draw.rect(SCREEN, (200, 200, 200), box_rect, 3, border_radius=15)

            name_surf = FONT_L.render(speaker, True, (255, 215, 0))
            SCREEN.blit(name_surf, (box_rect.x + 30, box_rect.y + 20))

            text_surf = FONT.render(text, True, (255, 255, 255))
            SCREEN.blit(text_surf, (box_rect.x + 30, box_rect.y + 70))

            next_surf = FONT_S.render("SPACE 키를 눌러 계속...", True, (150, 150, 150))
            SCREEN.blit(next_surf, (box_rect.right - 180, box_rect.bottom - 30))

            if "획득!" in text:
                rod_img = None
                if "Lv.2" in text:
                    rod_img = ROD_IMGS[2]
                elif "Lv.3" in text:
                    rod_img = ROD_IMGS[3]
                if rod_img:
                    cx, cy = W // 2, H // 2 - 50
                    pygame.draw.circle(SCREEN, (255, 255, 200), (cx, cy), 110)
                    SCREEN.blit(rod_img, (cx - 100, cy - 100))


class EnvCenter:
    def __init__(self, game):
        self.game = game
        self.bg_img = load_img_safe(os.path.join("맵", "환경보건센터.png"), (W, H))
        self.doctor_img = load_img_safe(os.path.join(BASE_DIR, "박사님.png"), (150, 150))
        play_bgm("환경보건센터 bgm.mp3")

    def handle(self, e):
        global rod_lv, coins
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.game.change(Lobby(self.game))
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.game.pending_stage_clear: self.game.try_center_progress()

    def update(self):
        pass

    def draw(self):
        SCREEN.blit(self.bg_img, (0, 0));
        SCREEN.blit(self.doctor_img, (W - 250, H // 2 - 50))
        draw_header("환경보건센터 (ESC=로비)")
        box_rect = pygame.Rect(80, H - 180, W - 160, 150)
        pygame.draw.rect(SCREEN, (30, 30, 40, 200), box_rect, border_radius=12);
        pygame.draw.rect(SCREEN, (100, 100, 120), box_rect, 2, border_radius=12)
        shop_x = W // 2 - 300;
        shop_y = 100;
        s = pygame.Surface((250, 200), pygame.SRCALPHA);
        s.fill((0, 0, 0, 150));
        SCREEN.blit(s, (shop_x, shop_y))
        SCREEN.blit(FONT.render("낚싯대 상태", True, (255, 200, 50)), (shop_x + 20, shop_y + 20))
        SCREEN.blit(FONT_S.render(f"현재: Lv.{rod_lv}", True, (200, 200, 200)), (shop_x + 20, shop_y + 60))

        if self.game.pending_stage_clear is None or stage_idx > 4:
            lines = ["박사: 어서 오게. 분석할 시료가 아직 없구만.", "호수에서 더 많은 데이터를 모아오게나."]
        else:
            st = self.game.pending_stage_clear;
            lines = [f"박사: 오! Stage {st}의 시료를 가져왔군.", "분석 결과가 아주 흥미로워. 들어보겠나?",
                     "(SPACE 키를 눌러 계속)"]
        y = box_rect.y + 20
        for line in lines: SCREEN.blit(FONT.render(line, True, (230, 230, 230)), (box_rect.x + 20, y)); y += 30


class FishingSystem:
    IDLE, CHARGING, CASTING, FLOATING, BITE, HOOK_QTE, REELING, RESULT, BOSS_BATTLE = range(9)

    def __init__(self, game, lake_rect):
        self.game = game;
        self.lake = lake_rect;
        self.state = self.IDLE
        self.charge = 0.0;
        self.charge_dir = 1;
        self.charge_speed = 1.5
        self.start_pos = pygame.Vector2();
        self.target_pos = pygame.Vector2();
        self.bob = pygame.Vector2()
        self.cast_progress = 0.0;
        self.cast_duration = 0.6
        self.qte_t = 0.0;
        self.qte_dur = 0.9;
        self.qte_ok_window = (0.35, 0.6);
        self.qte_radius = (64, 14)
        self.progress = 0.0;
        self.tension = 0.0;
        self.reel_up = 24.0;
        self.tens_up = 34.0;
        self.tens_rel = 26.0;
        self.prog_rel = 6.0
        self.shadow = pygame.Vector2();
        self.shadow_phase = 0.0;
        self.pull_force = 0.0
        self.ripples = [];
        self.splashes = [];
        self.success = False;
        self.result_t = 0.0;
        self.caught_name = None
        self.bite_timer = 0.0;
        self.bite_delay = (1.2, 2.6);
        self.exclaim_t = 0.0

        # 보스전 변수
        self.boss_distance = 500
        self.is_boss_angry = False
        self.boss_rage_timer = 0.0
        self.boss_phase = 1

    def reset(self):
        self.state = self.IDLE;
        self.charge = 0.0;
        self.cast_progress = 0.0
        self.ripples.clear();
        self.splashes.clear();
        self.progress = 0.0;
        self.tension = 0.0
        self.success = False;
        self.result_t = 0.0;
        self.caught_name = None
        stop_sfx("bite")

    def can_cast_here(self, px, py):
        return True

    def start_charge(self):
        if self.state == self.IDLE: self.state = self.CHARGING; self.charge = 0.0; self.charge_dir = 1

    def release_cast(self, origin, mouse_pos):
        if self.state != self.CHARGING: return
        self.state = self.CASTING;
        self.start_pos = pygame.Vector2(origin)
        cast_dist = 100.0 + (self.charge * 250.0)
        dx = mouse_pos[0] - origin[0];
        dy = mouse_pos[1] - origin[1]
        angle = math.atan2(dy, dx)
        self.target_pos.x = origin[0] + math.cos(angle) * cast_dist
        self.target_pos.y = origin[1] + math.sin(angle) * cast_dist
        self.target_pos.x = clamp(self.target_pos.x, 50, W - 50)
        self.target_pos.y = clamp(self.target_pos.y, 50, H - 50)
        self.cast_progress = 0.0;
        self.bite_timer = 0.0;
        self.progress = 0.0;
        self.tension = 0.0
        self.ripples.clear();
        self.splashes.clear();
        self.success = False;
        self.result_t = 0.0;
        self.caught_name = None
        play_sfx("cast")

    def pick_fish(self, st: int) -> str:
        names = STAGES[st]["fish"];
        base_w = STAGES[st]["weights"][:]
        counts = stage_codex_counts[st]
        missing_idx = [i for i, n in enumerate(names) if counts[n] == 0]
        if missing_idx:
            w = [bw * 0.2 for bw in base_w]
            for i in missing_idx: w[i] += base_w[i] * 3.0
        else:
            w = base_w
        r = random.random() * sum(w);
        s = 0.0
        for n, weight in zip(names, w):
            s += weight
            if r <= s: return n
        return names[-1]

    def handle_boss_input(self, e):
        # 보스전: 광분 상태를 피해 스페이스바 연타로 당기기
        if self.state == self.BOSS_BATTLE:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                if self.is_boss_angry:
                    # [난이도 수정] 광분 시 텐션 증가 + 보스 거리 회복(도망)
                    self.tension += 15
                    self.boss_distance += 20
                    flash("보스가 회복합니다! 공격 중지!", 0.5)
                else:
                    self.boss_distance -= 8
                    # [난이도 상향] 텐션 증가량 3 -> 7
                    self.tension += 7

    def start_boss_battle(self):
        self.state = self.BOSS_BATTLE;
        self.boss_distance = 500;
        self.tension = 0
        self.boss_rage_timer = random.uniform(2.0, 4.0);
        self.is_boss_angry = False

        # [수정 완료] 보스 이름 변경
        self.caught_name = "매지호의 폭군"

    def update_boss_battle(self, dt):
        # 실패: 장력이 꽉 차면 줄 끊어짐
        if self.tension >= 100:
            self.success = False;
            self.state = self.RESULT;
            self.result_t = 0.0
            return

        # 승리: 거리가 0이 되면 잡음 (바로 엔딩으로 이어짐)
        if self.boss_distance <= 0:
            self.success = True;
            self.state = self.RESULT;
            self.result_t = 0.0
            return

        # 광분 타이머 관리
        self.boss_rage_timer -= dt
        if self.boss_rage_timer <= 0:
            self.is_boss_angry = not self.is_boss_angry
            # [난이도 상향] 광분 패턴 변화 주기 단축 (더 정신없게)
            self.boss_rage_timer = random.uniform(0.8, 2.5)

            # [난이도 상향] 텐션 자연 감소 속도 하향 (회복이 느림)
        self.tension -= 15.0 * dt
        self.tension = clamp(self.tension, 0, 100)

    def update(self, dt, mouse_down, mouse_click, player_pos):
        st = max(1, min(4, stage_idx))
        reel_up = 60.0 + (rod_lv - 1) * 5.0;
        tens_up = 100.0 + (st - 1) * 20.0;
        tens_rel = 80.0

        if self.state == self.BOSS_BATTLE:
            self.update_boss_battle(dt)
            return

        if self.state == self.IDLE:
            pass
        elif self.state == self.CHARGING:
            self.charge += dt * self.charge_speed * self.charge_dir
            if self.charge >= 1.0:
                self.charge = 1.0;
                self.charge_dir = -1
            elif self.charge <= 0.0:
                self.charge = 0.0;
                self.charge_dir = 1
        elif self.state == self.CASTING:
            self.cast_progress += dt / self.cast_duration
            if self.cast_progress >= 1.0:
                self.cast_progress = 1.0;
                self.state = self.FLOATING
                self.bob = pygame.Vector2(self.target_pos)
                for _ in range(5): self.ripples.append(Ripple(self.bob.x, self.bob.y))
                self.bite_timer = random.uniform(1.0, 2.5)
            else:
                p = self.cast_progress
                ground_pos = self.start_pos.lerp(self.target_pos, p)
                height = math.sin(p * math.pi) * 100.0
                self.bob.x = ground_pos.x;
                self.bob.y = ground_pos.y - height
        elif self.state == self.FLOATING:
            self.bob.y = self.target_pos.y + math.sin(pygame.time.get_ticks() * 0.005) * 2
            self.bite_timer -= dt
            if self.bite_timer <= 0:
                self.state = self.BITE;
                self.exclaim_t = 0.8;
                play_sfx("bite");
                stop_sfx("cast")
        elif self.state == self.BITE:
            self.exclaim_t = max(0.0, self.exclaim_t - dt)
            if random.random() < 10 * dt: self.ripples.append(Ripple(self.bob.x, self.bob.y))
            if mouse_click: self.state = self.HOOK_QTE; self.qte_t = 0.0
        elif self.state == self.HOOK_QTE:
            self.qte_t += dt
            if mouse_click:
                norm = clamp(self.qte_t / self.qte_dur, 0.0, 1.0);
                ok_lo, ok_hi = self.qte_ok_window
                if ok_lo <= norm <= ok_hi:
                    self._setup_shadow();
                    stop_sfx("bite")
                    self.caught_name = self.pick_fish(st)

                    if self.caught_name == "매지호의 폭군":
                        self.start_boss_battle()
                    else:
                        self.state = self.REELING
                        for _ in range(10): self.splashes.append(Splash(self.bob.x, self.bob.y))
                else:
                    self.state = self.FLOATING;
                    self.bite_timer = random.uniform(0.8, 1.8)
            if self.qte_t >= self.qte_dur: self.state = self.FLOATING; self.bite_timer = random.uniform(0.8, 1.8)
        elif self.state == self.REELING:
            self._update_shadow(dt, st)
            if mouse_down:
                self.progress += reel_up * dt;
                self.tension += (tens_up + self.pull_force) * dt
                if random.random() < 18 * dt: self.splashes.append(Splash(self.bob.x, self.bob.y))
            else:
                self.tension -= tens_rel * dt;
                self.progress -= 15.0 * dt
            self.progress = clamp(self.progress, 0, 100);
            self.tension = clamp(self.tension, 0, 100)
            if self.tension >= 100:
                self.success = False;
                self.state = self.RESULT;
                self.result_t = 0.0
            elif self.progress >= 100:
                self.success = True;
                self.state = self.RESULT;
                self.result_t = 0.0
                for _ in range(14): self.splashes.append(Splash(self.bob.x, self.bob.y - 6))
        elif self.state == self.RESULT:
            self.result_t += dt
            if self.result_t > 0.9:
                if self.success and self.caught_name:
                    stage_codex_counts[st][self.caught_name] += 1;
                    bag_global.append(self.caught_name)
                    flash(f"성공! {self.caught_name}")
                    self.game.after_catch_check()

                    if st == 4 and self.caught_name == "매지호의 폭군":
                        self.game.change(Cutscene(self.game, 5))
                        return
                self.reset()
        for r in self.ripples: r.update(dt)
        for s in self.splashes: s.update(dt)
        self.ripples = [r for r in self.ripples if not r.dead()];
        self.splashes = [s for s in self.splashes if not s.dead()]
        if not pygame.Rect(0, 0, W, H).collidepoint(self.bob.x, self.bob.y): self.reset()

    def _setup_shadow(self):
        self.shadow.update(self.bob.x + random.uniform(-30, 30), self.bob.y + random.uniform(-20, 20))
        self.shadow_phase = 0.0;
        self.pull_force = 0.0

    def _update_shadow(self, dt, st):
        self.shadow_phase += dt
        tgt = pygame.Vector2(self.bob.x + 60 * math.sin(self.shadow_phase * 2),
                             self.bob.y + 28 * math.sin(self.shadow_phase * 1.5))
        self.shadow += (tgt - self.shadow) * min(1, dt * 3)
        if random.random() < dt: self.pull_force = random.uniform(2, 8)

    def draw(self, surf, player_pos):
        if self.state == self.BOSS_BATTLE:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA);
            overlay.fill((0, 0, 0, 100));
            surf.blit(overlay, (0, 0))

            status_text = "광분!!" if self.is_boss_angry else "당겨!!"
            col = (255, 0, 0) if self.is_boss_angry else (0, 255, 0)
            if self.is_boss_angry:
                if int(pygame.time.get_ticks() / 100) % 2 == 0:
                    red_ol = pygame.Surface((W, H), pygame.SRCALPHA);
                    red_ol.fill((255, 0, 0, 50));
                    surf.blit(red_ol, (0, 0))
            dist_surf = FONT_L.render(f"거리: {int(self.boss_distance)}m", True, (255, 255, 255))
            status_surf = FONT_XL.render(status_text, True, col)
            surf.blit(dist_surf, (W // 2 - 60, 100));
            surf.blit(status_surf, (W // 2 - 60, 150))
            pygame.draw.rect(surf, (255, 255, 255), (W // 2 - 150, 250, 300, 30), 2)
            pygame.draw.rect(surf, (255, 50, 50), (W // 2 - 148, 252, 296 * (self.tension / 100), 26))
            surf.blit(FONT.render("TENSION", True, (255, 255, 255)), (W // 2 - 40, 220))
            surf.blit(FONT_S.render("SPACE 연타로 당기세요! (광분 시 중지)", True, (200, 200, 200)), (W // 2 - 120, 300))

            boss_img = FISH_IMGS.get("매지호의 폭군")
            if boss_img:
                shake_x = random.randint(-20, 20);
                shake_y = random.randint(-20, 20)
                scaled_boss = pygame.transform.scale(boss_img, (150, 150))
                rot_angle = math.sin(pygame.time.get_ticks() * 0.02) * 30
                rotated_boss = pygame.transform.rotate(scaled_boss, rot_angle)
                rect = rotated_boss.get_rect(center=(W // 2 + shake_x, 450 + shake_y))  # Y=450
                surf.blit(rotated_boss, rect)
            return

        if self.state == self.CHARGING:
            bar_w, bar_h = 40, 6;
            bx = player_pos[0] - bar_w // 2;
            by = player_pos[1] - 60
            pygame.draw.rect(surf, (50, 50, 50), (bx, by, bar_w, bar_h))
            col = (int(255 * self.charge), int(255 * (1 - self.charge)), 0)
            pygame.draw.rect(surf, col, (bx, by, int(bar_w * self.charge), bar_h))
        if self.state in (self.CASTING, self.FLOATING, self.BITE, self.HOOK_QTE, self.REELING, self.RESULT):
            start = (player_pos[0] + 10, player_pos[1] - 20);
            end = (self.bob.x, self.bob.y)
            pygame.draw.aaline(surf, (200, 200, 200), start, end)
            pygame.draw.circle(surf, (250, 252, 252), (int(self.bob.x), int(self.bob.y)), 5)
            pygame.draw.circle(surf, (220, 70, 70), (int(self.bob.x), int(self.bob.y)), 5, 2)
        if self.state in (self.REELING,):
            s = pygame.Surface((64, 48), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (10, 25, 40, 140), (0, 12, 48, 20))
            surf.blit(s, (int(self.shadow.x - 24), int(self.shadow.y - 16)))
        if self.state == self.BITE and self.exclaim_t > 0:
            lbl = FONT.render("!", True, (255, 240, 60));
            surf.blit(lbl, (self.bob.x - lbl.get_width() // 2, self.bob.y - 35))
        if self.state == self.HOOK_QTE:
            n = self.qte_t / self.qte_dur;
            r = int(60 * (1 - n))
            pygame.draw.circle(surf, (255, 255, 255), (int(self.bob.x), int(self.bob.y)), r, 2)
            st = max(1, min(4, stage_idx));
            window = 0.15 - (st * 0.02)
            pygame.draw.circle(surf, (50, 200, 50), (int(self.bob.x), int(self.bob.y)), int(60 * (1 - (0.5 - window))),
                               1)
            t = FONT_S.render("Click!", True, (255, 255, 0));
            surf.blit(t, (self.bob.x - 20, self.bob.y - 80))
        if self.state == self.REELING:
            cx, cy = int(self.bob.x), int(self.bob.y) - 80
            pygame.draw.circle(surf, (0, 0, 0), (cx, cy), 40)
            pygame.draw.circle(surf, (100, 100, 100), (cx, cy), 40, 2)
            self._arc(surf, (100, 255, 100), (cx, cy), 36, 6, 0, int(360 * (self.progress / 100.0)))
            self._arc(surf, (255, 50, 50), (cx, cy), 28, 6, 0, int(360 * (self.tension / 100.0)))
            surf.blit(FONT_S.render("Reel!", True, (255, 255, 255)), (cx - 15, cy - 10))
            s = pygame.Surface((60, 40), pygame.SRCALPHA);
            pygame.draw.ellipse(s, (0, 0, 0, 100), (0, 0, 60, 40))
            surf.blit(s, (self.shadow.x - 30, self.shadow.y - 20))
        elif self.state == self.RESULT:
            if self.success and self.caught_name:
                overlay = pygame.Surface((W, H), pygame.SRCALPHA);
                overlay.fill((0, 0, 0, 180));
                surf.blit(overlay, (0, 0))
                cx_scr, cy_scr = W // 2, H // 2
                pygame.draw.circle(surf, (255, 255, 200), (cx_scr, cy_scr - 20), 80)
                fish_img = FISH_IMGS_BIG.get(self.caught_name)
                if fish_img: surf.blit(fish_img, (cx_scr - 64, cy_scr - 84))
                name_surf = FONT_L.render(self.caught_name, True, (255, 255, 255))
                surf.blit(name_surf, (cx_scr - name_surf.get_width() // 2, cy_scr + 60))
                sub_surf = FONT.render("잡았다!", True, (100, 255, 100))
                surf.blit(sub_surf, (cx_scr - sub_surf.get_width() // 2, cy_scr + 100))
            else:
                fail_surf = FONT.render("놓쳤다...", True, (255, 100, 100))
                bx, by = int(self.bob.x), int(self.bob.y)
                surf.blit(fail_surf, (bx - 30, by - 50))
        for r in self.ripples: r.draw(surf)
        for s in self.splashes: s.draw(surf)
        self.ripples = [r for r in self.ripples if not r.dead()];
        self.splashes = [s for s in self.splashes if not s.dead()]
        if not pygame.Rect(0, 0, W, H).collidepoint(self.bob.x, self.bob.y): self.reset()

    def _setup_shadow(self):
        self.shadow.update(self.bob.x + random.uniform(-30, 30), self.bob.y + random.uniform(-20, 20))
        self.shadow_phase = 0.0;
        self.pull_force = 0.0

    def _update_shadow(self, dt, st):
        self.shadow_phase += dt
        tgt = pygame.Vector2(self.bob.x + 60 * math.sin(self.shadow_phase * 2),
                             self.bob.y + 28 * math.sin(self.shadow_phase * 1.5))
        self.shadow += (tgt - self.shadow) * min(1, dt * 3)
        if random.random() < dt: self.pull_force = random.uniform(2, 8)

    def draw(self, surf, player_pos):
        if self.state == self.BOSS_BATTLE:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA);
            overlay.fill((0, 0, 0, 100));
            surf.blit(overlay, (0, 0))

            status_text = "광분!!" if self.is_boss_angry else "당겨!!"
            col = (255, 0, 0) if self.is_boss_angry else (0, 255, 0)
            if self.is_boss_angry:
                if int(pygame.time.get_ticks() / 100) % 2 == 0:
                    red_ol = pygame.Surface((W, H), pygame.SRCALPHA);
                    red_ol.fill((255, 0, 0, 50));
                    surf.blit(red_ol, (0, 0))
            dist_surf = FONT_L.render(f"거리: {int(self.boss_distance)}m", True, (255, 255, 255))
            status_surf = FONT_XL.render(status_text, True, col)
            surf.blit(dist_surf, (W // 2 - 60, 100));
            surf.blit(status_surf, (W // 2 - 60, 150))
            pygame.draw.rect(surf, (255, 255, 255), (W // 2 - 150, 250, 300, 30), 2)
            pygame.draw.rect(surf, (255, 50, 50), (W // 2 - 148, 252, 296 * (self.tension / 100), 26))
            surf.blit(FONT.render("TENSION", True, (255, 255, 255)), (W // 2 - 40, 220))
            surf.blit(FONT_S.render("SPACE 연타로 당기세요! (광분 시 중지)", True, (200, 200, 200)), (W // 2 - 120, 300))

            # [수정 완료] 보스 이미지 호출 이름 변경
            boss_img = FISH_IMGS.get("매지호의 폭군")
            if boss_img:
                shake_x = random.randint(-20, 20);
                shake_y = random.randint(-20, 20)
                scaled_boss = pygame.transform.scale(boss_img, (150, 150))
                rot_angle = math.sin(pygame.time.get_ticks() * 0.02) * 30
                rotated_boss = pygame.transform.rotate(scaled_boss, rot_angle)
                rect = rotated_boss.get_rect(center=(W // 2 + shake_x, 450 + shake_y))  # Y=450
                surf.blit(rotated_boss, rect)
            return

        if self.state == self.CHARGING:
            bar_w, bar_h = 40, 6;
            bx = player_pos[0] - bar_w // 2;
            by = player_pos[1] - 60
            pygame.draw.rect(surf, (50, 50, 50), (bx, by, bar_w, bar_h))
            col = (int(255 * self.charge), int(255 * (1 - self.charge)), 0)
            pygame.draw.rect(surf, col, (bx, by, int(bar_w * self.charge), bar_h))
        if self.state in (self.CASTING, self.FLOATING, self.BITE, self.HOOK_QTE, self.REELING, self.RESULT):
            start = (player_pos[0] + 10, player_pos[1] - 20);
            end = (self.bob.x, self.bob.y)
            pygame.draw.aaline(surf, (200, 200, 200), start, end)
            pygame.draw.circle(surf, (250, 252, 252), (int(self.bob.x), int(self.bob.y)), 5)
            pygame.draw.circle(surf, (220, 70, 70), (int(self.bob.x), int(self.bob.y)), 5, 2)
        if self.state in (self.REELING,):
            s = pygame.Surface((64, 48), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (10, 25, 40, 140), (0, 12, 48, 20))
            surf.blit(s, (int(self.shadow.x - 24), int(self.shadow.y - 16)))
        if self.state == self.BITE and self.exclaim_t > 0:
            lbl = FONT.render("!", True, (255, 240, 60));
            surf.blit(lbl, (self.bob.x - lbl.get_width() // 2, self.bob.y - 35))
        if self.state == self.HOOK_QTE:
            n = self.qte_t / self.qte_dur;
            r = int(60 * (1 - n))
            pygame.draw.circle(surf, (255, 255, 255), (int(self.bob.x), int(self.bob.y)), r, 2)
            st = max(1, min(4, stage_idx));
            window = 0.15 - (st * 0.02)
            pygame.draw.circle(surf, (50, 200, 50), (int(self.bob.x), int(self.bob.y)), int(60 * (1 - (0.5 - window))),
                               1)
            t = FONT_S.render("Click!", True, (255, 255, 0));
            surf.blit(t, (self.bob.x - 20, self.bob.y - 80))
        if self.state == self.REELING:
            cx, cy = int(self.bob.x), int(self.bob.y) - 80
            pygame.draw.circle(surf, (0, 0, 0), (cx, cy), 40)
            pygame.draw.circle(surf, (100, 100, 100), (cx, cy), 40, 2)
            self._arc(surf, (100, 255, 100), (cx, cy), 36, 6, 0, int(360 * (self.progress / 100.0)))
            self._arc(surf, (255, 50, 50), (cx, cy), 28, 6, 0, int(360 * (self.tension / 100.0)))
            surf.blit(FONT_S.render("Reel!", True, (255, 255, 255)), (cx - 15, cy - 10))
            s = pygame.Surface((60, 40), pygame.SRCALPHA);
            pygame.draw.ellipse(s, (0, 0, 0, 100), (0, 0, 60, 40))
            surf.blit(s, (self.shadow.x - 30, self.shadow.y - 20))
        elif self.state == self.RESULT:
            if self.success and self.caught_name:
                overlay = pygame.Surface((W, H), pygame.SRCALPHA);
                overlay.fill((0, 0, 0, 180));
                surf.blit(overlay, (0, 0))
                cx_scr, cy_scr = W // 2, H // 2
                pygame.draw.circle(surf, (255, 255, 200), (cx_scr, cy_scr - 20), 80)
                fish_img = FISH_IMGS_BIG.get(self.caught_name)
                if fish_img: surf.blit(fish_img, (cx_scr - 64, cy_scr - 84))
                name_surf = FONT_L.render(self.caught_name, True, (255, 255, 255))
                surf.blit(name_surf, (cx_scr - name_surf.get_width() // 2, cy_scr + 60))
                sub_surf = FONT.render("잡았다!", True, (100, 255, 100))
                surf.blit(sub_surf, (cx_scr - sub_surf.get_width() // 2, cy_scr + 100))
            else:
                fail_surf = FONT.render("놓쳤다...", True, (255, 100, 100))
                bx, by = int(self.bob.x), int(self.bob.y)
                surf.blit(fail_surf, (bx - 30, by - 50))
        for r in self.ripples: r.draw(surf)
        for s in self.splashes: s.draw(surf)
        self.ripples = [r for r in self.ripples if not r.dead()];
        self.splashes = [s for s in self.splashes if not s.dead()]
        if not pygame.Rect(0, 0, W, H).collidepoint(self.bob.x, self.bob.y): self.reset()

    def _arc(self, surf, color, center, radius, width, start_deg, sweep_deg):
        if sweep_deg <= 0: return
        steps = max(6, sweep_deg // 6);
        pts = []
        for i in range(steps + 1):
            a = math.radians(start_deg + sweep_deg * (i / steps))
            pts.append((center[0] + math.cos(a) * radius, center[1] + math.sin(a) * radius))
        if len(pts) >= 2: pygame.draw.lines(surf, color, False, pts, width)


class FishingMap:
    def __init__(self, game):
        self.game = game;
        self.player = Player();
        self.st = max(1, min(4, stage_idx))
        fname = BG_FILES.get(self.st, "첫 화면.jpg")
        self.bg_img = load_img_safe(os.path.join("맵", fname), (W, H))
        self.lake = pygame.Rect(140, 140, W - 280, 340)
        self.show_codex = False;
        self.fishsys = FishingSystem(game, self.lake)
        self.clicked = False;
        self.gonji = FishingGonji(self.player.x - 26, self.player.y - 4)
        self.bubble_text = "";
        self.bubble_t = 0.0;
        self.bubble_owner = "gonji"
        self.walkable_rects = WALKABLE_AREAS.get(self.st, [])
        if self.st == 1:
            play_bgm("낚시터1 bgm.mp3")
        elif self.st == 2:
            play_bgm("낚시터2 bgm.mp3")
        elif self.st == 3:
            play_bgm("외래종 서식지 bgm1.mp3")
        elif self.st == 4:
            play_bgm("보스전 bgm.mp3")
        if self.walkable_rects:
            center_rect = self.walkable_rects[0]
            self.player.x = center_rect.centerx
            self.player.y = center_rect.centery

    def handle(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.game.change(Lobby(self.game))
            elif e.key == pygame.K_c:
                self.show_codex = not getattr(self, 'show_codex', False)
            if self.fishsys.state == FishingSystem.BOSS_BATTLE: self.fishsys.handle_boss_input(e)
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.clicked = True
            if self.fishsys.state == FishingSystem.IDLE: self.fishsys.start_charge()
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.fishsys.state == FishingSystem.CHARGING: self.fishsys.release_cast(self.player.center(),
                                                                                       pygame.mouse.get_pos())

    def update(self):
        keys = pygame.key.get_pressed();
        self.player.update(keys, self.walkable_rects, "step_dirt" if self.st in (1, 4) else "step_wood")
        self.gonji.update(self.player)
        dt = CLOCK.get_time() / 1000.0;
        mouse_down = pygame.mouse.get_pressed()[0]
        clicked = self.clicked;
        self.clicked = False
        self.fishsys.update(dt, mouse_down, clicked, self.player.center())
        if self.fishsys.state in (FishingSystem.IDLE, FishingSystem.FLOATING):
            if random.random() < 0.8 * dt:
                rx = random.uniform(self.lake.x + 30, self.lake.right - 30)
                ry = random.uniform(self.lake.y + 20, self.lake.bottom - 20)
                self.fishsys.ripples.append(Ripple(rx, ry))
        if self.bubble_t > 0:
            self.bubble_t -= dt
        else:
            if random.random() < 0.12 * dt:
                owner = random.choice(["player", "gonji"]);
                self.bubble_owner = owner
                self.bubble_text = random.choice(BUBBLE_LINES[owner]);
                self.bubble_t = 3.0

    def draw_bubble(self):
        if self.bubble_t <= 0 or not self.bubble_text: return
        if self.bubble_owner == "gonji":
            anchor_x = int(self.gonji.x + self.gonji.w / 2);
            anchor_y = int(self.gonji.y)
        else:
            ax, ay = self.player.center();
            anchor_x, anchor_y = int(ax), int(ay)
        text_surf = FONT_S.render(self.bubble_text, True, (20, 20, 20))
        pad = 6;
        bw = text_surf.get_width() + pad * 2;
        bh = text_surf.get_height() + pad * 2
        rect = pygame.Rect(anchor_x - bw // 2, anchor_y - bh - 18, bw, bh)
        pygame.draw.rect(SCREEN, (255, 255, 255), rect, border_radius=8)
        pygame.draw.rect(SCREEN, (40, 40, 60), rect, 1, border_radius=8)
        tip_y = rect.bottom;
        tip_x = anchor_x
        pygame.draw.polygon(SCREEN, (255, 255, 255), [(tip_x - 6, tip_y), (tip_x + 6, tip_y), (tip_x, tip_y + 10)])
        SCREEN.blit(text_surf, (rect.x + pad, rect.y + pad))

    def draw(self):
        SCREEN.blit(self.bg_img, (0, 0))
        draw_header(f"{STAGES[self.st]['name']}  |  호숫가: LMB 길게→캐스팅, '!'에 클릭→훅셋  C=도감  ESC=로비")
        self.player.draw(SCREEN);
        self.gonji.draw(SCREEN);
        self.fishsys.draw(SCREEN, self.player.center());
        self.draw_bubble()
        SCREEN.blit(FONT_S.render(f"Coins: -", True, (255, 255, 255)), (24, H - 30))
        if getattr(self, 'show_codex', False): draw_codex_overlay(self.st)


class Lobby:
    def __init__(self, game):
        self.game = game;
        self.player = Player();
        self.walkable_rects = WALKABLE_AREAS["lobby"]
        self.gonji = LobbyGonji()
        self.bg_img = load_img_safe(os.path.join("맵", BG_FILES["lobby"]), (W, H))
        play_bgm("낚시터1 bgm.mp3")

    def handle(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            if math.hypot(self.player.x - self.gonji.x, self.player.y - self.gonji.y) < 80: self.gonji.interact()

    def update(self):
        keys = pygame.key.get_pressed();
        self.player.update(keys, self.walkable_rects, "step_wood")
        self.gonji.update()
        foot = self.player.foot_point()

        # [이동 트리거 범위 확인]
        # 센터(위쪽)
        if 460 <= foot[0] <= 580 and foot[1] <= 150:
            self.game.change(EnvCenter(self.game))
        # 낚시터(오른쪽)
        if foot[0] >= 950:
            self.game.change(FishingMap(self.game))

    def draw(self):
        SCREEN.blit(self.bg_img, (0, 0));
        draw_header(f"로비 (탐험할 곳을 선택하세요)")
        self.gonji.draw(SCREEN);
        self.player.draw(SCREEN)

        # ---------------- [직관적인 길 안내 UI 추가] ----------------
        t = pygame.time.get_ticks() / 300.0  # 애니메이션 속도
        bounce = math.sin(t) * 5  # 둥둥 떠다니는 효과

        # 1. 위쪽 (환경보건센터) 안내
        center_x, center_y = 465, 180 + bounce
        # 화살표(삼각형) 그리기
        pygame.draw.polygon(SCREEN, (255, 215, 0), [
            (center_x, center_y - 10),
            (center_x - 10, center_y + 10),
            (center_x + 10, center_y + 10)
        ])
        pygame.draw.polygon(SCREEN, (0, 0, 0), [  # 테두리
            (center_x, center_y - 10),
            (center_x - 10, center_y + 10),
            (center_x + 10, center_y + 10)
        ], 2)
        # 텍스트
        lbl_center = FONT_S.render("환경보건센터", True, (255, 255, 255))
        lbl_bg = lbl_center.get_rect(center=(center_x, center_y + 25))
        pygame.draw.rect(SCREEN, (0, 0, 0, 150), lbl_bg.inflate(10, 4), border_radius=4)
        SCREEN.blit(lbl_center, lbl_bg)

        # 2. 오른쪽 (낚시터) 안내
        lake_x, lake_y = 950 + bounce, 450
        # 화살표(삼각형) 그리기
        pygame.draw.polygon(SCREEN, (255, 215, 0), [
            (lake_x + 10, lake_y),
            (lake_x - 10, lake_y - 10),
            (lake_x - 10, lake_y + 10)
        ])
        pygame.draw.polygon(SCREEN, (0, 0, 0), [  # 테두리
            (lake_x + 10, lake_y),
            (lake_x - 10, lake_y - 10),
            (lake_x - 10, lake_y + 10)
        ], 2)
        # 텍스트
        lbl_lake = FONT_S.render("낚시터", True, (255, 255, 255))
        lbl_bg_l = lbl_lake.get_rect(center=(lake_x - 40, lake_y))
        pygame.draw.rect(SCREEN, (0, 0, 0, 150), lbl_bg_l.inflate(10, 4), border_radius=4)
        SCREEN.blit(lbl_lake, lbl_bg_l)
        # -----------------------------------------------------------

class Game:
    def __init__(self):
        self.state = StartScreen(self);
        self.pending_stage_clear = None

    def change(self, state):
        self.state = state

    def handle(self, e):
        self.state.handle(e)

    def update(self):
        self.state.update()

    def draw(self):
        self.state.draw()

    def after_catch_check(self):
        global stage_idx;
        st = max(1, min(4, stage_idx))
        if goal_met(st) and self.pending_stage_clear is None:
            self.pending_stage_clear = st;
            flash("도감 목표 달성! 로비의 환경보건센터로 가자.")

    def try_center_progress(self):
        global stage_idx, rod_lv;
        st = self.pending_stage_clear
        if st is None: flash("아직 분석할 시료가 부족합니다."); return
        self.pending_stage_clear = None
        if st == 1:
            stage_idx = 2;
            rod_lv = 2;
            self.change(Cutscene(self, 1.5))
        elif st == 2:
            stage_idx = 3;
            self.change(Cutscene(self, 2.5))
        elif st == 3:
            stage_idx = 4;
            rod_lv = 3;
            self.change(Cutscene(self, 3.5))
        elif st == 4:
            stage_idx = 5;
            self.change(Cutscene(self, 5))


def main():
    g = Game();
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_q:
                running = False
            else:
                g.handle(e)
        g.update();
        g.draw();
        draw_message()
        pygame.display.flip();
        CLOCK.tick(60)
    pygame.quit();
    sys.exit()


if __name__ == "__main__": main()