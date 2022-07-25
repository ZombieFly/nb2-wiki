
name = 're'


class D:
    def __init__(self, name) -> None:
        self.name = name


wiki_list = [D('q'), D('w'), D('e')]

y = list(
    filter(
        lambda wiki: wiki.name == name,
        wiki_list
    )
)

print(y)

print(
    bool(y)
)
