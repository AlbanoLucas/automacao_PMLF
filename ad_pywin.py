import win32com.client

def criar_usuario_ad(nome_usuario, sobrenome, login, senha, unidade_organizacional):
    try:
        # Conectar ao Active Directory
        ad = win32com.client.Dispatch('ADsNameSpaces')
        root = ad.GetObject('', 'LDAP://192.168.0.20')
        domain = 'LDAP://' + root.Get('defaultNamingContext')

        # Criar um objeto de conexão com o AD
        adsi = win32com.client.Dispatch('ADsDSOObject')
        connection = adsi.OpenDSObject(domain, 'CN=Albano Lucas Evangelista de Souza,OU=DTIC,OU=SECAD,DC=calf,DC=local', '1122018*', 1)

        # Criar um novo objeto de usuário
        usuario = connection.Create('user', 'CN=' + nome_usuario + ' ' + sobrenome)

        # Definir propriedades do usuário
        usuario.Put('givenName', nome_usuario)  # Nome
        usuario.Put('sn', sobrenome)  # Sobrenome
        usuario.Put('sAMAccountName', login)  # Nome de login
        usuario.Put('userPrincipalName', login + '@calf.local')  # UPN (usuário principal)
        usuario.Put('userAccountControl', 66048)  # 512 significa conta de usuário ativa

        # Definir senha
        usuario.SetInfo()  # Salva as informações
        usuario.SetPassword(senha)

        # Adicionar o usuário à unidade organizacional
        usuario.MoveHere(unidade_organizacional)

        print(f"Usuário {nome_usuario} {sobrenome} criado com sucesso!")

    except Exception as e:
        print(f"Erro ao criar o usuário: {str(e)}")

# Exemplo de uso:
nome_usuario = 'Teste'
sobrenome = 'Teste'
login = 'tteste'
senha = '123@mudar'
unidade_organizacional = 'OU=DTIC,OU=SECAD,DC=calf,DC=local'

criar_usuario_ad(nome_usuario, sobrenome, login, senha, unidade_organizacional)
