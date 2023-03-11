from PyQt5.QtCore import QThread, QObject, pyqtSignal, QMutex, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
from ui import Ui_MainWindow
from gtts import gTTS
import pygame
import openai
import sys
import os

senhaRaw = None


class WorkerAudio(QObject):
    fechar = pyqtSignal()
    erro = pyqtSignal(str)
    estadoBtn = pyqtSignal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.mutex = QMutex()
        self.pararAudio: bool = False

    @pyqtSlot()
    def terminarAudio(self) -> None:
        self.mutex.lock()
        self.pararAudio = True
        self.mutex.unlock()

    @pyqtSlot()
    def run(self):
        try:
            self.estadoBtn.emit(True)
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load('audio.mp3')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if self.pararAudio:
                    pygame.mixer.music.stop()
            self.estadoBtn.emit(False)
            self.fechar.emit()
        except Exception as e:
            self.erro.emit(str(e))
            raise e


class WorkerGpt(QObject):
    saidaStatus = pyqtSignal(str)
    saidaTextoIA = pyqtSignal(str)
    fechar = pyqtSignal()

    def __init__(self, textoUsuario, parent=None) -> None:
        super().__init__(parent)
        self.textoUsuario = textoUsuario

    def motorGPT(self, senha):
        try:
            openai.api_key = senha
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"{self.textoUsuario}"},
                ]
            )
            return response.choices[0]['message']['content']
        except (openai.error.AuthenticationError, Exception) as e:
            raise e

    def motorGTTS(self, texto, linguagem) -> None:
        diretorioAtual = os.getcwd()
        caminho = os.path.join(diretorioAtual, 'audio.mp3')
        aud = gTTS(
            text=texto,
            lang=linguagem
        )
        aud.save(caminho)

    @pyqtSlot()
    def run(self):
        try:
            language = 'pt-br'

            self.saidaStatus.emit('Pesquisando ...')
            response = self.motorGPT(senhaRaw)

            self.motorGTTS(response, language)

            self.saidaTextoIA.emit(response)
            self.saidaStatus.emit('Pronto!!!')
            self.fechar.emit()
        except Exception as e:
            raise e


class InterfaceGPT(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        super().setupUi(self)

        self.abaPesquisa.setEnabled(False)
        self.btnPararAudio.setEnabled(False)
        self.btnPesquisar.clicked.connect(self.acaoBtn)
        self.btnLimparTexto.clicked.connect(self.deletarCaixaTexto)
        self.btnPlayAudio.clicked.connect(self.playAudio)
        self.btnPararAudio.clicked.connect(self.paradaAudio)
        self.btnSenha.clicked.connect(self.acaoLogin)

    def mostrarLabel(self, texto: str) -> None:
        self.resposta.setText(texto)

    def mostrarCaixaTexto(self, texto: str) -> None:
        self.saidaText.setPlainText(texto)

    def obterTextoUsuario(self) -> str:
        return self.entradaUsuario.text()

    def deletarCaixaTexto(self) -> None:
        self.saidaText.setPlainText('')

    def acaoLogin(self) -> None:
        entradaSenhaUsuario = self.entradaSenha.text()
        if entradaSenhaUsuario == '':
            self.statusLogin.setText("O campo senha não pode estar vazio.")
            self.entradaSenha.setFocus()
        else:
            global senhaRaw
            senhaRaw = entradaSenhaUsuario
            if senhaRaw is not None:
                try:
                    chat = WorkerGpt('Diga boas vindas em uma única linha')
                    resposta = chat.motorGPT(senhaRaw)
                    self.statusLogin.setText(f'{resposta}\nLogin efetuado.')
                    self.abaPesquisa.setEnabled(True)
                    self.btnSenha.setEnabled(False)
                except (openai.error.AuthenticationError, Exception) as e:
                    self.statusLogin.setText(f'{e}')

    def acaoBtn(self) -> None:
        try:
            self.btnPararAudio.setEnabled(False)
            self.textoUsuario = self.obterTextoUsuario()
            self.threadGPT = QThread()
            self.workGpt = WorkerGpt(self.textoUsuario)
            self.workGpt.moveToThread(self.threadGPT)
            self.threadGPT.started.connect(self.workGpt.run)
            self.workGpt.fechar.connect(self.threadGPT.quit)
            self.workGpt.fechar.connect(self.threadGPT.deleteLater)
            self.workGpt.fechar.connect(self.workGpt.deleteLater)
            self.workGpt.saidaStatus.connect(self.mostrarLabel)
            self.workGpt.saidaTextoIA.connect(self.mostrarCaixaTexto)

            self.threadGPT.start()
        except Exception as e:
            self.mostrarLabel(str(e))

    def playAudio(self) -> None:
        try:
            self.threadGPTAudio = QThread()
            self.workGpt = WorkerAudio()
            self.workGpt.moveToThread(self.threadGPTAudio)
            self.threadGPTAudio.started.connect(self.workGpt.run)
            self.workGpt.fechar.connect(self.threadGPTAudio.quit)
            self.workGpt.fechar.connect(self.threadGPTAudio.deleteLater)
            self.workGpt.fechar.connect(self.workGpt.deleteLater)
            self.workGpt.fechar.connect(self.threadGPTAudio.wait)
            self.workGpt.estadoBtn.connect(self.ativarBtnPararAudio)

            self.threadGPTAudio.start()
        except Exception as e:
            self.mostrarLabel(str(e))

    def ativarBtnPararAudio(self, estado) -> None:
        self.btnPararAudio.setEnabled(estado)

    def paradaAudio(self) -> None:
        self.btnPararAudio.setEnabled(False)
        self.workGpt.terminarAudio()
        self.threadGPTAudio.quit()
        self.threadGPTAudio.wait()


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    iu = InterfaceGPT()
    iu.show()
    qt.exec_()
