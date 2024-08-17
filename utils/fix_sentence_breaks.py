import stanza
import os 


stanza.download('en')       # This downloads the English models for the neural pipeline
nlp = stanza.Pipeline('en') # This sets up a default neural pipeline in English

def fix_sentence_splits(raw_text_dir: str, annotated_dir: str) -> None:
    """
    Fixes sentence splits that aren't present.
    """
    raw_text_dir_files = os.listdir(raw_text_dir)
    annotated_text_dir_files = [os.path.join(annotated_dir, filename + ".tsv") for filename in raw_text_dir_files]
    raw_text_dir_files = [os.path.join(raw_text_dir, filename) for filename in raw_text_dir_files]

    for raw_text, annotated in zip(raw_text_dir_files, annotated_text_dir_files):

        prefix_raw, prefix_annotated = raw_text.split(".")[0], annotated.split(".")[0]
        prefix_raw, prefix_annotated = prefix_raw.split("/")[-1], prefix_annotated.split("/")[-1]

        assert prefix_raw == prefix_annotated, f"raw_text: {raw_text} | annotated: {annotated}"

        fix_single_file_sentences(raw_text, annotated)


def fix_single_file_sentences(text_filepath: str, annotated_filepath: str):
    """
    For each sentence, find the last word of the sentence. 

    For that last word, locate it in the TSV file

    Split the sentence there if it isn't split.
    """

    if not os.path.exists(annotated_filepath) or not os.path.exists(text_filepath):
        print(f"{annotated_filepath} or {text_filepath} doesn't exist. skipping.")
        return 
    print(f"Attempting to apply fixes to file {text_filepath}")
    sentence_endings = []  # Tuples of (3rd to last word, 2nd to last word, last word)
    with open(text_filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        doc = nlp(content)

        for sent in doc.sentences:
            last_word = sent.words[-1].text
            second = ""
            third = ""
            if len(sent.words) >= 2:
                second = sent.words[-2].text
            if len(sent.words) >= 3:
                third = sent.words[-3].text
            sentence_endings.append((third, second, last_word))

    new_lines = []
    with open(annotated_filepath, "r+", encoding="utf-8") as fout:
        lines = fout.readlines()
        cur_ending_seq, num = sentence_endings[0], 0  # which ending seq we are on rn

        third, second, last = cur_ending_seq
        still_searching = True 

        for i, line in enumerate(lines):
            if still_searching:
                cur_ending_seq = sentence_endings[num]
            third, second, last = cur_ending_seq
            if line.startswith(last) and still_searching:  # if we pass number of endings, we are done
                # Attempt to catch all cases where we don't have a true ending
                if second and i - 1 >= 0 and not lines[i - 1].startswith(second):
                    new_lines.append(line)
                    continue 
                if third and i - 2 >= 0 and not lines[i - 2].startswith(third):
                    new_lines.append(line)
                    continue
                # here, we should know that this line is a true ending. We need to add a space if there isn't one. 
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                if next_line != "\n":
                    print(f"Adding a new line at line {i}")
                    new_lines.append(line)
                    new_lines.append("\n")

                else:
                    new_lines.append(line)
                
                num += 1
                if num >= len(sentence_endings):
                    still_searching = False
                    print(f"Searching has been turned off: num = {num}")
            else:
                new_lines.append(line)
    
    with open(annotated_filepath, "w+", encoding="utf-8") as fnew:
        fnew.writelines(new_lines)


if __name__ == "__main__":
    fix_sentence_splits("/Users/alexshan/Desktop/en-worldwide-newswire/original_articles", "/Users/alexshan/Desktop/en-worldwide-newswire/processed_annotated")
