import connection as cn
import pandas as pd
import random

# Constantes de cálculo
LR = 0.1 # Taxa de Aprendizado -  quanto mais alta, mas ele arrisca
DF = 0.6 # Fator de Desconto - importância da recompensa imediata
RF = 18  # Constante de aleatoriedade

# Lista de Movimentos
dict_mov = ['left', 'right', 'jump']

# Funcao para obter a posicao na matriz
def getPosition(string:str)->int:
    n_bloco = int(string[2:7],2)
    sentido = int(string[7:9],2)
    print(f'Plataforma: {n_bloco}, sentido: {sentido}')
    return (n_bloco<<2) + sentido

def getNextMove(bloco, matrix)->float:
    # Verfico se vai fazer uma transicao aleatoria ou não
    if random.randint(0,100) < RF:
        return random.randint(0,2)
    # Pego o maior valor que possuo na tabela para deteminado bloco
    valores_blocos = [matrix[i][bloco] for i in range(3)]
    return valores_blocos.index(max(valores_blocos))

def qLearning(matrix, direcaoAtual, direcaoNova, blocoAtual, blocoNovo)->float:
    return  (matrix[direcaoAtual][blocoAtual] + 
             LR * (reward + DF * matrix[direcaoNova][blocoNovo] - matrix[direcaoAtual][blocoAtual]))

if __name__ == "__main__":
    # Quantidade de Movimentos e Sucessos
    N_LOOPS = 100
    success = 0

    # Setando a plataforma inicial e a posicao
    plataformaAtual, direcaoAtual = 0, 2

    # Lendo a Matriz pré salva
    matrix = pd.read_csv('resultado.txt', header = None, sep=' ')

    # Conectando com o servidor
    appConnect = cn.connect(2037)         

    if appConnect:
        #for i in range(N_LOOPS):
        i = 1
        while success < 10:
            action = dict_mov[direcaoAtual]
            print(60*"-" + f'\nI:{i}, A: {action}')
            # Envio para o servidor a acao escolhida
            state, reward = cn.get_state_reward(appConnect, action)
            # Verifico a nova plataforma que ele está
            plataformaNova = getPosition(state) 
            if reward == 300: success += 1
            direcaoNova = getNextMove(plataformaNova, matrix)
            print(f'next move: {direcaoNova}')
            # Atualizo o valor da matrix para aquele bloco utlizando o calculo QL
            matrix[direcaoAtual][plataformaAtual] = qLearning(matrix, direcaoAtual, direcaoNova, 
                                                              plataformaAtual, plataformaNova)
            # Atualizo as novas direcoes e plataforma
            direcaoAtual, plataformaAtual = direcaoNova, plataformaNova
            i +=1
        
        print(f'total success: {success}')
        matrix.to_csv('resultado.txt', header=None, index=None, mode='w', sep = ' ')
        appConnect.close()