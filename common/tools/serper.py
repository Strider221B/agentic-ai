from langchain_community.utilities import GoogleSerperAPIWrapper

class Serper:

    _SERPER = GoogleSerperAPIWrapper()

    @classmethod
    def run(cls, query: str) -> str:
        return cls._SERPER.run(query)