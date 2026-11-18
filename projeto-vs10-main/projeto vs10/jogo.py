
from pyscript import document, when
from random import randint
import asyncio

# ==================================================
# TABULEIRO E IMAGEM DE FUNDO
# ==================================================

tabuleiro = document.querySelector("#jogo")

tabuleiro.style.backgroundImage = "url('./img/fundo.jpeg')"
tabuleiro.style.backgroundSize = "cover"
tabuleiro.style.backgroundPosition = "center"
tabuleiro.style.backgroundRepeat = "no-repeat"
tabuleiro.style.position = "relative"
tabuleiro.style.overflow = "hidden"


# ==================================================
# ELEMENTOS DA TELA
# ==================================================

jogador = document.querySelector("#jogador")
moeda = document.querySelector("#moeda")
inimigo = document.querySelector("#inimigo")

placar = document.querySelector("#placar")
vidas_tela = document.querySelector("#vidas")
tempo_tela = document.querySelector("#tempo")
fase_tela = document.querySelector("#fase")
mensagem = document.querySelector("#mensagem")

som_moeda = document.querySelector("#somMoeda")
som_colisao = document.querySelector("#somColisao")


# ==================================================
# POSICIONAMENTO DOS PERSONAGENS
# ==================================================

for elemento in [jogador, moeda, inimigo]:
    elemento.style.position = "absolute"

jogador.style.zIndex = "3"
moeda.style.zIndex = "2"
inimigo.style.zIndex = "2"


# ==================================================
# SONS
# ==================================================

def tocar_som(som):
    try:
        som.currentTime = 0
        som.play()
    except Exception:
        pass


# ==================================================
# ESTADO DO JOGO
# ==================================================

game_over = False

x = 100
y = 100

velocidade = 10
velocidade_corrida = 20
correndo = False


def velocidade_atual():
    return velocidade_corrida if correndo else velocidade


def atualizar_jogador():
    jogador.style.left = f"{x}px"
    jogador.style.top = f"{y}px"


def voltar_inicio():
    global x, y

    x = 100
    y = 100

    atualizar_jogador()
    mensagem.innerText = "🔄 Você voltou à posição inicial!"


# ==================================================
# LIMITES DO TABULEIRO
# ==================================================

def limitar_movimento():
    global x, y

    largura = tabuleiro.clientWidth
    altura = tabuleiro.clientHeight

    x = max(0, min(x, largura - jogador.offsetWidth))
    y = max(0, min(y, altura - jogador.offsetHeight))


# ==================================================
# MOEDAS E PONTUAÇÃO
# ==================================================

moeda_x = 300
moeda_y = 200
pontos = 0


def mover_moeda():
    global moeda_x, moeda_y

    largura = tabuleiro.clientWidth
    altura = tabuleiro.clientHeight

    moeda_x = randint(10, max(10, largura - moeda.offsetWidth - 10))
    moeda_y = randint(10, max(10, altura - moeda.offsetHeight - 10))

    moeda.style.left = f"{moeda_x}px"
    moeda.style.top = f"{moeda_y}px"


# ==================================================
# SISTEMA DE FASES
# ==================================================

fase = 1
velocidade_inimigo = 5


def verificar_fase():
    global fase, velocidade_inimigo

    if pontos >= 10:
        nova_fase = 3
        nova_velocidade = 12
    elif pontos >= 5:
        nova_fase = 2
        nova_velocidade = 8
    else:
        nova_fase = 1
        nova_velocidade = 5

    if nova_fase != fase:
        fase = nova_fase
        velocidade_inimigo = nova_velocidade

        fase_tela.innerText = str(fase)

        if fase == 2:
            mensagem.innerText = "🚀 Fase 2! O inimigo está mais rápido!"
        elif fase == 3:
            mensagem.innerText = "🔥 Fase 3! Prepare-se para o desafio!"


# ==================================================
# COLETAR MOEDAS
# ==================================================

def verificar_moeda():
    global pontos

    if game_over:
        return

    distancia_x = abs(x - moeda_x)
    distancia_y = abs(y - moeda_y)

    if distancia_x < 40 and distancia_y < 40:
        pontos += 1
        placar.innerText = str(pontos)

        mensagem.innerText = "🪙 Moeda coletada! +1 ponto!"

        tocar_som(som_moeda)
        mover_moeda()
        verificar_fase()


# ==================================================
# SISTEMA DE VIDAS
# ==================================================

vidas = 3
pode_perder_vida = True


def atualizar_vidas():
    vidas_tela.innerText = str(vidas)


async def liberar_vida():
    global pode_perder_vida

    await asyncio.sleep(1)
    pode_perder_vida = True


def perder_vida():
    global vidas, pode_perder_vida, game_over
    global x, y, correndo

    if not pode_perder_vida or game_over:
        return

    vidas -= 1
    pode_perder_vida = False

    atualizar_vidas()
    tocar_som(som_colisao)

    correndo = False
    jogador.classList.remove("correndo")

    if vidas <= 0:
        game_over = True
        mensagem.innerText = f"💀 GAME OVER! Pontuação final: {pontos}"
    else:
        mensagem.innerText = "💥 Você perdeu uma vida!"

        x = 100
        y = 100

        atualizar_jogador()
        asyncio.create_task(liberar_vida())


# ==================================================
# INIMIGO
# ==================================================

inimigo_x = 500
inimigo_y = 200


def verificar_colisao():
    if game_over:
        return

    distancia_x = abs(x - inimigo_x)
    distancia_y = abs(y - inimigo_y)

    if distancia_x < 40 and distancia_y < 40:
        perder_vida()


def mover_inimigo():
    global inimigo_x

    inimigo_x -= velocidade_inimigo

    if inimigo_x < 0:
        inimigo_x = tabuleiro.clientWidth

    inimigo.style.left = f"{inimigo_x}px"
    inimigo.style.top = f"{inimigo_y}px"

    verificar_colisao()


# ==================================================
# CONTROLE DO TECLADO
# ==================================================

@when("keydown", "body")
def tecla_pressionada(evento):
    global x, y, correndo

    if game_over:
        return

    if evento.key == "Shift":
        correndo = True
        jogador.classList.add("correndo")
        mensagem.innerText = "⚡ Corrida ativada!"
        return

    if evento.key.lower() == "r":
        voltar_inicio()
        return

    passo = velocidade_atual()

    if evento.key == "ArrowRight":
        evento.preventDefault()
        x += passo

    elif evento.key == "ArrowLeft":
        evento.preventDefault()
        x -= passo

    elif evento.key == "ArrowDown":
        evento.preventDefault()
        y += passo

    elif evento.key == "ArrowUp":
        evento.preventDefault()
        y -= passo

    else:
        return

    limitar_movimento()
    atualizar_jogador()
    verificar_moeda()
    verificar_colisao()


# ==================================================
# TECLAS SOLTAS
# ==================================================

@when("keyup", "body")
def tecla_solta(evento):
    global correndo

    if evento.key == "Shift":
        correndo = False
        jogador.classList.remove("correndo")

        if not game_over:
            mensagem.innerText = "🏃 Corrida desativada."


# ==================================================
# CRONÔMETRO
# ==================================================

tempo = 60


async def contar_tempo():
    global tempo, game_over, correndo

    while tempo > 0 and not game_over:
        await asyncio.sleep(1)

        if game_over:
            return

        tempo -= 1
        tempo_tela.innerText = str(tempo)

    if tempo <= 0 and not game_over:
        game_over = True
        correndo = False

        jogador.classList.remove("correndo")

        mensagem.innerText = f"⏰ TEMPO ESGOTADO! Pontuação final: {pontos}"


# ==================================================
# MOVIMENTO AUTOMÁTICO DO INIMIGO
# ==================================================

async def ciclo_inimigo():
    while not game_over:
        mover_inimigo()
        await asyncio.sleep(0.03)


# ==================================================
# INICIALIZAÇÃO DO JOGO
# ==================================================

atualizar_jogador()
atualizar_vidas()

mover_moeda()
verificar_fase()

inimigo.style.left = f"{inimigo_x}px"
inimigo.style.top = f"{inimigo_y}px"

asyncio.create_task(ciclo_inimigo())
asyncio.create_task(contar_tempo())
