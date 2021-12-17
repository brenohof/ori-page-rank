from random import random, randint
import sys
import os
import re

def escreve_lista(nomeArquivo, lista):
    lista = dict(sorted(lista.items()))
    arq = open(nomeArquivo, 'w')
    for chave, valor in lista.items():
        arq.write(f'{chave}:')
        for v in valor:
            arq.write(f' {v}')
        arq.write('\n')

if len(sys.argv) <= 1:
    print('Número de argumentos inválido.')
    exit()    

if not os.path.isdir(sys.argv[1]):
    print('O caminho não é um diretório.')
    exit()

# lê o nome dos documentos no diretório
documentos = os.listdir(sys.argv[1])

origem = {doc:set() for doc in documentos}  # grafo de origem
destino = {doc:set() for doc in documentos} # grafo de destino
for doc in documentos:
    arq = open(f'{sys.argv[1]}/{doc}', 'r')
    html = arq.read()
    arq.close()

    links = re.findall(r'(?<=<a href=)".+"', html)
    semAspas = {link.replace('"', '') for link in links}
    validados = {link for link in semAspas if link in documentos and link != doc}

    origem[doc] = {link for link in validados}
    for link in validados:
        destino[link].add(doc)

escreve_lista('links_origem.txt', origem)
escreve_lista('links_destino.txt', destino)

## MÉTODO DE AMOSTRAGEM

TRANSICOES = 10000 # constante de transições
DUMPING = 0.85     # constante de porcentagem de dumping

prob = {doc:0 for doc in documentos} # lista de probabilidades
docInicial = documentos[0] # documento inicial
nDoc = len(documentos)-1 # número de documentos na base
for i in range(0, TRANSICOES):
    if (random() > 1 - DUMPING):
        if len(origem[docInicial]) > 0:
            linksDocCorrente = [d for d in origem[docInicial]]
            qtdLinks = len(linksDocCorrente)-1
            docInicial = linksDocCorrente[randint(0, qtdLinks)]
            prob[docInicial] += 1
        else:
            docInicial = documentos[randint(0, nDoc)]
            prob[docInicial] += 1
    else:
        docInicial = documentos[randint(0, nDoc)]
        prob[docInicial] += 1

prob = {c:[v/TRANSICOES] for c, v in prob.items()}

escreve_lista('pg_amostragem.txt', prob)

## MÉTODO ITERATIVO

nDoc = len(documentos) # número de documentos
prob = {doc:1/nDoc for doc in documentos} 
flag = True # flag de parada da iteração
while flag:
    probCopy = prob.copy() # cópia das probabilidades

    for doc in documentos:
        termo1 = (1-DUMPING)/nDoc
        links = [d for d in destino[doc]]
        termo2 = 0
        for link in links:
            termo2 += prob[link]/len(origem[link])
        prob[doc] = termo1 + (DUMPING * termo2)

    prob = {doc:prob[doc]/sum(prob.values()) for doc in documentos}
    for doc in documentos:
        if abs(probCopy[doc] - prob[doc]) <= 10**(-6):
            flag = False
            break

prob = {c:[v] for c, v in prob.items()}

escreve_lista('pg_iterativo.txt', prob)