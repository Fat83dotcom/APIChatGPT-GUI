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
    estadoBtnPesquisar = pyqtSignal(bool)
    estadoBtnLimpar = pyqtSignal(bool)

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
            self.estadoBtnPesquisar.emit(False)
            self.estadoBtnLimpar.emit(False)
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load('audio.mp3')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if self.pararAudio:
                    pygame.mixer.music.stop()
            self.estadoBtn.emit(False)
            self.estadoBtnPesquisar.emit(True)
            self.estadoBtnLimpar.emit(True)
            self.fechar.emit()
        except Exception as e:
            self.erro.emit(str(e))
            raise e


class WorkerGpt(QObject):
    saidaStatus = pyqtSignal(str)
    saidaTextoIA = pyqtSignal(str)
    estadoBtnPlayAudio = pyqtSignal(bool)
    estadoBtnPesquisar = pyqtSignal(bool)
    estadoBtnLimpar = pyqtSignal(bool)
    fechar = pyqtSignal()

    def __init__(self, textoUsuario, parent=None) -> None:
        super().__init__(parent)
        self.textoUsuario = textoUsuario

    def motorGPT(self, senha):
        try:
            openai.api_key = senha
            resposta = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"{self.textoUsuario}"},
                ]
            )
            return resposta.choices[0]['message']['content']
        except (openai.error.AuthenticationError, Exception) as e:
            print(e)
            raise e

    def motorGTTS(self, texto, linguagem) -> None:
        try:
            diretorioAtual = os.getcwd()
            caminho = os.path.join(diretorioAtual, 'audio.mp3')
            aud = gTTS(
                text=texto,
                lang=linguagem
            )
            aud.save(caminho)
        except Exception as e:
            raise e

    @pyqtSlot()
    def run(self):
        try:
            language = 'pt-br'

            self.saidaStatus.emit('Pesquisando ...')
            self.estadoBtnPesquisar.emit(False)
            self.estadoBtnLimpar.emit(False)
            self.estadoBtnPlayAudio.emit(False)
            response = self.motorGPT(senhaRaw)

            self.motorGTTS(response, language)

            self.saidaTextoIA.emit(response)
            self.estadoBtnPesquisar.emit(True)
            self.estadoBtnLimpar.emit(True)
            self.estadoBtnPlayAudio.emit(True)
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
        self.btnPesquisar.clicked.connect(self.pesquisarAPI)
        self.btnLimparTexto.clicked.connect(self.deletarCaixaTexto)
        self.btnPlayAudio.clicked.connect(self.playAudio)
        self.btnPararAudio.clicked.connect(self.paradaAudio)
        self.btnLoginApi.clicked.connect(self.loginAPI)
        self.entradaUsuario.returnPressed.connect(self.pesquisarAPI)
        self.entradaSenha.returnPressed.connect(self.loginAPI)

    def mostrarLabel(self, texto: str) -> None:
        self.resposta.setText(texto)

    def mostrarCaixaTexto(self, texto: str) -> None:
        self.saidaText.setPlainText(texto)

    def obterTextoUsuario(self) -> str:
        return self.entradaUsuario.text()

    def deletarCaixaTexto(self) -> None:
        self.saidaText.setPlainText('')

    def loginAPI(self) -> None:
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
                    self.btnLoginApi.setEnabled(False)
                except (openai.error.AuthenticationError, Exception) as e:
                    self.statusLogin.setText(f'{e}')

    def pesquisarAPI(self) -> None:
        try:
            self.mudarEstadoBtnPararAudio(False)
            self.textoUsuario = self.obterTextoUsuario()
            self.threadGPT = QThread()
            self.workGpt = WorkerGpt(self.textoUsuario)
            self.workGpt.moveToThread(self.threadGPT)
            self.threadGPT.started.connect(self.workGpt.run)

            self.workGpt.fechar.connect(self.threadGPT.quit)
            self.workGpt.fechar.connect(self.workGpt.deleteLater)
            self.workGpt.fechar.connect(self.threadGPT.deleteLater)
            self.workGpt.fechar.connect(self.threadGPT.wait)
            self.workGpt.saidaStatus.connect(self.mostrarLabel)
            self.workGpt.saidaTextoIA.connect(self.mostrarCaixaTexto)
            self.workGpt.estadoBtnPesquisar.connect(
                self.mudarEstadoBtnPesquisar
            )
            self.workGpt.estadoBtnLimpar.connect(self.mudarEstadoBtnLimpar)
            self.workGpt.estadoBtnPlayAudio.connect(
                self.mudarEstadoBtnPlayAudio
            )

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
            self.workGpt.fechar.connect(self.workGpt.deleteLater)
            self.workGpt.fechar.connect(self.threadGPTAudio.deleteLater)
            self.workGpt.fechar.connect(self.threadGPTAudio.wait)
            self.workGpt.estadoBtn.connect(self.mudarEstadoBtnPararAudio)
            self.workGpt.estadoBtnPesquisar.connect(
                self.mudarEstadoBtnPesquisar
            )
            self.workGpt.estadoBtnLimpar.connect(self.mudarEstadoBtnLimpar)

            self.threadGPTAudio.start()
        except Exception as e:
            self.mostrarLabel(str(e))

    def mudarEstadoBtnPlayAudio(self, estado: bool) -> None:
        self.btnPlayAudio.setEnabled(estado)

    def mudarEstadoBtnPararAudio(self, estado: bool) -> None:
        self.btnPararAudio.setEnabled(estado)

    def mudarEstadoBtnPesquisar(self, estado: bool) -> None:
        self.btnPesquisar.setEnabled(estado)

    def mudarEstadoBtnLimpar(self, estado: bool) -> None:
        self.btnLimparTexto.setEnabled(estado)

    def paradaAudio(self) -> None:
        try:
            self.mudarEstadoBtnPararAudio(False)
            self.workGpt.terminarAudio()
            self.threadGPTAudio.quit()
            self.threadGPTAudio.wait()
        except Exception as e:
            raise e


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    iu = InterfaceGPT()
    iu.show()
    qt.exec_()
