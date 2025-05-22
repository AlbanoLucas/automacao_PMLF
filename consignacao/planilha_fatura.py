"""
Processador de arquivo CSV para associação de valores entre titulares e dependentes.

Este script lê um arquivo CSV contendo informações de beneficiários de um plano
e associa os valores cobrados dos dependentes (cônjuges e filhos) ao titular.
"""

import csv
import sys
from collections import defaultdict

def processar_csv(arquivo_entrada, arquivo_saida=None):
    """
    Processa o arquivo CSV, associando valores de dependentes aos titulares.
    
    Args:
        arquivo_entrada (str): Caminho para o arquivo CSV de entrada
        arquivo_saida (str, opcional): Caminho para o arquivo CSV de saída
                                      Se não for fornecido, imprime no console
    
    Returns:
        dict: Dicionário com os titulares e seus valores totais
    """
    # Dicionário para armazenar os resultados
    resultados = defaultdict(float)
    
    # Variáveis para controle
    titular_atual = None
    nome_titular_atual = None
    
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as arquivo:
            # Usar o delimitador ponto e vírgula
            leitor_csv = csv.DictReader(arquivo, delimiter=';')
            
            # Verificar se todas as colunas esperadas estão presentes
            colunas_esperadas = [
                'MATRICULA', 'CPF', 'BENEFICIARIO', 'NASCIMENTO', 'INICIO', 
                'IDADE', 'PARENTESCO', 'PLANO', 'AC', 'MENSALIDADE', 
                'ADICIONAL', 'TAXA_ADESAO', 'DESCONTO', ' COBRADO '
            ]
            
            # Verificar se as colunas do arquivo correspondem às esperadas
            if not all(coluna in leitor_csv.fieldnames for coluna in colunas_esperadas):
                print(f"Erro: O arquivo não contém todas as colunas esperadas.")
                print(f"Colunas esperadas: {colunas_esperadas}")
                print(f"Colunas encontradas: {leitor_csv.fieldnames}")
                return None
            
            # Processar cada linha do arquivo
            for linha in leitor_csv:
                parentesco = linha['PARENTESCO'].strip().upper()
                beneficiario = linha['BENEFICIARIO'].strip()
                
                # Tentar converter o valor cobrado para float
                try:
                    valor_cobrado = float(linha[' COBRADO '].replace(',', '.'))
                except (ValueError, AttributeError):
                    print(f"Aviso: Valor inválido para COBRADO na linha do beneficiário {beneficiario}. Usando 0.0")
                    valor_cobrado = 0.0
                
                # Se for um titular, inicia um novo grupo
                if parentesco == 'TITULAR':
                    titular_atual = linha['MATRICULA']
                    nome_titular_atual = beneficiario
                    resultados[titular_atual] = valor_cobrado
                # Se for dependente (cônjuge ou filho), soma ao titular atual
                elif parentesco in ['CONJUGE', 'FILHO', 'FILHA', 'FILHO(A)'] and titular_atual:
                    resultados[titular_atual] += valor_cobrado
                else:
                    print(f"Aviso: Parentesco '{parentesco}' não reconhecido para {beneficiario}")
        
        # Gerar saída
        if arquivo_saida:
            with open(arquivo_saida, 'w', encoding='utf-8', newline='') as saida:
                escritor = csv.writer(saida, delimiter=';')
                escritor.writerow(['MATRICULA', 'BENEFICIARIO', 'VALOR_TOTAL'])
                
                # Obter os dados dos titulares para incluir os nomes
                with open(arquivo_entrada, 'r', encoding='utf-8') as arquivo:
                    leitor_csv = csv.DictReader(arquivo, delimiter=';')
                    titulares = {}
                    for linha in leitor_csv:
                        if linha['PARENTESCO'].strip().upper() == 'TITULAR':
                            titulares[linha['MATRICULA']] = linha['BENEFICIARIO']
                
                # Escrever os resultados
                for matricula, valor_total in resultados.items():
                    nome = titulares.get(matricula, "Nome não encontrado")
                    escritor.writerow([matricula, nome, f"{valor_total:.2f}".replace('.', ',')])
                
                print(f"Resultados salvos em {arquivo_saida}")
        else:
            # Imprimir resultados no console
            print("\nResultados:")
            print("MATRICULA;BENEFICIARIO;VALOR_TOTAL")
            
            # Obter os dados dos titulares para incluir os nomes
            with open(arquivo_entrada, 'r', encoding='utf-8') as arquivo:
                leitor_csv = csv.DictReader(arquivo, delimiter=';')
                titulares = {}
                for linha in leitor_csv:
                    if linha['PARENTESCO'].strip().upper() == 'TITULAR':
                        titulares[linha['MATRICULA']] = linha['BENEFICIARIO']
            
            # Imprimir os resultados
            for matricula, valor_total in resultados.items():
                nome = titulares.get(matricula, "Nome não encontrado")
                print(f"{matricula};{nome};{valor_total:.2f}".replace('.', ','))
        
        return resultados
    
    except FileNotFoundError:
        print(f"Erro: O arquivo {arquivo_entrada} não foi encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao processar o arquivo: {str(e)}")
        return None

def main():
    """Função principal para execução via linha de comando."""
    if len(sys.argv) < 2:
        print("Uso: python processador_csv.py <arquivo_entrada.csv> [arquivo_saida.csv]")
        sys.exit(1)
    
    arquivo_entrada = sys.argv[1]
    arquivo_saida = sys.argv[2] if len(sys.argv) > 2 else None
    
    processar_csv(arquivo_entrada, arquivo_saida)

if __name__ == "__main__":
    main()