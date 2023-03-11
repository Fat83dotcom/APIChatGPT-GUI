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

    def __init__(self, textoUsuario, senha, parent=None) -> None:
        super().__init__(parent)
        self.textoUsuario = textoUsuario
        self.senha = senha

    @pyqtSlot()
    def run(self):
        try:
            diretorioAtual = os.getcwd()
            caminho = os.path.join(diretorioAtual, 'audio.mp3')
            language = 'pt-br'
            openai.api_key = senha

            self.saidaStatus.emit('Pesquisando ...')
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"{self.textoUsuario}"},
                ]
            )

            aud = gTTS(
                text=response.choices[0]['message']['content'],
                lang=language
            )
            aud.save(caminho)
            self.saidaTextoIA.emit(response.choices[0]['message']['content'])
            self.saidaStatus.emit('Pronto!!!')
            self.fechar.emit()
        except Exception as e:
            self.saidaStatus.emit(str(e))
            raise e


class InterfaceGPT(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        super().setupUi(self)

        self.btnPararAudio.setEnabled(False)
        self.btnPesquisar.clicked.connect(self.acaoBtn)
        self.btnLimparTexto.clicked.connect(self.deletarCaixaTexto)
        self.btnPlayAudio.clicked.connect(self.playAudio)
        self.btnPararAudio.clicked.connect(self.paradaAudio)

    def mostrarLabel(self, texto: str) -> None:
        self.resposta.setText(texto)

    def mostrarCaixaTexto(self, texto: str) -> None:
        self.saidaText.setPlainText(texto)

    def obterTextoUsuario(self) -> str:
        return self.entradaUsuario.text()

    def deletarCaixaTexto(self) -> None:
        self.saidaText.setPlainText('')

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
