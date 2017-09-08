from django.views.generic import View
from line.utilities import parser
from line.einstein_vision import Predict
from app.models import SfContact


class LineCallbackView(View):
    def __init__(self, **kwargs):
        self.predict = Predict()
        super().__init__(**kwargs)

    @staticmethod
    def events_parse(request):
        return parser.parse(
            request.body.decode('utf-8'),
            request.META['HTTP_X_LINE_SIGNATURE'])

    @staticmethod
    def get_session(line_id):
        session = SfContact.get_by_line_id(line_id)
        return session if session is not None else {}

    @staticmethod
    def session_create(line_id):
        return SfContact.create(line_id)

    @staticmethod
    def get_message_reply_by_predict_label(result_lists):
        result_list = result_lists[0]
        probability = result_list.get('probability', '')
        if result_list.get('probability') > 0.8:
            return result_list.get('label', '') + '(' + str(probability) + ')'
        else:
            return '画像の認識ができませんでした。(' + str(probability) + ')'
