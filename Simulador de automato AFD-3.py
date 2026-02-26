import time

# ==============================================================================
# UTILITÁRIOS DE INTERFACE
# ==============================================================================
def imprimir_cabecalho(titulo):
    print("\n" + "="*60)
    print(f"{titulo:^60}")
    print("="*60)

def exibir_passo_maquina(fita, posicao_cabecote, estado_atual, transicao_info=None):
    
    # Simula visualmente a Máquina de Estados Finitos (MEF).
   
    # Construção visual da fita
    fita_str = " | ".join(fita)
    fita_visual = f"[ {fita_str} ]"
    
    # Calcular posição do cursor (cabeçote)
    # Cada char ocupa 3 espaços " c ", mais os separadores
    espacos = 2 + (posicao_cabecote * 4) 
    cursor = " " * espacos + "^"
    
    print("\n--- MÁQUINA DE ESTADOS ---")
    print(f"FITA:     {fita_visual}")
    print(f"CABEÇOTE: {cursor}")
    print(f"CONTROL:  Estado Atual: '{estado_atual}'")
    
    if transicao_info:
        print(f"FUNÇÃO:   δ({transicao_info[0]}, '{transicao_info[1]}') -> {transicao_info[2]}")
    else:
        print("FUNÇÃO:   Início do processamento")
    print("-" * 30)
    time.sleep(1) # Pequena pausa para o usuário ver o passo a passo

# ==============================================================================
# CLASSE AFD (Autômato Finito Determinístico)
# ==============================================================================
class AFD:
    def __init__(self, alfabeto, estados, transicoes, estado_inicial, estados_finais):
        self.alfabeto = alfabeto          # Σ
        self.estados = estados            # Q
        self.transicoes = transicoes      # δ
        self.estado_inicial = estado_inicial # q0
        self.estados_finais = estados_finais # F

    def validar_palavra(self, palavra):
        
        # Verificar validade com Fita e Unidade de Controle.
        
        imprimir_cabecalho("VALIDAÇÃO DA PALAVRA (Simulação MEF)")
        
        estado_atual = self.estado_inicial
        fita = list(palavra)
        
        # Passo 0: Estado inicial
        exibir_passo_maquina(fita, 0, estado_atual)
        
        for i, simbolo in enumerate(fita):
            if simbolo not in self.alfabeto:
                print(f"\n[ERRO] Símbolo '{simbolo}' não pertence ao alfabeto Σ.")
                return False

            chave = (estado_atual, simbolo)
            
            # Verifica se a transição existe (Função Total ou Parcial)
            if chave not in self.transicoes:
                print(f"\n[TRAVAMENTO] Não há transição definida para δ({estado_atual}, {simbolo}).")
                return False

            proximo_estado = self.transicoes[chave]
            
            # Exibe o processamento do passo atual
            exibir_passo_maquina(fita, i, estado_atual, (estado_atual, simbolo, proximo_estado))
            
            estado_atual = proximo_estado

        # Resultado Final
        print("\n--- RESULTADO FINAL ---")
        print(f"Estado de Parada: {estado_atual}")
        
        if estado_atual in self.estados_finais:
            print(">>> PALAVRA ACEITA <<<")
            return True
        else:
            print(">>> PALAVRA REJEITADA <<<")
            return False

    def __str__(self):
        return (f"AFD Definido:\n"
                f"  Σ = {self.alfabeto}\n"
                f"  Q = {self.estados}\n"
                f"  q0 = {self.estado_inicial}\n"
                f"  F = {self.estados_finais}")

# ==============================================================================
# CLASSE AFND (Autômato Finito Não-Determinístico)
# ==============================================================================
class AFND:
    def __init__(self, alfabeto, estados, transicoes, estado_inicial, estados_finais):
        self.alfabeto = alfabeto
        self.estados = estados
        self.transicoes = transicoes # Dicionário onde valor é LISTA: ('q0', 'a'): ['q0', 'q1']
        self.estado_inicial = estado_inicial
        self.estados_finais = estados_finais

    def converter_para_afd(self):
        """
        Conversão de AFND para AFD.
        Usa o algoritmo de construção de subconjuntos.
        """
        imprimir_cabecalho("CONVERSÃO AFND -> AFD")
        print("Iniciando algoritmo de subconjuntos...\n")

        # O estado inicial do AFD é o fecho do estado inicial do AFND (simplificado aqui como o próprio set)
        estados_afd_finais = []
        transicoes_afd = {}
        
        # Mapeamento: Frozenset de estados do AFND -> Nome do estado no AFD (S0, S1...)
        estado_inicial_set = frozenset([self.estado_inicial])
        mapa_estados = {estado_inicial_set: "S0"}
        
        fila_processamento = [estado_inicial_set]
        estados_processados = set()
        
        contador_estados = 1
        
        print(f"Estado Inicial AFD (S0) = {{{self.estado_inicial}}}")

        while fila_processamento:
            conjunto_atual = fila_processamento.pop(0)
            nome_atual = mapa_estados[conjunto_atual]
            
            if conjunto_atual in estados_processados:
                continue
            estados_processados.add(conjunto_atual)

            # Verifica se este conjunto é final (se contém algum final do AFND)
            eh_final = any(e in self.estados_finais for e in conjunto_atual)
            if eh_final:
                estados_afd_finais.append(nome_atual)

            # Para cada símbolo do alfabeto, descobre para onde o conjunto vai
            for simbolo in self.alfabeto:
                destinos = set()
                for sub_estado in conjunto_atual:
                    if (sub_estado, simbolo) in self.transicoes:
                        # Adiciona todos os destinos possíveis
                        destinos.update(self.transicoes[(sub_estado, simbolo)])
                
                if not destinos:
                    continue # Transição para vazio (implícito estado de erro/morto)

                destino_frozen = frozenset(destinos)
                
                # Se é um novo conjunto de estados, batiza de S_novo
                if destino_frozen not in mapa_estados:
                    novo_nome = f"S{contador_estados}"
                    mapa_estados[destino_frozen] = novo_nome
                    fila_processamento.append(destino_frozen)
                    contador_estados += 1
                    print(f"  Novo estado descoberto: {novo_nome} = {set(destino_frozen)}")

                nome_destino = mapa_estados[destino_frozen]
                transicoes_afd[(nome_atual, simbolo)] = nome_destino
                print(f"  Transição criada: δ({nome_atual}, {simbolo}) -> {nome_destino}")

        # Monta o objeto AFD resultante
        lista_estados_afd = list(mapa_estados.values())
        
        print("\nConversão concluída com sucesso!")
        return AFD(self.alfabeto, lista_estados_afd, transicoes_afd, "S0", estados_afd_finais)

# ==============================================================================
# FUNÇÕES DE ENTRADA DO USUÁRIO
# ==============================================================================
def criar_afd_usuario():
    imprimir_cabecalho("DEFINIÇÃO DE AFD")
    print("Preencha os dados do Autômato conforme solicitado.")
    
    alfabeto = input("1. Alfabeto (separe por espaços, ex: 0 1): ").strip().split()
    estados = input("2. Estados (separe por espaços, ex: A B C): ").strip().split()
    inicial = input(f"3. Estado Inicial (deve estar em {estados}): ").strip()
    finais = input(f"4. Estados Finais (separe por espaços): ").strip().split()
    
    print("\n5. Definição da Função de Transição (δ):")
    transicoes = {}
    for estado in estados:
        for simbolo in alfabeto:
            destino = input(f"   δ({estado}, {simbolo}) = ").strip()
            # Permite deixar vazio para transição indefinida, ou digitar o estado destino
            if destino in estados:
                transicoes[(estado, simbolo)] = destino
            elif destino == "":
                print("   (Sem transição definida)")
            else:
                print(f"   [AVISO] Estado '{destino}' não existe. Transição ignorada.")

    return AFD(alfabeto, estados, transicoes, inicial, finais)

def criar_afnd_usuario():
    imprimir_cabecalho("DEFINIÇÃO DE AFND [Item 3]")
    print("Nota: No AFND, uma transição pode levar a MÚLTIPLOS estados.")
    
    alfabeto = input("1. Alfabeto (ex: a b): ").strip().split()
    estados = input("2. Estados (ex: q0 q1): ").strip().split()
    inicial = input("3. Estado Inicial: ").strip()
    finais = input("4. Estados Finais: ").strip().split()
    
    print("\n5. Transições (Separe múltiplos destinos por vírgula, ex: q0,q1):")
    transicoes = {}
    for estado in estados:
        for simbolo in alfabeto:
            entrada = input(f"   δ({estado}, {simbolo}) -> ").strip()
            if entrada:
                destinos = entrada.split(',')
                # Validação simples
                destinos_validos = [d.strip() for d in destinos if d.strip() in estados]
                if destinos_validos:
                    transicoes[(estado, simbolo)] = destinos_validos
                else:
                    print("   [AVISO] Nenhum estado válido inserido.")

    return AFND(alfabeto, estados, transicoes, inicial, finais)

# ==============================================================================
# MAIN (Controlador Principal)
# ==============================================================================
def main():
    automato_atual = None
    
    while True:
        imprimir_cabecalho("MENU PRINCIPAL")
        print("1. Definir AFD")
        print("2. Validar Palavra no AFD")
        print("3. Definir AFND e Converter para AFD")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            # Definir AFD pelo usuário 
            automato_atual = criar_afd_usuario()
            print("\nAFD Armazenado com sucesso.")
            print(automato_atual)
            
        elif opcao == "2":
            # Validar w com visualização de Fita/Controle [cite: 15]
            if automato_atual is None:
                print("\n[ERRO] Nenhum AFD definido! Use a opção 1 ou 3 primeiro.")
            else:
                w = input("\nDigite a palavra para validar: ")
                automato_atual.validar_palavra(w)
                
        elif opcao == "3":
            # Definir AFND e Converter 
            afnd = criar_afnd_usuario()
            automato_atual = afnd.converter_para_afd() # O resultado da conversão vira o automato atual
            print("\nO AFD resultante da conversão foi salvo como o autômato atual.")
            
        elif opcao == "0":
            print("Encerrando software...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()