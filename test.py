import ace_lib as ace
from auth import get_session

s = get_session()

datasets = ace.get_datasets(s)

print(datasets)
