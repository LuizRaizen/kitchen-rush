import random

# 1. Bases: tijolos da vida
bases = ['A', 'T', 'C', 'G']

def criar_dna(tamanho):
    """Gera uma sequência aleatória de DNA"""
    return ''.join(random.choice(bases) for _ in range(tamanho))

# 2. Gene: trecho do DNA que guarda uma informação
class Gene:
    def __init__(self, sequencia):
        self.sequencia = sequencia
    
    def expressar(self):
        """Transforma o gene em uma 'função' de vida"""
        instrucoes = {
            'A': 'Iniciar crescimento',
            'T': 'Produzir energia',
            'C': 'Reparar danos',
            'G': 'Adaptar ambiente'
        }
        return [instrucoes[base] for base in self.sequencia]

# 3. Proteína: resultado da expressão dos genes
class Proteina:
    def __init__(self, funcoes):
        self.funcoes = funcoes
    
    def agir(self):
        """Realiza ações que constroem a vida"""
        for funcao in self.funcoes:
            print(f"🧬 {funcao}...")

# 4. Célula: unidade viva
class Celula:
    def __init__(self, dna):
        self.genes = [Gene(dna[i:i+3]) for i in range(0, len(dna), 3)]
        self.proteinas = [Proteina(gene.expressar()) for gene in self.genes]
    
    def viver(self):
        print("✨ Célula acordando para a vida!")
        for proteina in self.proteinas:
            proteina.agir()

# 5. Tecido: conjunto de células
class Tecido:
    def __init__(self, quantidade):
        self.celulas = [Celula(criar_dna(9)) for _ in range(quantidade)]
    
    def funcionar(self):
        print("🔗 Tecido em ação...")
        for celula in self.celulas:
            celula.viver()

# 6. Órgão: grupo de tecidos
class Orgao:
    def __init__(self, quantidade):
        self.tecidos = [Tecido(3) for _ in range(quantidade)]
    
    def operar(self):
        print("❤️ Órgão funcionando harmoniosamente...")
        for tecido in self.tecidos:
            tecido.funcionar()

# 7. Ser Vivo: a grande criação
class SerVivo:
    def __init__(self):
        self.orgaos = [Orgao(2) for _ in range(4)]  # Exemplo: 4 órgãos
    
    def existir(self):
        print("🌟 Um ser vivo surgiu!")
        for orgao in self.orgaos:
            orgao.operar()

# Simulando a criação da vida
if __name__ == "__main__":
    vida = SerVivo()
    vida.existir()
