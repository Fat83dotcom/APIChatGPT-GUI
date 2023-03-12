import openai
import unittest
from unittest.mock import patch
from interfaceCGPT import WorkerGpt


class TesteWorkerGpt(unittest.TestCase):
    def setUp(self) -> None:
        self.wG1 = WorkerGpt('uma frase')

    def test_pyqtSignal_saidaStatus(self):
        result: list = []
        self.wG1.saidaStatus.connect(lambda text: result.append(text))
        self.wG1.saidaStatus.emit('saidaStatus')
        self.assertEqual(result, ['saidaStatus'])

    def test_pyqtSignal_saidaTextoIA(self):
        result: list = []
        self.wG1.saidaTextoIA.connect(lambda text: result.append(text))
        self.wG1.saidaTextoIA.emit('saidaTIA')
        self.assertEqual(result, ['saidaTIA'])

    def test_pyqtSignal_fechar(self):
        result: list = []
        self.wG1.fechar.connect(lambda: result.append(1))
        self.wG1.fechar.emit()
        self.assertEqual(result, [1])

    def test_attr_textoUsurio_foi_recebido_na_instancia(self):
        self.assertEqual(self.wG1.textoUsuario, 'uma frase')

    def test_ausencia_de_senha_openai(self):
        with self.assertRaises(openai.error.AuthenticationError):
            self.wG1.motorGPT('')

    def test_senha_incorreta_openai(self):
        with self.assertRaises(openai.error.AuthenticationError):
            self.wG1.motorGPT('123456')

    def test_retorno_motorGPT_ok(self):
        with patch('openai.ChatCompletion.create') as chat:
            chat.return_value.choices[0]['message']['content'] = str

    def test_geral_metodo_run(self):
        with self.assertRaises(openai.error.AuthenticationError):
            self.wG1.run()


if __name__ == '__main__':
    unittest.main(verbosity=2)
