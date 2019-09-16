# =============================================================================
# api.py (new file in risk repo)
# =============================================================================
from risk import battle


def calc_probs(request):

    print('running API')
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    print(request)
    print(request.get_json())
    print(type(request))
    print(dir(request))
    print(request.args)
    print(request.data)
    print(request.content_type)

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
