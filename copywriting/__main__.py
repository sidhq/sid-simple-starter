import textwrap
from sid import query_sid
def make_shorter(text):
    # This is a simple way to shorten text by removing every alternate sentence.
    sentences = text.split('.')
    shorter_sentences = [sentences[i] for i in range(len(sentences)) if i % 2 == 0]
    return '.'.join(shorter_sentences)

def make_longer(text):
    # This is a simple way to lengthen text by repeating every sentence.
    sentences = text.split('.')
    longer_sentences = [sentence for sentence in sentences for _ in range(2)]
    return '.'.join(longer_sentences)

def fix_spelling_and_grammar(text):
    # For simplicity, this function doesn't actually fix spelling and grammar.
    # In a real-world scenario, you might integrate with a service like Grammarly or LanguageTool.
    return text

def improve_writing(text):
    # This is a placeholder. In a real-world scenario, you might use advanced NLP techniques.
    return text

def add_context(text):
    # This is a simple way to add context by appending a generic sentence.
    return text + " This is added for context."

def main():
    choice = input("Do you want to paste existing text or generate new text from scratch? (paste/generate): ")

    if choice == "paste":
        text = input("Paste your text: ")
    else:
        text = ""

    while True:
        print("\nCurrent Text:\n", textwrap.fill(text, 80))
        print("\nChoose an option:")
        print("1. Make shorter")
        print("2. Make longer")
        print("3. Fix spelling and grammar")
        print("4. Improve writing")
        print("5. Add context")
        print("6. Exit")

        option = input("Enter your choice (1-6): ")

        if option == "1":
            text = make_shorter(text)
        elif option == "2":
            text = make_longer(text)
        elif option == "3":
            text = fix_spelling_and_grammar(text)
        elif option == "4":
            text = improve_writing(text)
        elif option == "5":
            text = add_context(text)
        elif option == "6":
            break
        else:
            print("Invalid choice. Please choose again.")

if __name__ == "__main__":

    main()
