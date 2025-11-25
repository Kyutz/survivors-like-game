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
        # Se for a Bota de Mercúrio, soma apenas +0.1 ao atributo de speed
        if self.name == 'Bota de Mercúrio' and self.attribute == 'speed':
            current_value = getattr(player, self.attribute, 0)
            setattr(player, self.attribute, current_value + 0.1)
        elif hasattr(player, self.attribute):
            current_value = getattr(player, self.attribute)
            setattr(player, self.attribute, current_value + self.value)

# Lista de todos os itens passivos disponíveis
passives_list = [
    PassiveItem('Bota de Mercúrio', 'speed', 0.2, icon_path='assets/sprites/Boots.png'),
    PassiveItem('Anel do Aventureiro', 'crit_chance', 0.05, icon_path='assets/sprites/Ring.png'),
    PassiveItem('Essência do Caos', 'amount_multiplier', 1, icon_path='assets/sprites/Essence.png'),
    PassiveItem('Manto de Ferro', 'armor', 0.05, icon_path='assets/sprites/Armor.png'),
    PassiveItem('Luva de Força', 'damage_multiplier', 0.25, icon_path='assets/sprites/Gloves.png'),
    PassiveItem('Tomo Vazio', 'cooldown_multiplier', -0.10, icon_path='assets/sprites/Tome.png'),
]
