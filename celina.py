"""
CELINA: ECOS DE OBSSESSÃO
Jogo narrativo de suspense em Python — feito apenas com a biblioteca padrão (tkinter).

Como jogar:
  1. Salve/abra este arquivo com Python 3.
  2. Execute: python celina.py
  3. Use WASD ou as setas para andar.
  4. Pressione E perto de personagens/objetos para interagir.
  5. Pressione ESC para pausar/voltar ao menu.

O visual é 2D com profundidade falsa (2.5D), usando perspectiva,
sombras e camadas. Não precisa instalar pygame ou outros pacotes.
"""

import tkinter as tk
import random
import math

W, H = 960, 600
TILE = 48

COLORS = {
    "bg": "#10121c", "floor": "#282b3a", "floor2": "#303347",
    "wall": "#171a28", "line": "#45485e", "pink": "#d65b87",
    "red": "#a83e58", "cream": "#f0dfd2", "muted": "#a6a5b8",
    "blue": "#6c9ebd", "gold": "#d8b66d", "green": "#79a88c"
}

class CelinaGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CELINA: Ecos de Obsessão")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=W, height=H, bg=COLORS["bg"],
                                highlightthickness=0)
        self.canvas.pack()
        self.keys = set()
        self.scene = "menu"
        self.dialogue = None
        self.dialogue_index = 0
        self.flags = {"bilhete": False, "foto": False, "confianca": 0}
        self.player = {"x": 170, "y": 390}
        self.nearby = None
        self.day = 1
        self.suspense = 0
        self.ending = ""
        self.bind_keys()
        self.draw_menu()

    def bind_keys(self):
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)

    def key_down(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if key == "escape":
            if self.scene == "game":
                self.scene = "pause"
                self.draw_pause()
            elif self.scene == "pause":
                self.scene = "game"
        elif key in ("e", "space", "return"):
            if self.scene == "game":
                if self.dialogue:
                    self.advance_dialogue()
                else:
                    self.interact()
            elif self.scene == "ending":
                self.scene = "menu"
                self.draw_menu()
        elif key == "1" and self.dialogue and self.dialogue.get("choices"):
            self.choose(0)
        elif key == "2" and self.dialogue and self.dialogue.get("choices"):
            self.choose(1)

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def button(self, x, y, label, command, width=250):
        self.canvas.create_rectangle(x-width//2, y-23, x+width//2, y+23,
                                     fill="#282536", outline=COLORS["pink"], width=2)
        self.canvas.create_text(x, y, text=label, fill=COLORS["cream"],
                                font=("Georgia", 13, "bold"))
        self.canvas.tag_bind(self.canvas.find_all()[-1], "<Button-1>",
                             lambda e: command())
        self.canvas.tag_bind(self.canvas.find_all()[-2], "<Button-1>",
                             lambda e: command())

    def draw_menu(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, W, H, fill="#11121c", outline="")
        # Graphic-novel inspired abstract background
        for i in range(8):
            x = i * 145 - 60
            self.canvas.create_polygon(x, 0, x+95, 0, x+300, H, x+205, H,
                                       fill=("#1b1b2a" if i % 2 else "#202033"),
                                       outline="")
        self.canvas.create_oval(610, 55, 890, 335, fill="#4b253c", outline="")
        self.canvas.create_oval(650, 95, 850, 295, fill="#1a1b29", outline="")
        self.canvas.create_text(480, 155, text="CELINA", fill="#f0d9dc",
                                font=("Georgia", 48, "bold"))
        self.canvas.create_text(480, 207, text="ECOS DE OBSESSÃO", fill=COLORS["pink"],
                                font=("Georgia", 18, "bold"))
        self.canvas.create_text(480, 275,
            text="Uma história de mistério, escolhas e segredos no Colégio Aurora.",
            fill=COLORS["muted"], font=("Georgia", 12))
        self.button(480, 370, "COMEÇAR", self.start_game)
        self.button(480, 430, "COMO JOGAR", self.show_help)
        self.canvas.create_text(480, 555, text="Ficção • Suspense psicológico • 2.5D",
                                fill="#77778b", font=("Arial", 9))

    def show_help(self):
        self.canvas.delete("all")
        self.canvas.create_text(480, 105, text="COMO JOGAR", fill=COLORS["pink"],
                                font=("Georgia", 28, "bold"))
        lines = [
            "WASD ou setas — movimentar Celina",
            "E — conversar / examinar objetos",
            "1 ou 2 — escolher uma resposta",
            "ESC — pausar",
            "",
            "Explore o colégio, encontre pistas e decida como",
            "Celina vai lidar com seus sentimentos por Will.",
            "Suas escolhas mudam a confiança dos personagens",
            "e o desfecho da história."
        ]
        self.canvas.create_text(480, 300, text="\n".join(lines), fill=COLORS["cream"],
                                font=("Georgia", 14), justify="center", spacing=9)
        self.button(480, 500, "VOLTAR", self.draw_menu)

    def start_game(self):
        self.scene = "game"
        self.player = {"x": 165, "y": 420}
        self.dialogue = {
            "speaker": "NARRAÇÃO",
            "lines": ["Segunda-feira, 07h35. O Colégio Aurora está mais silencioso que o normal.",
                      "Celina chegou cedo. Will ainda não apareceu.",
                      "Há algo estranho no mural do corredor..."],
            "choices": None, "next": None
        }
        self.dialogue_index = 0
        self.draw_game()

    def draw_game(self):
        if self.scene != "game":
            return
        self.canvas.delete("all")
        self.draw_background()
        self.draw_objects()
        self.draw_character(self.player["x"], self.player["y"], "celina")
        self.nearby = self.find_nearby()
        self.canvas.create_rectangle(0, 0, W, 52, fill="#131521", outline="")
        self.canvas.create_text(22, 25, anchor="w", text="DIA 1  •  COLÉGIO AURORA",
                                fill=COLORS["cream"], font=("Georgia", 12, "bold"))
        self.canvas.create_text(W-22, 25, anchor="e",
                                text=f"PRESSÃO: {'●' * min(5, self.suspense)}{'○' * (5-min(5,self.suspense))}",
                                fill=COLORS["pink"], font=("Arial", 10, "bold"))
        if self.nearby and not self.dialogue:
            self.canvas.create_text(480, 505, text=f"[E] {self.nearby['hint']}",
                                    fill=COLORS["gold"], font=("Arial", 12, "bold"))
        self.canvas.create_text(18, H-18, anchor="w", text="WASD / SETAS: mover   E: interagir   ESC: pausar",
                                fill="#89899b", font=("Arial", 9))
        if self.dialogue:
            self.draw_dialogue()
        self.root.after(30, self.tick)

    def draw_background(self):
        # Hallway in pseudo-3D: floor trapezoid and converging perspective lines
        self.canvas.create_rectangle(0, 52, W, H, fill="#1b1d2b", outline="")
        self.canvas.create_polygon(0, 175, W, 175, W, H, 0, H,
                                   fill="#292b3b", outline="")
        self.canvas.create_polygon(210, 175, 750, 175, 960, 600, 0, 600,
                                   fill="#303246", outline="")
        for i in range(1, 11):
            y = 175 + i * 40
            self.canvas.create_line(0, y, W, y, fill="#41445a", width=1)
        for x in range(-200, 1200, 120):
            self.canvas.create_line(480, 175, x, 600, fill="#41445a", width=1)
        # walls and lockers
        self.canvas.create_polygon(0, 52, 210, 175, 210, 600, 0, 600,
                                   fill="#202232", outline="")
        self.canvas.create_polygon(750, 175, W, 52, W, 600, 750, 600,
                                   fill="#202232", outline="")
        for side in ("left", "right"):
            for i in range(4):
                if side == "left":
                    x1, x2 = 18+i*45, 55+i*45
                else:
                    x1, x2 = 785+i*43, 820+i*43
                y1 = 205 + i*20
                self.canvas.create_rectangle(x1, y1, x2, 430+i*10,
                    fill=("#454057" if i%2 else "#3c4054"), outline="#777087", width=2)
                self.canvas.create_oval((x1+x2)//2-2, 300, (x1+x2)//2+2, 306,
                                        fill=COLORS["gold"], outline="")
            self.canvas.create_rectangle(375, 80, 585, 171, fill="#282334",
                                     outline=COLORS["pink"], width=3)
        self.canvas.create_text(480, 108, text="COLÉGIO AURORA",
                                fill=COLORS["cream"], font=("Georgia", 15, "bold"))
        self.canvas.create_text(480, 140, text="CORREDOR PRINCIPAL",
                                fill=COLORS["muted"], font=("Arial", 9))

    def draw_objects(self):
        # Bulletin board
        self.canvas.create_rectangle(315, 205, 465, 300, fill="#6a4b4a",
                                     outline="#d4b58b", width=3)
        self.canvas.create_text(390, 220, text="MURAL", fill="#f5dfc8",
                                font=("Georgia", 11, "bold"))
        self.canvas.create_rectangle(335, 238, 390, 282, fill="#e7d8c8", outline="")
        self.canvas.create_text(362, 259, text="?", fill="#8b405b",
                                font=("Georgia", 23, "bold"))
        # Door
        self.canvas.create_rectangle(545, 200, 660, 390, fill="#443447",
                                     outline="#9b7185", width=4)
        self.canvas.create_rectangle(560, 218, 645, 372, fill="#292334",
                                     outline="#776078", width=2)
        self.canvas.create_oval(630, 295, 640, 305, fill=COLORS["gold"], outline="")
        self.canvas.create_text(600, 185, text="SALA DE MÚSICA", fill=COLORS["cream"],
                                font=("Arial", 9, "bold"))
        # Bench
        self.canvas.create_rectangle(690, 420, 820, 438, fill="#684c50", outline="")
        self.canvas.create_rectangle(700, 438, 710, 475, fill="#45333c", outline="")
        self.canvas.create_rectangle(800, 438, 810, 475, fill="#45333c", outline="")
        self.canvas.create_text(755, 402, text="BANCO", fill=COLORS["muted"],
                                font=("Arial", 8))

    def draw_character(self, x, y, kind):
        scale = max(.65, min(1.0, (y-150)/300))
        r = 16*scale
        if kind == "celina":
            body, hair, skin = "#a84468", "#211b2b", "#e6b9a9"
        else:
            body, hair, skin = "#527b9a", "#302b32", "#e7c2ae"
        self.canvas.create_oval(x-23*scale, y+12*scale, x+23*scale, y+22*scale,
                                fill="#151522", outline="")
        self.canvas.create_polygon(x-14*scale, y-2*scale, x+14*scale, y-2*scale,
                                   x+18*scale, y+40*scale, x-18*scale, y+40*scale,
                                   fill=body, outline="#171722")
        self.canvas.create_oval(x-r, y-38*scale, x+r, y-7*scale,
                                fill=skin, outline="#211b2b", width=2)
        self.canvas.create_arc(x-r-2, y-43*scale, x+r+2, y-5*scale,
                               start=0, extent=180, fill=hair, outline=hair, width=3)
        self.canvas.create_line(x-6*scale, y-21*scale, x-3*scale, y-20*scale,
                                fill="#34222c", width=2)
        self.canvas.create_line(x+4*scale, y-21*scale, x+7*scale, y-20*scale,
                                fill="#34222c", width=2)

    def find_nearby(self):
        targets = [
            {"x": 390, "y": 285, "id": "mural", "hint": "examinar o mural"},
            {"x": 600, "y": 360, "id": "door", "hint": "examinar a sala de música"},
            {"x": 755, "y": 440, "id": "bench", "hint": "olhar o banco"},
            {"x": 755, "y": 390, "id": "will", "hint": "conversar com Will"}
        ]
        for t in targets:
            if math.hypot(self.player["x"]-t["x"], self.player["y"]-t["y"]) < 72:
                return t
        return None

    def interact(self):
        target = self.find_nearby()
        if not target:
            return
        if target["id"] == "mural":
            if not self.flags["bilhete"]:
                self.flags["bilhete"] = True
                self.start_dialogue("NARRAÇÃO", [
                    "Entre os avisos, Celina encontra um bilhete dobrado.",
                    "“Will, precisamos conversar depois da aula. — M.”",
                    "A letra parece familiar, mas não há mais pistas."
                ])
            else:
                self.start_dialogue("CELINA", ["O bilhete continua aqui. Não devo tirar conclusões sem saber a verdade."])
        elif target["id"] == "door":
            self.start_dialogue("NARRAÇÃO", [
                "A sala de música está trancada.",
                "Do outro lado, uma melodia curta toca e para de repente."
            ])
        elif target["id"] == "bench":
            self.start_dialogue("NARRAÇÃO", [
                "Há uma fotografia esquecida no banco.",
                "Nela, Will aparece com colegas durante a feira cultural."
            ])
            self.flags["foto"] = True
        elif target["id"] == "will":
            self.start_dialogue("WILL", [
                "Oi, Celina. Você chegou cedo hoje.",
                "Will parece cansado, mas sorri educadamente."
            ], choices=[
                ("Perguntar sobre o bilhete", "bilhete"),
                ("Conversar sobre a feira cultural", "feira")
            ])

    def start_dialogue(self, speaker, lines, choices=None):
        self.dialogue = {"speaker": speaker, "lines": lines, "choices": choices}
        self.dialogue_index = 0
        self.draw_game()

    def draw_dialogue(self):
        d = self.dialogue
        self.canvas.create_rectangle(55, 435, 905, 570, fill="#151522",
                                     outline="#bd6687", width=2)
        self.canvas.create_text(80, 455, anchor="w", text=d["speaker"],
                                fill=COLORS["pink"], font=("Georgia", 11, "bold"))
        line = d["lines"][self.dialogue_index]
        self.canvas.create_text(80, 492, anchor="w", text=line, width=790,
                                fill=COLORS["cream"], font=("Georgia", 13))
        if d.get("choices"):
            self.canvas.create_text(80, 540, anchor="w",
                text="1 — " + d["choices"][0][0] + "       2 — " + d["choices"][1][0],
                fill=COLORS["gold"], font=("Arial", 10, "bold"))
        else:
            self.canvas.create_text(875, 550, anchor="e", text="[E] continuar",
                                    fill=COLORS["muted"], font=("Arial", 9))

    def advance_dialogue(self):
        if not self.dialogue:
            return
        if self.dialogue.get("choices"):
            return
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.dialogue["lines"]):
            self.dialogue = None
            self.draw_game()
        else:
            self.draw_game()
        
    def choose(self, index):
        if not self.dialogue or not self.dialogue.get("choices"):
            return
        choice = self.dialogue["choices"][index][1]
        if choice == "bilhete":
            if self.flags["bilhete"]:
                lines = ["Celina: “Vi um bilhete no mural. Era para você?”",
                         "Will: “Ah... deve ser da Marina. Ela quer organizar a feira.”",
                         "Will: “Você pode perguntar a ela amanhã, se quiser.”"]
                self.flags["confianca"] += 1
            else:
                lines = ["Celina: “Você parece preocupado.”",
                         "Will: “Só estou tentando terminar um trabalho. Depois conversamos?”"]
        else:
            lines = ["Celina: “A feira parece interessante. Você vai participar?”",
                     "Will: “Vou cuidar da música. Seria legal se você também participasse.”",
                     "Celina percebe que pode conhecê-lo melhor sem invadir seu espaço."]
            self.flags["confianca"] += 2
            self.suspense = max(0, self.suspense-1)
        self.dialogue = {"speaker": "CONVERSA", "lines": lines, "choices": None}
        self.dialogue_index = 0
        self.draw_game()

    def tick(self):
        if self.scene != "game":
            return
        if not self.dialogue:
            dx = dy = 0
            if "a" in self.keys or "left" in self.keys: dx -= 3
            if "d" in self.keys or "right" in self.keys: dx += 3
            if "w" in self.keys or "up" in self.keys: dy -= 3
            if "s" in self.keys or "down" in self.keys: dy += 3
            self.player["x"] = max(35, min(W-35, self.player["x"]+dx))
            self.player["y"] = max(190, min(H-75, self.player["y"]+dy))
        self.draw_game()

    def draw_pause(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, W, H, fill="#11121c", outline="")
        self.canvas.create_text(480, 190, text="PAUSADO", fill=COLORS["cream"],
                                font=("Georgia", 34, "bold"))
        self.button(480, 300, "CONTINUAR", self.resume)
        self.button(480, 365, "MENU PRINCIPAL", self.to_menu)

    def resume(self):
        self.scene = "game"
        self.draw_game()

    def to_menu(self):
        self.scene = "menu"
        self.dialogue = None
        self.draw_menu()

root = tk.Tk()
game = CelinaGame(root)
root.mainloop()