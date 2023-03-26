# APIChatGPT-GUI
-Interface gráfica para Chat GPT desenvolvido em Python

## Empacotando o programa com Pyinstaller:

### Linux:

- Copie o repositório:

    `git clone https://github.com/Fat83dotcom/APIChatGPT-GUI.git`

- Crie um ambiente virtual, ative e instale os pacotes de requirements.txt:
 
    `python3 -m venv venv` (supondo que o virtualenv já esteja intalado no sistema)

    `source ./venv/bin/activate `

    `pip install -r requirements.txt`

- Execute o seguinte comando:

    `pyinstaller -F -w --hidden-import=PyQt5.QtGui --hidden-import=PyQt5.QtCore interfaceCGPT.py -n <nome_do_programa>`

- Após o empacotamento, o programa estará na pasta `dist`.

- Existem outras libs para empacotamento de scripts Python, entretanto, Pyinstaller foi o mais
simples e eficiente que testei e usei.

[Documentação Pyinstaller](https://pyinstaller.org/en/stable/)

# APIChatGPT-GUI v1.2

- Implementação de testes unitários
- Implementaçã de uma tela de login
- Melhoria no controle do som e melhor estabilidade geral da interface

# APIChatGPT-GUI v1.2.1

- Bloqueio de alguns botões de comando enquanto certas operações são reaçizadas
- Diminuição de bugs causados por threads executadas de forma assincrona
- Maior estabilidade da interface 