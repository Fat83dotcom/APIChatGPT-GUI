<<<<<<< HEAD
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


=======
# APIChatGPT-GUI v1.2

- Implementação de testes unitários
- Implementaçã de uma tela de login
- Melhoria no controle do som e melhor estabilidade geral da interface
>>>>>>> a818cd8be0f23f78488854a9e40a446a8ffcc54b
