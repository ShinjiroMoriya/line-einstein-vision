import os
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings as st
from line.utilities import parser
from line.einstein_vision import Predict
from line.cloudinary import set_image_upload, get_url
from line.service import jwt_encode
import qrcode


class LineCallbackView(View):
    def __init__(self, **kwargs):
        self.predict = Predict()
        super().__init__(**kwargs)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def events_parse(request):
        return parser.parse(
            request.body.decode('utf-8'),
            request.META['HTTP_X_LINE_SIGNATURE'])

    @staticmethod
    def get_predict_result(result_lists, contact):
        result_list = result_lists[0]
        probability = result_list.get('probability', '')

        if result_list.get('probability') > 0.7:
            label = result_list.get('label')
            if label == 'anpanman':
                contact.update(character_01_ok=True)
                return 'アンパンマンです。'
            elif label == 'doraemon':
                contact.update(character_02_ok=True)
                return 'ドラえもんです。'
            elif label == 'kitty':
                contact.update(character_03_ok=True)
                return 'キティーちゃんです。'

            return ''
        else:
            return '画像の認識ができませんでした。(' + str(probability) + ')'

    @staticmethod
    def get_qrcode(line_id):
        line_id_encode = jwt_encode({
            'line_id': line_id
        })
        img = qrcode.make(st.URL + '/qr/' + line_id_encode)
        img_path = os.path.join(st.PROJECT_ROOT, 'qr_img.png')
        img.save(img_path)
        res = set_image_upload(img_path)
        os.remove(img_path)
        return {
            'preview': get_url(res.get('public_id'), sizes={
                'width': 240, 'height': 240}),
            'original': res.get('secure_url'),
        }
