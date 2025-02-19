from imports import *


def carregar_dados():
    # Carregar o arquivo Excel
    df = pd.read_excel("tabela_dados.xlsx")

    # Converter para lista de dicionários
    lista_dicionarios = df.to_dict(orient="records")
    dados_formatados = []
    print(lista_dicionarios)
    for dados in lista_dicionarios:
        nome_completo = dados.get('nome')
        cpf = dados.get('cpf')
        secretaria = dados.get('secretaria')
        setor = dados.get('setor')
        departamento = dados.get('departamento')
        divisao = dados.get('divisao')
        matricula = dados.get('matricula')
        atribuicoes = dados.get('atribuicoes')

        try:
            #Tratamento do nome
            nome = nome_completo.split()

            # Caso o nome tenha apenas nome e sobrenome
            if len(nome) == 2:
                primeiro_nome = nome[0][0].lower()  # Primeira letra do primeiro nome
                segundo_nome = nome[1].lower()  # Segundo nome 
                login_name = f"{primeiro_nome}{segundo_nome}"

            # Caso o nome tenha mais de 2 partes
            elif len(nome) > 2:
                primeiro_nome = nome[0][0].lower()  # Primeira letra do primeiro nome
                segundo_nome = nome[1][0].lower()   # Primeira letra do segundo nome
                ultimo_nome = nome[-1].lower()  # Último nome 
                login_name = f"{primeiro_nome}{segundo_nome}{ultimo_nome}"
        except:
            print("Erro ao gerar login name")
        senha_cad = cpf.replace('.', '').replace('-', '')[:6]
        lista_atribuicoes = []
        for palavra in atribuicoes.split(','):
            lista_atribuicoes.append(palavra) 

        dados_formatados.append({'nome' : nome_completo,
                                'login' : login_name, 
                                'cpf' : cpf,
                                'senha' : senha_cad,
                                'secretaria' : secretaria,
                                'setor' : setor,
                                'departamento' : departamento,
                                'divisao' : divisao,
                                'matricula' : matricula,
                                'atribuicoes' : lista_atribuicoes,
                                })
    
    return(dados_formatados)
