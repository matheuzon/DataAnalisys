class Cliente:
    def __init__(self, nome, email, plano):
        self.nome = nome
        self.email = email
        self.lista_planos = ['basic','premium']
        if plano in self.lista_planos:
            self.plano = plano
        else:
            raise Exception('Plano ('+plano+') não existe')

    def mudar_plano(self, plano):
        if plano in self.lista_planos:
            self.plano = plano
        else: 
            raise Exception('Plano ('+plano+') não existe')



cliente = Cliente('Matheus', 'matheus@gmail.com', 'premium')
print(cliente.plano)

cliente.mudar_plano('basisc')
print(cliente.plano)