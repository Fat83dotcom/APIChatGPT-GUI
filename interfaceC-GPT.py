from PyQt5.QtCore import QThread, QObject, pyqtSignal, QMutex, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
from ui import Ui_MainWindow
import openai
import sys
from gtts import gTTS
from time import sleep
# from playsound import playsound
import pygame
from confidencial import senha


class WorkerAudio(QObject):
    fechar = pyqtSignal()
    erro = pyqtSignal(str)
    def run(self):
        try:
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load('audio.mp3')
            pygame.mixer.music.play()
            
        except Exception as e:
            self.erro.emit(str(e))
            self.fechar.emit()
            raise e

class WorkerGpt(QObject):
    saida = pyqtSignal(str)
    saidaTextoIA = pyqtSignal(str)
    quiti = pyqtSignal()

    def __init__(self, textoUsuario, parent=None) -> None:
        super().__init__(parent)
        self.textoUsuario = textoUsuario

    @pyqtSlot()
    def run(self):
        try:
            audio = 'audio.mp3'
            language = 'pt-br'
            openai.api_key = senha
            self.saida.emit('Pesquisando ...')
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
            aud.save(audio)
            self.saidaTextoIA.emit(response.choices[0]['message']['content'])
            self.saida.emit('Pronto!!!')
            self.quiti.emit()
        except Exception as e:
            self.saida.emit(str(e))
            raise e

        


class InterfaceGPT(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        super().setupUi(self)
        self.btnPesquisar.clicked.connect(self.acaoBtn)
        self.btnLimparTexto.clicked.connect(self.deletarCaixaTexto)
        self.btnPlayAudio.clicked.connect(self.playAudio)
        
    
    def mostrarLabel(self, texto: str)-> None:
        self.resposta.setText(texto)
    
    def mostrarCaixaTexto(self, texto: str)-> None:
        self.saidaText.setPlainText(texto)

    def obterTextoUsuario(self) -> str:
        return self.entradaUsuario.text()
    
    def deletarCaixaTexto(self)-> None:
        self.saidaText.setPlainText('')

    def acaoBtn(self):
        try:
            self.textoUsuario = self.obterTextoUsuario()
            self.threadGPT = QThread()
            self.workGpt = WorkerGpt(self.textoUsuario)
            self.workGpt.moveToThread(self.threadGPT)
            self.threadGPT.started.connect(self.workGpt.run)
            self.workGpt.quiti.connect(self.threadGPT.quit)
            self.workGpt.quiti.connect(self.threadGPT.deleteLater)
            self.workGpt.quiti.connect(self.workGpt.deleteLater)
            self.workGpt.saida.connect(self.mostrarLabel)
            self.workGpt.saidaTextoIA.connect(self.mostrarCaixaTexto)
            # self.btnPararThread.clicked.connect()
            self.threadGPT.start()
        except Exception as e:
            self.mostrarLabel(str(e))

    def playAudio(self):
        try:
            self.threadGPTAudio = QThread()
            self.workGpt = WorkerAudio()
            self.workGpt.moveToThread(self.threadGPTAudio)
            self.threadGPTAudio.started.connect(self.workGpt.run)
            self.workGpt.fechar.connect(self.threadGPTAudio.quit)
            self.workGpt.fechar.connect(self.threadGPTAudio.deleteLater)
            self.workGpt.fechar.connect(self.workGpt.deleteLater)
            self.workGpt.fechar.connect(self.threadGPTAudio.wait)
            self.threadGPTAudio.start()

            self.btnPararAudio.clicked.connect(self.parada)
        except Exception as e:
            self.mostrarLabel(str(e))

    def parada(self):
        self.threadGPTAudio.quit()
        # self.threadGPTAudio.terminate()
        self.threadGPTAudio.wait()
        self.workGpt.deleteLater()
        self.threadGPTAudio.deleteLater()
        # self.workGpt.deleteLater()
    #     # self.workGpt.fechar.connect(self.threadGPT.wait)


if __name__ == '__main__':
    qt = QApplication(sys.argv)
    iu = InterfaceGPT()
    iu.show()
    qt.exec_()