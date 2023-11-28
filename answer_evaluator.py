# 점수 채점해서 총점, OX_map, score_map 반환하는 함수
def evaluateAnswer(detected_answer_li, answer_map):
    total_sum_score = 0
    OX_map = dict()
    score_map = dict()

    for number in answer_map.keys():
        now_detected_answer = detected_answer_li[number-1]
        now_correct_answer = answer_map[number]['answer']
        now_points = answer_map[number]['points']

        
        len_now_correct_answer = 1 if type(now_correct_answer) == int else len(now_correct_answer)
        len_now_detected_answer = 1 if type(now_detected_answer) == int else len(now_detected_answer)


        if len_now_correct_answer == 1: # 단수 정답 문항
            if len_now_detected_answer != 1 or now_detected_answer != now_correct_answer:
                OX_map[number] = 'X'
                score_map[number] = 0
            else:
                total_sum_score += now_points
                OX_map[number] = 'O'
                score_map[number] = now_points
        else:                           # 복수 정답 문항
            if len_now_detected_answer != len_now_correct_answer or set(now_detected_answer) != set(now_correct_answer):
                OX_map[number] = 'X'
                score_map[number] = 0
            else:
                total_sum_score += now_points
                OX_map[number] = 'O'
                score_map[number] = now_points
    
    return total_sum_score, OX_map, score_map

    