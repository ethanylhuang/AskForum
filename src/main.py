from gemini import Gemini

def main():
    gemini = Gemini()
    response = gemini.generate("Who won the euro 2024?")
    print(response)

if __name__ == "__main__":
    main()
