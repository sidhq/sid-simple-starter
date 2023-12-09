import json

import sid


def main():
    example = sid.example()
    print(f"Here is an example of what SID can answer for you:\n {example['result']['text']}\n")
    print(f"And here are some useful results that SID returned from your personal files\n")
    result = sid.query(example['result']['text'], query_processing='extended')
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
