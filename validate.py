from aiohttp import web
import json


def validate_email(mail_):
    # проверка на тип
    if type(mail_) is not str:
        raise web.HTTPConflict(text=json.dumps({'status': 'error',
                                                'message': f'Your email is not string'}),
                               content_type='application/json')
    # email лучше проверять не регуляркой(она огромна), а просто наличием @ и '.' строке (на хабре пишут).
    if not ('@' in mail_ and '.' in mail_):
        raise web.HTTPConflict(text=json.dumps({'status': 'error',
                                                'message': f'Your email {mail_} is incorrect'}),
                               content_type='application/json')


def validate_password(pass_):
    # проверка на тип
    if type(pass_) is not str:
        raise web.HTTPConflict(text=json.dumps({'status': 'error',
                                                'message': f'Your password is not string'}),
                               content_type='application/json')
    # проверка на кол-во символов
    if len(pass_) < 8:
        raise web.HTTPConflict(text=json.dumps({'status': 'error', 'message': 'bad passwords length, less then 8'}),
                               content_type='application/json')


# # Валидация пароля и email для метода patch (email-a или пароля может в запросе и не быть, если их не правим)
async def patch_validate(json_value):
    if json_value.get('email'):
        validate_email(json_value['email'])
    if json_value.get('password'):
        validate_password(json_value['password'])
    return json_value


# Валидация пароля и email для метода post (+проверка на обязательное наличие и email и пароля в запросе)
async def post_validate(json_value):
    # проверка на обязательное наличие почты
    if not json_value.get('email'):
        raise web.HTTPConflict(text=json.dumps({'status': 'error',
                                                'message': f'email is necessary to create user'}),
                               content_type='application/json')
    else:
        validate_email(json_value['email'])
    # проверка обязательное наличие пароля
    if not json_value.get('password'):
        raise web.HTTPConflict(text=json.dumps({'status': 'error',
                                                'message': f'password is necessary to create user'}),
                               content_type='application/json')
    else:
        validate_password(json_value['password'])
    return json_value