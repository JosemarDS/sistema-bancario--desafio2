# ======================================================
# 🏦 SISTEMA BANCÁRIO V3 - Decoradores, Geradores e Iteradores
# Autor: Josemar Joel Damião Sebastião
# ======================================================

from datetime import datetime

# ---------------- DECORADOR DE LOG ---------------- #

def registrar_transacao(func):
    """Decorador para registrar data, hora e tipo da transação."""
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] "
              f"Transação executada: {func.__name__.upper()}")
        return resultado
    return wrapper


# ---------------- FUNÇÕES PRINCIPAIS ---------------- #

@registrar_transacao
def depositar(saldo, valor, extrato, /):
    """Depósito (argumentos posicionais)."""
    if valor > 0:
        saldo += valor
        extrato.append(("Depósito", valor))
        print(f"\n✅ Depósito de R$ {valor:.2f} realizado com sucesso!")
    else:
        print("\n❌ Operação falhou! O valor informado é inválido.")
    return saldo, extrato


@registrar_transacao
def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    """Saque (argumentos nomeados)."""
    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= limite_saques

    if excedeu_saldo:
        print("\n❌ Saldo insuficiente.")
    elif excedeu_limite:
        print("\n❌ Valor excede o limite permitido.")
    elif excedeu_saques:
        print("\n❌ Número máximo de saques atingido.")
    elif valor > 0:
        saldo -= valor
        extrato.append(("Saque", -valor))
        numero_saques += 1
        print(f"\n✅ Saque de R$ {valor:.2f} realizado com sucesso!")
    else:
        print("\n❌ Valor inválido.")
    return saldo, extrato, numero_saques


@registrar_transacao
def criar_conta(agencia, numero_conta, usuarios):
    """Criação de conta vinculada a usuário existente."""
    cpf = input("Informe o CPF do titular: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\n✅ Conta criada com sucesso!")
        return {
            "agencia": agencia,
            "numero_conta": numero_conta,
            "usuario": usuario,
            "saldo": 0,
            "extrato": []
        }

    print("\n❌ Usuário não encontrado. Criação de conta encerrada.")


# ---------------- GERADOR DE RELATÓRIOS ---------------- #

def gerar_relatorio(transacoes, tipo=None):
    """
    Gerador que retorna transações uma a uma.
    Pode filtrar por tipo ('Depósito' ou 'Saque').
    """
    for t in transacoes:
        if tipo is None or t[0].lower() == tipo.lower():
            yield t


# ---------------- ITERADOR PERSONALIZADO ---------------- #

class ContasIterator:
    """Iterador personalizado que percorre todas as contas do banco."""
    def __init__(self, contas):
        self._contas = contas
        self._indice = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._indice < len(self._contas):
            conta = self._contas[self._indice]
            self._indice += 1
            return (conta["numero_conta"],
                    conta["usuario"]["nome"],
                    conta["saldo"])
        raise StopIteration


# ---------------- FUNÇÕES AUXILIARES ---------------- #

def exibir_extrato(saldo, /, *, extrato):
    print("\n================ EXTRATO ================")
    if not extrato:
        print("Não foram realizadas movimentações.")
    else:
        for tipo, valor in extrato:
            print(f"{tipo}: R$ {valor:.2f}")
    print(f"\nSaldo atual: R$ {saldo:.2f}")
    print("==========================================")


def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente números): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\n⚠️ Já existe um usuário com este CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, nº - bairro - cidade/UF): ")

    usuarios.append({
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": endereco
    })
    print("\n✅ Usuário criado com sucesso!")


def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [u for u in usuarios if u["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None


def listar_contas(contas):
    print("\n========== CONTAS CADASTRADAS ==========")
    for numero, nome, saldo in ContasIterator(contas):
        print(f"Conta: {numero} | Titular: {nome} | Saldo: R$ {saldo:.2f}")
    print("========================================")


# ---------------- PROGRAMA PRINCIPAL ---------------- #

def main():
    LIMITE_SAQUES = 3
    AGENCIA = "0001"

    usuarios = []
    contas = []
    numero_conta = 1
    saldo = 0
    limite = 500
    extrato = []
    numero_saques = 0

    menu = """
================ MENU ================
[d] Depositar
[s] Sacar
[e] Extrato
[nu] Novo Usuário
[nc] Nova Conta
[lc] Listar Contas
[r] Relatório de Transações
[q] Sair
=> """

    while True:
        opcao = input(menu).lower()

        if opcao == "d":
            valor = float(input("Valor do depósito: "))
            saldo, extrato = depositar(saldo, valor, extrato)

        elif opcao == "s":
            valor = float(input("Valor do saque: "))
            saldo, extrato, numero_saques = sacar(
                saldo=saldo, valor=valor, extrato=extrato,
                limite=limite, numero_saques=numero_saques,
                limite_saques=LIMITE_SAQUES
            )

        elif opcao == "e":
            exibir_extrato(saldo, extrato=extrato)

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            conta = criar_conta(AGENCIA, numero_conta, usuarios)
            if conta:
                contas.append(conta)
                numero_conta += 1

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "r":
            if not extrato:
                print("\n⚠️ Nenhuma transação registrada.")
                continue
            tipo = input("Filtrar por tipo (Depósito/Saque ou Enter para todos): ")
            print("\n========= RELATÓRIO DE TRANSAÇÕES =========")
            for transacao in gerar_relatorio(extrato, tipo if tipo else None):
                print(f"{transacao[0]}: R$ {transacao[1]:.2f}")
            print("===========================================")

        elif opcao == "q":
            print("\n👋 Encerrando o sistema bancário. Até logo!")
            break

        else:
            print("\n❌ Opção inválida. Tente novamente.")


# Execução
if __name__ == "__main__":
    main()
