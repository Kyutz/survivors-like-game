# 🧠 Projeto Final – GAC126 – Programação Aplicada com Suporte de IA

## 📌 Informações do Projeto

**Título do Projeto:** Em Brainstorming  
**Autores:** Thallys Henrique Martins, Andreia José da Silva  
**Curso:** Ciência da Computação  
**Semestre:** 2025-2  
**Professor:** Julio César Alves   
**Departamento:** Departamento de Computação Aplicada (DAC)  

---

## 🎯 Descrição Geral

Este projeto consiste no desenvolvimento de um jogo funcional no estilo survivor-like (ou bullet heaven), com temática de fantasia. O objetivo é aplicar os conhecimentos da disciplina, como decomposição de problemas, engenharia de prompt e uso de APIs. O desenvolvimento é conduzido com o apoio obrigatório de ferramentas de Inteligência Artificial Generativa (como GitHub Copilot, ChatGPT, Gemini, entre outras).

---

## 🏗️ Funcionalidades Principais

Liste as principais funcionalidades implementadas:

- [x] **Ciclo de Combate Funcional:** Movimentação do jogador e spawning de inimigos sequencial por tempo.
- [x] **Armas Variadas:** Implementação de 6 tipos de ataque (Teleguiado, Direcional, AOE, Perfurante).
- [x] **Sistema de Progressão:** Geração/Coleta de XP, Barra de Progresso, e Menu de Level-Up para a seleção de upgrades.
- [x] **Sistema de *Builds*:** Implementação de 6 Itens Passivos (Manto de Ferro, Tomo Vazio, Luva de Poder, etc.) que aplicam multiplicadores globais de Dano, Cooldown e Armadura.
- [x] **Fluxo de Jogo Completo:** Menu Principal, Tela de Instruções, Menu de Pausa e Condição de Game Over.
- [x] **Balanceamento Dinâmico:** Escalonamento de HP e Spawn Rate dos inimigos a cada 30 segundos, ajustando o desafio.

---

## 🤖 Uso da Inteligência Artificial

O uso da IA foi essencial para o desenvolvimento, atuando principalmente como auxiliar de lógica e template de código.

- **Ferramentas utilizadas:** GitHub Copilot e Gemini (para brainstorming e orientação arquitetural).
- **Exemplos de prompts ou instruções que foram úteis:**
    * "Implemente uma função que calcule o dano final causado ao inimigo, levando em conta o multiplicador de dano do jogador (Player.damage_multiplier) e a chance de acerto crítico, retornando o valor ajustado conforme o resultado do crítico." (Usado para a lógica de dano)
    * "Crie a classe Player herdando de pygame.sprite.Sprite, incluindo o método update_movement para movimentação com as teclas WASD." (Usado para lógica inicial)
    * "Implemente uma função para que o inimigo se mova continuamente em direção à posição atual do player, utilizando vetores para calcular a direção e velocidade." (Usado para a lógica de perseguição)
- **Como a IA auxiliou na criação, depuração ou documentação:** A IA acelerou a criação de templates de classes e a implementação de lógicas complexas (perseguição).

### 💬 Reflexão Crítica sobre o Uso de IA

1. **Como a IA foi usada no processo de desenvolvimento?** A IA foi utilizada em diversas etapas do desenvolvimento, desde a geração de trechos de código para funcionalidades específicas até a sugestão de estruturas de classes e organização modular do projeto. Ela auxiliou na decomposição de problemas complexos, na criação de lógicas matemáticas (como movimentação e colisão), na automação de tarefas repetitivas e na documentação de partes do código.
2. **Quais foram os principais benefícios?** Os principais benefícios foram o aumento significativo da produtividade, redução do tempo necessário para implementar funcionalidades, facilidade para testar diferentes soluções e a redução do esforço manual em tarefas rotineiras. O uso da IA permitiu focar mais no design do jogo e no balanceamento, tornando o processo mais eficiente e criativo.
3. **Quais limitações ou dificuldades foram encontradas?** A principal limitação observada foi que a IA, apesar de acelerar a geração de código e sugerir soluções, muitas vezes não compreende totalmente o contexto ou as necessidades específicas do projeto, resultando em sugestões genéricas ou incompatíveis com a arquitetura desejada. Quando isso ocorria, foi necessário ajustar os prompts e solicitar à própria IA que reescrevesse ou adaptasse o código até que atendesse corretamente aos requisitos do projeto.
4. **O que você aprendeu sobre o uso consciente dessas ferramentas?** Aprendemos que o uso consciente de ferramentas de IA exige uma postura ativa e crítica do desenvolvedor. É fundamental revisar, adaptar e compreender cada sugestão gerada, pois a IA serve como apoio, mas não substitui o entendimento profundo do problema e das melhores práticas de desenvolvimento.

---

## ⚙️ Tecnologias Utilizadas

- **Linguagem principal:** Python
- **Bibliotecas / Frameworks:** Pygame, Pytmx (para carregamento de mapa)
- **Outras ferramentas:** GitFlow, Trello (para gestão Kanban)

---

## 🚀 Como Executar o Projeto

**Descreva passo a passo como rodar o projeto localmente:**

1. Clone o repositório:
    ```bash
    git clone https://github.com/Kyutz/survivors-like-game.git
    ```
2. Acesse a pasta do projeto:
    ```bash
    cd survivors-like-game
    ```
3. Crie e ative um ambiente virtual (recomendado):
    ```bash
    python -m venv .venv
    # No Windows: .venv\Scripts\activate
    # No Linux/Mac: source .venv/bin/activate
    ```
4. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
5. Execute o jogo:
    ```bash
    python main.py
    ```

---

## 📅 Organização do Projeto

**Ferramenta de gerenciamento utilizada:** Trello  
**Link para o quadro Kanban:** [Acesse o Quadro Kanban do Trello](https://trello.com/invite/b/68f6a6e676f72616b8e6362d/ATTIa77e0d8c72f730009c17826fe9dc756a68112C66/gac126-pasia-survivors-like-game)

---

## 🎥 Apresentação Final

Inclua aqui o link da gravação, slides ou outro material de apoio (caso aplicável).

---

## 📚 Créditos e Referências

Lista de fontes e *assets* utilizados no desenvolvimento do projeto **Dungeon Survivors**:

### **Assets Visuais (Tileset e Sprites)**

| Tipo de Asset | Fonte / Autor | Link |
| :--- | :--- | :--- |
| **Tileset, Sprites Gerais e Personagens** | Kenney (Tiny Dungeon) | `https://kenney.nl/assets/tiny-dungeon` |
| **Sprites de Itens** | Clockwork Raven (Fantasy Pixel Art Tileset) | `https://clockworkraven.itch.io/raven-fantasy-pixel-art-tileset-the-underworld` |

### **Áudio e Música (SFX e BGM)**

| Tipo de Áudio | Nome / Autor | Link |
| :--- | :--- | :--- |
| **SFX - Bola de Fogo/Tiro** | HighPixel (Fireball) | `https://freesound.org/people/HighPixel/sounds/431174/` |
| **SFX - Machado/Ataque** | smokebomb99 (Axe Throw) | `https://freesound.org/people/smokebomb99/sounds/147289/` |
| **Música Tema (Gameplay)** | Subspace Audio (Dark Quest) | `https://opengameart.org/content/dark-quest` |
| **Música - Game Over** | Subspace Audio (Game Over Theme) | `https://opengameart.org/content/game-over-theme` |
| **Música - Menu Principal** | Subspace Audio (Dark Lands) | `https://opengameart.org/content/dark-lands` |

### **Ferramentas de Apoio**

* **Editor de Mapa:** Tiled Map Editor
* **Biblioteca de Leitura de Mapa:** Pytmx
* **Inspiração de Design:** *Vampire Survivors*, *Brotato*