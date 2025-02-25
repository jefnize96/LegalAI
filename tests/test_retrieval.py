import unittest
from src.retrieval import Retriever

class TestRetrieval(unittest.TestCase):
    def setUp(self):
        self.retriever = Retriever()

    def test_search_by_id(self):
        result = self.retriever.search_by_id("CC-L1-T1-C1-Art.1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "CC-L1-T1-C1-Art.1")

    def test_search_semantic(self):
        results = self.retriever.search_semantic("capacità giuridica")
        self.assertTrue(any("CC-L1-T1-C1-Art.1" in r["id"] for r in results))

if __name__ == "__main__":
    unittest.main()
