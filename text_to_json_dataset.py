from argparse import ArgumentParser
from collections import defaultdict
from itertools import chain, repeat
from utils import preprocess_utterance
import json
import os
import random
import shutil

MAX_NUM_CANDIDATES = 19 # Specified in example_entry.py

def convert_text_dataset_to_json(
    text_dataset_path, json_dataset_path, dataset_name, candidate_prefix=">>>"):
    """
    Converts a plaintext conversations file into a json formatted like the personachat dataset.
    The conversations should follow the following format:
    <<< query
    >>> reply
    <<< query
    >>> reply
    [...]
    ====== Conversation separator
    <<< query
    >>> reply
    [...]
    """

    # Gather candidates
    next_candidate = 0
    all_candidates = []
    with open(text_dataset_path, 'r') as fin:
        for line in fin:
            threechars = line[:3]
            line = line[3:].strip()
            if not candidate_prefix or candidate_prefix == threechars:
                all_candidates.append(line)
    random.seed(1234)
    random.shuffle(all_candidates)

    # Create conversations
    conversations = []
    with open(text_dataset_path, 'r') as fin:
        conversation = {"personality": [], "utterances": []}
        history = []

        for line in fin:
            threechars = line[:3]
            line = preprocess_utterance(line[3:])
            if threechars == "===":
                # Conversation delimiter. Finalize conversation
                if conversation["utterances"]:
                    conversations.append(conversation)
                conversation = {"personality": [], "utterances": []}
                history = []
            elif threechars == "<<<":
                # Other speaker
                history.append(line)
            elif threechars == ">>>":
                # Add candidates. Make sure the candidate added isn't the same as the true reply
                utterance = {"candidates": [], "history": []}
                for _ in range(MAX_NUM_CANDIDATES - 1):
                    candidate = None
                    attempts = 0
                    while not candidate or candidate == line or attempts >= len(all_candidates):
                        candidate = all_candidates[(next_candidate + attempts) % len(all_candidates)]
                        attempts += 1
                    next_candidate += attempts
                    utterance["candidates"].append(candidate)
                # Last candidate is our reply
                utterance["candidates"].append(line)
                utterance["history"] = history[:]
                conversation["utterances"].append(utterance)
                history.append(line)

        # Finalize last conversation
        if conversation["utterances"]:
            conversations.append(conversation)

    # Save or resave existing json
    try:
        with open(json_dataset_path, 'r') as fin:
            datasets = json.load(fin)
    except:
        datasets = {"train": [], "valid": []}
    datasets[dataset_name] = conversations
    num_candidates = len(datasets["valid"][0]["utterances"][0]["candidates"])
    print(num_candidates)

    print(f"""Saving "{dataset_name}" dataset to {json_dataset_path}""")
    with open(json_dataset_path, 'w') as fout:
        json.dump(datasets, fout, indent=4, sort_keys=True)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('text_dataset_path', help="path to the source plaintext dataset",
        type=str)
    parser.add_argument('json_dataset_path', help="path to the destination json dataset",
        type=str)
    parser.add_argument('dataset_name', help="name of the dataset: 'train' or 'valid'",
        type=str)
    parser.add_argument('--candidate_prefix', help="use only lines with prefix as candidates",
        nargs='?', default=">>>", type=str)
    args = parser.parse_args()
    assert args.text_dataset_path != args.json_dataset_path

    convert_text_dataset_to_json(
        text_dataset_path=args.text_dataset_path,
        json_dataset_path=args.json_dataset_path,
        dataset_name=args.dataset_name,
        candidate_prefix=args.candidate_prefix,
    )
