import textwrap
from sid import query_sid

from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

def text_operation(text, prompt_template):
    model = ChatOpenAI()
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | model
    return chain.invoke({"text": text}).content

def make_shorter(text):
    prompt_template = "Make the following text shorter:\n\n{text}"
    return text_operation(text, prompt_template)

def make_longer(text):
    prompt_template = "Make the following text longer:\n\n{text}"
    return text_operation(text, prompt_template)

def fix_spelling_and_grammar(text):
    prompt_template = "Fix spelling and grammar in the following text:\n\n {text}"
    return text_operation(text, prompt_template)

def improve_writing(text):
    prompt_template = "Improve the writing of the following text:\n\n {text}"
    return text_operation(text, prompt_template)

def add_context(text):
    context = query_sid(text)
    prompt_template = "Based on what you learn from this:\n\n {context}\n\n Add any relevant context to the following text:\n\n {text}"
    model = ChatOpenAI()
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | model
    return chain.invoke({
        "context": context,
        "text": text
    }).content

def generate_text(prompt):
    response = langchain.generate(prompt, model="gpt-4")
    return response.text

def main():
    choice = input("Do you want to paste existing text or generate new text from scratch? (paste/generate): ")

    if choice == "paste":
        text = input("Paste your text: ")
    else:
        prompt = input("Enter the prompt to generate text from: ")
        text = generate_text(prompt)

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
