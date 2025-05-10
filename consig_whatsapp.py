import pandas as pd
import pywhatkit as kit
import time

# Configurações principais
arquivo_excel = "contatos_servidores.xlsx"
modo_simulacao = False  # True = apenas imprime; False = envia via WhatsApp
delay_entre_envios = 5  # segundos entre mensagens

# 🧠 Carregar Excel (pulando a primeira linha, que não contém cabeçalho)
df = pd.read_excel(arquivo_excel, header=0)  # Header na segunda linha (índice 1)
df = df.fillna('')


# 📝 Função de mensagem personalizada
def gerar_mensagem(nome_servidor):
    return f""" 
    *Prefeitura Municipal de Lauro de Freitas*
    Secretaria de Administração – SECAD
                            
    Prezado(a) Sr.(a) Servidor(a) {nome_servidor};                        
                                
    Assunto: Cobrança de Pagamento Pendente – Plano de Saúde.            
                                
    Informamos que o nosso sistema identificou a ausência do pagamento de algumas mensalidades referente ao seu plano de Saúde contratado - _HAPVIDA_.
                                
    Para regularização do pagamento e o *NÃO CANCELAMENTO* do seu Plano de Saúde, o valor devido será _descontado em folha (contracheque)_ a partir da mensalidade mês do junho de 2025, de forma parcelada, conforme demostrado no próprio contracheque.
                                
    A HAPVIDA reajustou o valor da mensalidade em 40% em janeiro de 2025. Porém, a _Prefeitura negociou este reajuste e conseguiu REDUZIR para 12%_.
                                
    Atenciosamente;                            
    PMLF - Secretaria de Administração-SECAD                    
    Núcleo de CONSIGNAÇÃO
    """.strip()

# 🚀 Envio de mensagem
def enviar_mensagem(numero, mensagem):
    if modo_simulacao:
        print(f"[SIMULAÇÃO] Enviando para {numero}:\n{mensagem}\n{'-'*60}")
    else:
        try:
            kit.sendwhatmsg_instantly(f"+55{int(numero)}", mensagem, wait_time=10, tab_close=True)
            print(f"[ENVIADO] Mensagem enviada para {numero}")
            time.sleep(delay_entre_envios)
        except Exception as e:
            print(f"[ERRO] Falha ao enviar para {numero}: {e}")

# 🔁 Processar cada servidor
for _, linha in df.iterrows():
    nome = str(linha["NOME"]).strip()
    numero = str(linha["TELEFONE"]).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if nome and numero:
        mensagem = gerar_mensagem(nome)
        enviar_mensagem(numero, mensagem)
