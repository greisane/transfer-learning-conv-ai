from argparse import ArgumentParser
from utils import PERSONACHAT_URL, preprocess_utterance
import colorama as con
import json
import re

SEPARATOR = "=" * 40

def sanitize(text):
    parts = re.split(r"([!?.,:;])", text.lower())
    return ' '.join(s.strip() for s in parts if s)

def print_line(text, end='\n'):
    print(text + " " * (80 - len(text)), end=end)

def print_history(conversation, i):
    past_line = conversation[i]
    next_line = conversation[i+1] if i+1 < len(conversation) else ""
    print_line(f"{con.Style.NORMAL}<<< {past_line}")
    print_line(f">>> ")
    print_line(f"<<< {next_line}")
    print_line(f"{con.Style.BRIGHT}{con.Cursor.UP(2)}>>> ", end='\r')

def redo_input():
    print(con.Cursor.UP(2), end='')

def get_source_dataset_conversations(source_dataset_path):
    """Parses a personachat dataset for chat lines."""
    from transformers import cached_path

    source_dataset_path = source_dataset_path or PERSONACHAT_URL
    print(f"Using dataset at {source_dataset_path}")
    source_dataset_path = cached_path(source_dataset_path)
    with open(source_dataset_path, 'r', encoding='utf-8') as fin:
        dataset = json.load(fin)

    def get_personachat_history(conversation):
        utterances = conversation["utterances"]
        for utterance in utterances:
            history = utterance["history"]
            if len(history) > 1:
                yield utterance["history"][-2]
            yield utterance["history"][-1]

    conversations = []
    for conversation in dataset["valid"]:
        conversations.append(list(get_personachat_history(conversation)))

    print(f"Grabbed {sum(len(l) for l in conversations)} total personachat history lines "
        f"from {len(conversations)} conversations")

    return conversations

def interactive_input_dataset(text_dataset_path, source_dataset_path, start_index=0):

    conversations = iter(get_source_dataset_conversations(source_dataset_path)[start_index:])
    con.init()

    with open(text_dataset_path, 'a') as fout:
        last_printed = None
        def print_file(text):
            nonlocal last_printed
            if last_printed is SEPARATOR and text is SEPARATOR:
                return
            last_printed = text
            print(text, file=fout)

        i = 0
        conversation = []
        while True:
            if not conversation or i >= len(conversation):
                print_line(SEPARATOR)
                print_file(SEPARATOR)
                try:
                    conversation = next(conversations)
                except StopIteration:
                    print("No more conversations")
                    return
                i = 0

            print_history(conversation, i)
            try:
                inp = input(">>> ")
                if not inp:
                    # No response, fetch next line
                    redo_input()
                    i += 1
                elif inp.startswith("<"):
                    # Modify current speaker line
                    redo_input()
                    conversation[i] = preprocess_utterance(inp[1:])
                elif inp.startswith(":"):
                    # Add note to file
                    redo_input()
                    print_file(f":::::: " + inp[1:])
                    fout.flush()
                else:
                    print_file("<<< " + conversation[i])
                    print_file(">>> " + preprocess_utterance(inp))
                    fout.flush()
                    i += 1
            except EOFError:
                # Move on to next conversation
                conversation = []

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('text_dataset_path', help="path to the plaintext dataset to append to",
        type=str)
    parser.add_argument('--source_dataset_path', help="path to dataset to take conversations from",
        default="", type=str)
    parser.add_argument('--start', help="skips forward a number of conversations",
        default=0, type=int)
    args = parser.parse_args()

    interactive_input_dataset(
        text_dataset_path=args.text_dataset_path,
        source_dataset_path=args.source_dataset_path,
        start_index=args.start,
    )
