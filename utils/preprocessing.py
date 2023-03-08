from typing import List


def sample(raw_text: str, paragraphs: List[int] = [2, 4]) -> str:
    """
    sample a combined story by paragrah

    inputs:

    raw_text: combined story parsed by \n# news <story num> \n
    paragraphs: number of paragraphs sampled for each story starting from 1

    outputs:
    cominbed string of sampled text
    """
    combined = ""
    with open(raw_text, "r") as f:
        lines = f.readlines()
        count = 0
        for line in lines:
            if len(line) < 5:
                continue
            if line.startswith("# news"):
                num = line.split()[-1]
                combined += f"\n story {num}"
                count = 0
                continue
            count += 1
            if count in paragraphs:
                combined += f"\n {line}"
    return combined
