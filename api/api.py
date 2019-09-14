# =============================================================================
# api.py (new file in risk repo)
# =============================================================================
from risk import battle


def calc_probs(request):
    names = ['a', 'd', 'a_sides', 'd_sides', 'stop']
    kwargs = dict()
    request_json = request.get_json()
    for name in names:
        if request.args and name in request.args:
            kwargs[name] = request.args.get(name)
        elif request_json and name in request_json:
            kwargs[name] = request_json[name]
    else:
        return f'Something went wrong :-('

    return battle.calc_probs(**kwargs).win[-1]


# # =============================================================================
# # main.py (in Cloud Functions)
# # =============================================================================
# from risk import api


# def calc_probs(*args, **kwargs):
#     return api.calc_probs(*args, **kwargs)
