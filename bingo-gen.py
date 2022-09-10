#!/usr/bin/python3
import sys
from copy import deepcopy
import random

from yaml import load, dump, loader
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from tqdm import trange

CSS = """
table, td {
  border: 2px solid black;
  padding: 5px;
  text-align: center;
}

td {
    height: 3em;
}

.questions {
    font-weight: bold;
    background:black;
    font-size:large;
    padding:35px;
}
"""

def generate_file(question_list, answer_list):
    questions = []
    for que in question_list:
        tmp  = [f'\t<span style="color:{v["color"]}">{v["query"]}</span>' for v in que]
        questions.append("<div class='questions'>\n" + "<br/>\n".join(tmp) + "\n</div>")
    page_break = '<div style="page-break-after: always;"></div>\n\n'
    pages      = [head + answer_list[i] + "<br/>\n" + questions[i] + page_break for i in range(num)]
    pages      = f"<style>{CSS}</style>\n\n" + "".join(pages)

    with open("output.html", "w") as f:
        f.write(pages)

def make2d(l):
    return [l[i*size:(i+1)*size] for i in range(size)]

def build_html_table(answers):
    random.shuffle(answers)

    s = "<table width='100%'><tr>"
    for i, ans in enumerate(answers, 1):
        s += f"<td style='background:{ans[1]}'>{ans[0]}</td>"
        if i % size == 0:
            s += "</tr><tr>"
    s += "</tr></table>"
    return s

def choose_answers():
    ans = []

    # choose subset of questions
    v = deepcopy(vals)
    v = random.sample(v, QpS)

    # assign random colors
    c = random.sample(cols, QpS)
    for vv, cc in zip(v,c):
        if 'color' not in vv:
            vv['color'] = cc
    
    for _ in range(size**2 + 1): # easiest upper bound to avoid infinite loop
        for item in v:
            if len(item['answers']) < 1: # skip empty questions
                continue
            answer = random.choice(item['answers'])
            ans.append((answer, item['color']))
            item['answers'].remove(answer)
            if len(ans) >= size**2:
                return v, ans
    else:
        raise RuntimeError("Too less answers to generate bingo field")


if __name__ == "__main__":
    conf_path = sys.argv[1] if len(sys.argv) > 1 else "./config.yml"
    conf = load(open(conf_path), Loader=Loader)

    size = conf['size']
    num  = conf['num']
    vals = conf['questions']
    cols = conf['colors']
    QpS  = conf['questions_per_sheet']
    head = conf['head']
    
    questions = []
    answers   = []
    for _ in trange(num):
        que, ans = choose_answers()
        tab = build_html_table(ans)
        questions.append(que)
        answers.append(tab)
    generate_file(questions, answers)