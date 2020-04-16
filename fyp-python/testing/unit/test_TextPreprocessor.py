import unittest

from helper_classes.TextPreprocessor import TextPreprocessor

class TestPreprocessor(unittest.TestCase):

    def setUp(self):
        self.test_text = "TEST TEXT:\nThis text contains numbers, such as 22, and 10.10, and accented chàráctèrs. Hurray."
        self.preprocessor = TextPreprocessor()

    
    def test_changeToLower(self):
        # Arrange
        expected = "test text:\nthis text contains numbers, such as 22, and 10.10, and accented chàráctèrs. hurray."

        # Act
        actual = self.preprocessor.changeToLower(self.test_text)

        # Assert
        self.assertEqual(expected, actual)

    def test_replaceNewline(self):
        # Arrange
        replacement_char_1 = ""
        expected_1 = "TEST TEXT:This text contains numbers, such as 22, and 10.10, and accented chàráctèrs. Hurray."

        replacement_char_2 = "!"
        expected_2 = "TEST TEXT:!This text contains numbers, such as 22, and 10.10, and accented chàráctèrs. Hurray."

        # Act
        actual_1 = self.preprocessor.replaceNewline(self.test_text, replacement_char_1)
        actual_2 = self.preprocessor.replaceNewline(self.test_text, replacement_char_2)

        # Assert
        self.assertEqual(expected_1, actual_1)
        self.assertEqual(expected_2, actual_2)
        

    def test_removeSpecialChars(self):
        # Arrange
        expected = "TEST TEXTThis text contains numbers such as  and  and accented chrctrs Hurray"

        # Act
        actual = self.preprocessor.removeSpecialChars(self.test_text)

        # Assert
        self.assertEqual(expected, actual)

    def test_stripAccents(self):
        # Arrange
        expected = "TEST TEXT:\nThis text contains numbers, such as 22, and 10.10, and accented characters. Hurray."

        # Act
        actual = self.preprocessor.stripAccents(self.test_text)

        # Assert
        self.assertEqual(expected, actual)

    def test_tokenizeWords(self):
        # Arrange
        expected = ["TEST","TEXT",":","This","text","contains","numbers",",","such","as","22",",","and","10.10",",","and","accented","chàráctèrs",".","Hurray","."]

        # Act
        actual = self.preprocessor.tokenizeWords(self.test_text)

        # Assert
        self.assertEqual(expected, actual)
    
    def test_tokenizeSentences(self): 
        # Arrange
        expected = ["TEST TEXT:\nThis text contains numbers, such as 22, and 10.10, and accented chàráctèrs.", "Hurray."]

        # Act
        actual = self.preprocessor.tokenizeSentences(self.test_text)

        # Assert
        self.assertEqual(expected, actual)

    def test_removeStopWords(self): 
        # Arrange
        expected = "TEST TEXT:\nThis text contains numbers, 22, 10.10, accented chàráctèrs. Hurray."

        # Act
        actual = self.preprocessor.removeStopWords(self.test_text)

        # Assert
        self.assertEqual(expected, actual)

    def test_stemText(self): 
        # Arrange
        expected = "test text : thi text contain number , such as 22 , and 10.10 , and accent chàráctèr . hurray . "

        # Act
        actual = self.preprocessor.stemText(self.preprocessor.tokenizeWords(self.test_text))

        # Assert
        self.assertEqual(expected, actual)

    def test_lemmatizeText(self): 
        # Arrange
        expected = "TEST TEXT : This text contains number , such a 22 , and 10.10 , and accented chàráctèrs . Hurray . "

        # Act
        actual = self.preprocessor.lemmatizeText(self.preprocessor.tokenizeWords(self.test_text))

        # Assert
        self.assertEqual(expected, actual)

    def test_useOriginalWords(self):
        # Arrange
        expected = "TEST TEXT : This text contains numbers , such as 22 , and 10.10 , and accented chàráctèrs . Hurray ."

        # Act
        actual = self.preprocessor.useOriginalWords(self.preprocessor.tokenizeWords(self.test_text))

        # Assert
        self.assertEqual(expected, actual)
