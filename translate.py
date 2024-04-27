import os
import re

symbols = [' ', '(', ')', '[', ']', '-', '{', '}', '%', "'", '"']


class RuneTrieNode:
    def __init__(self):
        self.child = {}
        self.value = None


class RuneTrie:
    def __init__(self):
        self.__root = RuneTrieNode()

    def put_if_absent(self, key: str, value) -> bool:
        if value is None:
            raise ValueError('cannot put a nil value')
        key = key.lower()
        node = self.__root
        for c in key:
            n = node.child.get(c)
            if n:
                node = n
            else:
                new_node = RuneTrieNode()
                node.child[c] = new_node
                node = new_node
        if node.value:
            return False
        node.value = value
        return True

    def __get_longest(self, s: str) -> (str, str):
        node2 = None
        key2 = ''
        node = self.__root
        key = ''
        for idx in range(len(s)):
            c = s[idx]
            n = node.child.get(c.lower())
            if n:
                key += c
                node = n
                if node.value is not None and (idx + 1 >= len(s) or s[idx + 1] in symbols):
                    node2 = node
                    key2 = key
            else:
                break
        if node2:
            return key2, node2.value
        return '', ''

    def replace_all(self, s: str) -> str:
        s2 = ''
        while s:
            if not (len(s2) == 0 or s2[-1] in symbols):
                s2 += s[0]
                s = s[1:]
                continue
            key, value = self.__get_longest(s)
            if key:
                s2 += value
                s = s[len(key):]
            else:
                s2 += s[0]
                s = s[1:]
        return s2


if __name__ == "__main__":

    trie = RuneTrie()

    with open('translate.tsv', 'r', encoding='utf-8') as f:
        f.readline()
        while True:
            line = f.readline().strip()
            if line:
                arr = line.split(',')
                if not trie.put_if_absent(arr[0], arr[1] if len(arr) >= 2 else ''):
                    raise ValueError("repeat: " + line)
            else:
                break

    regexp = re.compile(r'Description\("(.*?)"\)')
    regexp_space = re.compile(r'''(?<![()\[\]{}%'"A-Za-z]) (?![()\[\]{}%'"A-Za-z])''')

    for file_name in os.listdir('../../Cpp/LiveSplit.OriWotW/Logic'):
        if not file_name.startswith("Split") or not file_name.endswith(".cs"):
            continue

        file_name = '../../Cpp/LiveSplit.OriWotW/Logic/' + file_name

        lines = []
        with open(file_name, 'r', encoding='utf-8') as f:
            while True:
                line = f.readline()
                if line:
                    result = regexp.search(line)
                    if result:
                        a = result.group(1)
                        b = regexp_space.sub('', trie.replace_all(a))
                        line = line.replace(a, b, 1)
                    lines.append(line)
                else:
                    break

        with open(file_name, 'w', encoding='utf-8') as f:
            f.writelines(lines)
