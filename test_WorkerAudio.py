import unittest
# from unittest.mock import patch
from interfaceCGPT import WorkerAudio
from PyQt5.QtCore import QMutex


class TesteWorkweAudio(unittest.TestCase):
    def setUp(self) -> None:
        self.wA1 = WorkerAudio()
        self.mutex = QMutex()

    def test_signal_fechar(self):
        result: list = []
        self.wA1.fechar.connect(lambda: result.append(1))
        self.wA1.fechar.emit()
        self.assertEqual(result, [1])

    def test_signal_erro(self):
        result: list = []
        self.wA1.erro.connect(lambda text: result.append(text))
        self.wA1.erro.emit('Erro')
        self.assertEqual(result, ['Erro'])

    def test_signal_estadoBtn(self):
        result: list = []
        self.wA1.estadoBtn.connect(lambda valor: result.append(valor))
        self.wA1.estadoBtn.emit(True)
        self.assertEqual(result, [True])

    def test_attr_mutex_lock_e_unlock(self):
        self.assertTrue(self.mutex.tryLock())
        self.assertFalse(self.mutex.tryLock())
        self.mutex.unlock()
        self.assertTrue(self.mutex.tryLock())

    def test_attr_pararAudio_false(self):
        self.assertFalse(self.wA1.pararAudio)

    def test_terminarAudio_muda_attr_true(self):
        self.wA1.terminarAudio()
        self.assertTrue(self.wA1.pararAudio)
        self.wA1.estadoBtn = False

    def test_estadoBnt_continua_false_metodo_run(self):
        result: list = []
        self.wA1.estadoBtn.connect(lambda valor: result.append(valor))
        self.wA1.run()
        self.assertEqual(result, [True, False])


if __name__ == '__main__':
    unittest.main(verbosity=2)
