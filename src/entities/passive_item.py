"""
Classe PassiveItem (Acessório): Define um item que dá um bônus permanente ao Player.
Define o item 'Manto de Ferro' com atributo 'armor' e valor 0.05.
Implementa o método apply_effect(player) que aumenta o atributo 'armor' do player.
"""
class PassiveItem:
    def __init__(self, name, attribute, value, icon_path=None):
        self.name = name
        self.attribute = attribute
        self.value = value
        self.icon_path = icon_path

    def apply_effect(self, player):
        # Adiciona o valor do item (self.value) ao atributo correspondente do player
        if hasattr(player, self.attribute):
            current_value = getattr(player, self.attribute)
            setattr(player, self.attribute, current_value + self.value)

# Lista de todos os itens passivos disponíveis
passives_list = [
    PassiveItem('Manto de Ferro', 'armor', 0.05, icon_path='assets/sprites/Armor.png'),
    PassiveItem('Luva de Força', 'damage_multiplier', 0.25, icon_path='assets/sprites/Gloves.png'),
]
