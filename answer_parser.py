import json

from properties import values


def readJsonFile(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def getAnswerMap():
    try:
        data = readJsonFile(values.ANSWER_FILE_PATH)
        answer_map = {int(key): value for key, value in data.items()}
        if answer_map is None:
            raise Exception(f'Cannot Read {values.ANSWER_FILE_PATH}.')
        return answer_map
        

    except FileNotFoundError:
        print(f'[ERROR] Cannot Find {values.ANSWER_FILE_PATH}.')
    except json.JSONDecodeError:
        print(f'[ERROR] Cannot Read {values.ANSWER_FILE_PATH}.')
    except Exception as e:
        print(f'[ERROR] {e}.')