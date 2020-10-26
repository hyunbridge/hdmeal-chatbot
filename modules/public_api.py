# ██╗  ██╗██████╗ ███╗   ███╗███████╗ █████╗ ██╗
# ██║  ██║██╔══██╗████╗ ████║██╔════╝██╔══██╗██║
# ███████║██║  ██║██╔████╔██║█████╗  ███████║██║
# ██╔══██║██║  ██║██║╚██╔╝██║██╔══╝  ██╔══██║██║
# ██║  ██║██████╔╝██║ ╚═╝ ██║███████╗██║  ██║███████╗
# ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
# Copyright 2019-2020, Hyungyo Seo
# public_api.py - 공개 API 기능을 담당하는 스크립트입니다.

import datetime
from modules.common import get_data, conf


class HDMBadRequestError(Exception):
    pass


classes = int(conf.configs['School']['Classes'])


def webapp(request, req_id: str, debugging: bool):
    try:
        grade, class_ = int(request.args["grade"]), int(request.args['class'])
        if not 3 >= grade >= 1:
            raise HDMBadRequestError('grade must be greater than or equal to 1 and less than or equal to 3')
        if not classes >= class_ >= 1:
            raise HDMBadRequestError('class must be greater than or equal to 1 and less than or equal to %d' % classes)
    except KeyError:
        return {'status': 403, 'message': 'Missing Parameters: grade, class'}, 403
    except ValueError:
        return {'status': 403, 'message': 'Bad Format: grade, class'}, 403
    except HDMBadRequestError as e:
        return {'status': 403, 'message': str(e)}, 403
    try:
        if 'date' in request.args:
            date = [datetime.datetime.strptime(request.args['date'], '%Y-%m-%d')]
        else:
            date_from = datetime.datetime.strptime(request.args['date_from'], '%Y-%m-%d')
            date_to = datetime.datetime.strptime(request.args['date_to'], '%Y-%m-%d')
            delta = (date_to - date_from).days
            if delta > 7:
                raise HDMBadRequestError('Too Long')
            if delta < 0:
                raise HDMBadRequestError('date_from CANNOT be Later than date_to')
            date = [date_from + datetime.timedelta(days=i) for i in range(delta + 1)]
        print(date)
    except KeyError:
        return {'status': 403, 'message': 'Missing Parameters: date or (date_from, date_to)'}, 403
    except ValueError:
        return {'status': 403, 'message': 'Bad Format: date'}, 403
    except HDMBadRequestError as e:
        return {'status': 403, 'message': str(e)}, 403
    output = {}
    for i in date:
        try:
            schedule = get_data.schdl(i.year, i.month, i.day, req_id, debugging)
            if not schedule or schedule == '일정이 없습니다.':
                schedule = None
        except:
            schedule = '서버 오류가 발생했습니다.'
        try:
            menu = get_data.meal(i.year, i.month, i.day, req_id, debugging)['menu']
            if not menu:
                menu = None
        except KeyError:
            menu = None
        except:
            menu = '서버 오류가 발생했습니다.'
        try:
            timetable = get_data.tt(grade, class_, i, req_id, debugging)
            if not timetable or timetable == '등록된 데이터가 없습니다.':
                timetable = None
            else:
                timetable = timetable.split('):\n\n')[1]
        except:
            timetable = '서버 오류가 발생했습니다.'
        output['%04d-%02d-%02d(%s)' % (i.year, i.month, i.day, get_data.wday(i.weekday()))] = {
            'schedule': schedule,
            'menu': menu,
            'timetable': timetable
        }
    return output
