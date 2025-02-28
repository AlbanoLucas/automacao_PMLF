from ldap3 import Server, Connection, MODIFY_REPLACE

def criar_usuario_ldap(nome_usuario, sobrenome, login,  unidade_organizacional):
    # Configurar o servidor LDAP (Active Directory)
    server = Server('ldap://192.168.0.20', get_info='ALL')
    
    # Estabelecer uma conexão com o servidor LDAP usando credenciais administrativas
    conn = Connection(server, user='CN=Administrador GLPI,OU=DTIC,OU=SECAD,DC=calf,DC=local', password='Dtic@2025.ad.glpi', auto_bind=True)

    # Verifique se a conexão foi bem-sucedida
    if not conn.bound:
        print("Falha na conexão com o Active Directory.")
        return
    
    # Definir o Distinguished Name (DN) para o novo usuário
    dn = f"CN={nome_usuario} {sobrenome},{unidade_organizacional}"
    
    # Definir os atributos do usuário
    atributos = {
        'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
        'sAMAccountName': login,  # Nome de login do usuário (Username)
        'givenName': nome_usuario,  # Nome
        'sn': sobrenome,  # Sobrenome
        'userPrincipalName': f"{login}@calf.local",  # UserPrincipalName (UPN)
        'userAccountControl': 66048,  # Conta ativa + Forçar alteração de senha no primeiro login (512 + 65536)
    }
    
    # Adicionar o novo usuário ao Active Directory
    if conn.add(dn, attributes=atributos):
        print("Usuário adicionado com sucesso!")

        # Codificar a senha corretamente no formato UTF-16
        senha = '"123@mudar"'  # A senha precisa ser passada entre aspas duplas
        senha = senha.encode('utf-16le')  # Codificação UTF-16 Little Endian
        
        # Definir a senha para o novo usuário
        if conn.modify(dn, {'userPassword': [(MODIFY_REPLACE, [senha])]}) and conn.result['result'] == 0:
            print("Senha definida com sucesso!")
        else:
            print(f"Falha ao definir a senha: {conn.last_error}")
            print(f"Erro LDAP: {conn.result}")
        
    else:
        # Detalhamento do erro
        print(f"Falha ao adicionar o usuário: {conn.last_error}")
        print(f"Erro LDAP: {conn.result}")
        print(f"Mensagem: {conn.result['description']}")  # Detalhe da descrição do erro
        print(f"Código de erro: {conn.result['result']}")  # Detalhe do código do erro
    
    # Fechar a conexão
    conn.unbind()

# Exemplo de uso
nome_usuario = 'Teste'
sobrenome = 'Teste'
login = 'tteste'
unidade_organizacional = 'OU=DTIC,OU=SECAD,DC=calf,DC=local'

criar_usuario_ldap(nome_usuario, sobrenome, login,  unidade_organizacional)
