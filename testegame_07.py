import pygame
import sys
import time
import random

# ================== CONFIGURAÇÕES BASE ==================
pygame.init()
pygame.mixer.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Ecos da Lua Carmesim — Dark Romance")

# Cores — Estilo sombrio
PRETO = (10, 10, 18)
VINHO = (90, 15, 30)
ROXO_ESCURO = (40, 15, 60)
PRATA = (200, 200, 210)
CINZA = (80, 80, 90)
VERMELHO_FRACO = (140, 25, 45)
DOURADO = (180, 140, 20)
AZUL_PROFUNDO = (20, 30, 80)

# Fontes estilo retrô/pixel
fonte_titulo = pygame.font.Font(None, 52)
fonte_texto = pygame.font.Font(None, 32)
fonte_escolha = pygame.font.Font(None, 28)

clock = pygame.time.Clock()
FPS = 30

# ================== 🎵 MÚSICA — KAMAITACHI ==================
try:
    pygame.mixer.music.load("trilha.mp3")  # Homen Torto - Kamaitachi
    pygame.mixer.music.set_volume(0.35)      # Volume equilibrado
    pygame.mixer.music.play(-1)               # Repetição infinita
    print("🎵 Tocando: Homen Torto — Kamaitachi")
except Exception as erro:
    print(f"⚠️ Música não encontrada: {erro}")
    print("👉 Coloque 'trilha.mp3' na pasta do jogo!")

# ================== 🖼️ IMAGEM — MANSÃO ==================
imagem_mansao = None
try:
    imagem_mansao = pygame.image.load("cena1.png").convert()
    imagem_mansao = pygame.transform.scale(imagem_mansao, (LARGURA, ALTURA))
    print("🏚️ Imagem da mansão carregada!")
except Exception as erro:
    print(f"⚠️ Imagem não encontrada: {erro}")
    print("👉 Usando fundo alternativo...")

# ================== DADOS DO JOGO ==================
personagem = {
    "nome": "Você",
    "afeto_lucian": 0,
    "afeto_elara": 0,
    "afeto_morrigan": 0,
    "confianca": 50,
    "capitulo": 1
}

cenas = [
    {
        "id": 1,
        "titulo": "A Porta da Mansão",
        "texto": """A chuva cai sobre pedras antigas. À sua frente, a mansão ergue-se como uma sombra viva.
Dizem que quem entra... raramente sai o mesmo. No limiar, uma figura se destaca:
Lucian, olhos prateados, postura de quem guarda segredos profundos demais para serem ditos.""",
        "escolhas": [
            "• Avançar e dizer: 'Eu vim procurar a verdade, não fui convidada.'",
            "• Ficar parada, observando-o em silêncio, esperando que ele fale primeiro.",
            "• Recuar um passo, hesitante, mas sem virar completamente."
        ],
        "efeitos": [
            {"afeto_lucian": 15, "confianca": 10},
            {"afeto_lucian": 20, "confianca": 5},
            {"afeto_lucian": -10, "confianca": -5}
        ]
    },
    {
        "id": 2,
        "titulo": "O Salão e a Dama de Branco",
        "texto": """Lucian guia você por corredores silenciosos. No salão principal, uma mulher de cabelos negros os espera:
— Elara — apresenta ele, com tom seco — minha irmã. Ela não confia em estranhos.
Elara te avalia com olhos afiados: — A mansão muda quem entra. Você sabe no que está se metendo?""",
        "escolhas": [
            "• Olhar firme: 'Estou aqui pela verdade, não por permissão de ninguém.'",
            "• Curvar levemente a cabeça: 'Espero provar que não sou ameaça.'",
            "• Perguntar direta: 'O que vocês escondem aqui?'"
        ],
        "efeitos": [
            {"afeto_elara": 15, "confianca": 10, "afeto_lucian": -5},
            {"afeto_elara": 5, "confianca": 0, "afeto_lucian": 10},
            {"afeto_elara": -10, "confianca": 15, "afeto_lucian": 5}
        ]
    },
    {
        "id": 3,
        "titulo": "Sussurros no Jardim de Névoa",
        "texto": """No jardim envolto em névoa, uma terceira figura aparece: Morrigan, com olhos cor de âmbar.
— Eles escondem o passado — diz, sem rodeios — e o passado sempre volta.
Eu posso te mostrar o que Lucian e Elara ocultam... mas vai ter um preço.""",
        "escolhas": [
            "• Estender a mão: 'Qual preço? Diga logo.'",
            "• Recuar: 'Não faço acordos com quem não conheço.'",
            "• Perguntar suave: 'Por que você quer me ajudar?'"
        ],
        "efeitos": [
            {"afeto_morrigan": 20, "confianca": -5},
            {"afeto_morrigan": -10, "confianca": 10},
            {"afeto_morrigan": 15, "confianca": 5}
        ]
    },
    {
        "id": 4,
        "titulo": "A Verdade no Topo da Torre",
        "texto": """Subindo a torre, a lua brilha plena e vermelha. Os três estão lá, de lados opostos.
— A escolha é sua — diz Lucian, com voz trêmula — confiar em mim, em Elara, em Morrigan...
ou em nenhum de nós. Qualquer caminho vai deixar cicatrizes. Está pronta?""",
        "escolhas": [
            "• 'Confio em você, Lucian. Não importa o que aconteça.'",
            "• 'Confio em Elara. A honestidade vale mais que afeto.'",
            "• 'Confio em Morrigan. A verdade acima de tudo.'",
            "• 'Confio apenas em mim mesma. Vou descobrir sozinha.'"
        ],
        "efeitos": [
            {"afeto_lucian": 35, "afeto_elara": -10, "afeto_morrigan": -10},
            {"afeto_lucian": -5, "afeto_elara": 30, "afeto_morrigan": -5},
            {"afeto_lucian": -10, "afeto_elara": -5, "afeto_morrigan": 35},
            {"afeto_lucian": 10, "afeto_elara": 10, "afeto_morrigan": 10, "confianca": 20}
        ]
    }
]

# ================== FUNÇÕES VISUAIS ==================
def desenhar_fundo():
    """Desenha imagem da mansão ou fundo alternativo"""
    if imagem_mansao:
        tela.blit(imagem_mansao, (0, 0))  # ✅ Comando da imagem da mansão
    else:
        # Fundo estilo mansão sombria
        for y in range(ALTURA):
            tom = int(8 + (y / ALTURA) * 20)
            pygame.draw.line(tela, (tom, tom // 3, tom + 5), (0, y), (LARGURA, y))
        # Detalhes névoa/chuva
        for _ in range(15):
            x = random.randint(0, LARGURA)
            y = random.randint(0, ALTURA)
            pygame.draw.line(tela, (40, 40, 60), (x, y), (x, y+8), 1)

def desenhar_moldura():
    pygame.draw.rect(tela, ROXO_ESCURO, (10, 10, LARGURA-20, ALTURA-20), 4)
    pygame.draw.rect(tela, VINHO, (18, 18, LARGURA-36, ALTURA-36), 2)

def exibir_texto(texto, cor=PRATA, tamanho=32, x=60, y=150, largura_max=680):
    fonte = pygame.font.Font(None, tamanho)
    linhas = []
    linha_atual = ""
    for palavra in texto.split(" "):
        teste = linha_atual + palavra + " "
        if fonte.size(teste)[0] > largura_max:
            linhas.append(linha_atual)
            linha_atual = palavra + " "
        else:
            linha_atual = teste
    linhas.append(linha_atual)
    y_atual = y
    for linha in linhas:
        texto_render = fonte.render(linha, True, cor)
        tela.blit(texto_render, (x, y_atual))
        y_atual += tamanho + 6
    return y_atual

def barra_relacionamento(nome, valor, x, y, cor):
    tela.blit(fonte_texto.render(nome, True, PRATA), (x, y - 22))
    pygame.draw.rect(tela, CINZA, (x, y, 160, 16))
    if valor >= 0:
        larg = (valor / 100) * 160
        pygame.draw.rect(tela, cor, (x, y, larg, 16))
    else:
        larg = (abs(valor) / 100) * 160
        pygame.draw.rect(tela, (60, 60, 90), (x + 160 - larg, y, larg, 16))

def mostrar_barras():
    barra_relacionamento("Lucian", personagem["afeto_lucian"], 30, 60, VERMELHO_FRACO)
    barra_relacionamento("Elara", personagem["afeto_elara"], 220, 60, DOURADO)
    barra_relacionamento("Morrigan", personagem["afeto_morrigan"], 410, 60, AZUL_PROFUNDO)

# ================== FINAIS ==================
def mostrar_final():
    afeto_l = personagem["afeto_lucian"]
    afeto_e = personagem["afeto_elara"]
    afeto_m = personagem["afeto_morrigan"]
    
    desenhar_fundo()
    desenhar_moldura()
    
    maior = max(afeto_l, afeto_e, afeto_m)
    
    if maior == afeto_l and afeto_l >= 50:
        titulo = "🌙 LAÇO ETERNO — Com Lucian"
        mensagem = """Vocês escolheram um ao outro. Não foi o amor dos contos de fadas —
foi algo mais antigo, mais sombrio e mais forte.
Dois corações feridos encontrando abrigo na mesma escuridão.
A lua testemunhou: nenhum dos dois estará sozinho novamente."""
        cor_final = VERMELHO_FRACO
    elif maior == afeto_e and afeto_e >= 45:
        titulo = "🏰 GUARDIÃ DA VERDADE — Com Elara"
        mensagem = """Elara confiou em você. Juntas, restauraram a honra da família.
A mansão deixou de ser prisão e virou lar.
Não houve juras de amor imediato, mas houve respeito, lealdade...
e um carinho que cresce devagar, como luz rompendo a névoa."""
        cor_final = DOURADO
    elif maior == afeto_m and afeto_m >= 45:
        titulo = "🔮 ALIANÇA DAS SOMBRAS — Com Morrigan"
        mensagem = """Você aceitou o acordo. Morrigan te mostrou tudo — e encontrou
em você algo que julgava ter perdido: confiança.
Caminham juntas por um caminho que nenhum outro conhece:
entre luz e trevas, verdade e segredo, laço e liberdade."""
        cor_final = AZUL_PROFUNDO
    else:
        titulo = "✨ CAMINHO PRÓPRIO"
        mensagem = """Você não escolheu ninguém além de si mesma. Descobriu a verdade,
enfrentou todos e partiu — ou ficou, como dona do seu destino.
Algumas histórias não são feitas para pertencer a mais ninguém.
São feitas para serem vividas por você."""
        cor_final = PRATA
    
    tela.blit(fonte_titulo.render(titulo, True, cor_final), (LARGURA//2 - 200, 40))
    exibir_texto(mensagem, cor=cor_final, tamanho=28, y=140)
    tela.blit(fonte_texto.render("Pressione ESPAÇO para encerrar", True, CINZA), (230, ALTURA - 50))
    pygame.display.flip()
    
    esperando = True
    while esperando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                esperando = False

# ================== LOOP PRINCIPAL ==================
def main():
    cena_atual = 0
    
    while cena_atual < len(cenas):
        cena = cenas[cena_atual]
        escolhida = None
        
        while escolhida is None:
            desenhar_fundo()
            mostrar_barras()
            
            # Título
            tit_render = fonte_titulo.render(cena["titulo"], True, PRATA)
            tela.blit(tit_render, (LARGURA//2 - tit_render.get_width()//2, 30))
            
            # Texto da cena
            fim_texto = exibir_texto(cena["texto"], y=140)
            
            # Escolhas
            y_escolha = fim_texto + 30
            botoes = []
            for i, esc in enumerate(cena["escolhas"]):
                rect = pygame.Rect(60, y_escolha, 680, 45)
                mouse = pygame.mouse.get_pos()
                
                if rect.collidepoint(mouse):
                    pygame.draw.rect(tela, VINHO, rect, border_radius=6)
                    cor = PRATA
                else:
                    pygame.draw.rect(tela, ROXO_ESCURO, rect, border_radius=6)
                    cor = CINZA
                
                txt = fonte_escolha.render(esc, True, cor)
                tela.blit(txt, (80, y_escolha + 10))
                botoes.append(rect)
                y_escolha += 55
            
            # Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    return
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    for idx, bot in enumerate(botoes):
                        if bot.collidepoint(evento.pos):
                            escolhida = idx
            
            desenhar_moldura()
            pygame.display.flip()
            clock.tick(FPS)
        
        # Aplicar efeitos da escolha
        efeito = cena["efeitos"][escolhida]
        for chave, valor in efeito.items():
            if chave in personagem:
                personagem[chave] += valor
                if chave.startswith("afeto_"):
                    personagem[chave] = max(-100, min(100, personagem[chave]))
        
        personagem["capitulo"] += 1
        cena_atual += 1
        time.sleep(0.8)
    
    mostrar_final()
    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()