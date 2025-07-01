from pypdf import PdfReader

class Helpers:

    @staticmethod
    def get_linked_in_details(profile_path: str) -> str:
        reader = PdfReader(profile_path)
        linkedin = ''
        for page in reader.pages:
            text = page.extract_text()
            if text:
                linkedin += text
        return linkedin

    @staticmethod
    def get_summary_at(path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            summary = f.read()
        return summary
