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
        try:
            result_list = result_lists[0]
            probability = str(result_list.get('probability', ''))
            label = result_list.get('label')
            if label == 'friend_01':
                label_name = 'アストロくん'
            elif label == 'friend_02':
                label_name = 'きつねくん'
            elif label == 'friend_03':
                label_name = 'きつねくん'
            elif label == 'friend_04':
                label_name = 'いたちくん'
            elif label == 'friend_05':
                label_name = 'うさぎくん'
            else:
                label_name = ''

            if result_list.get('probability') > 0.9:
                if label == 'friend_01':
                    return ('正解！アストロくんです。({probability})\n\n'
                            'これで練習は完了となります。\n\n'
                            'このセッションが終わったら、3匹のぬいぐるみ'
                            '「きつねくん」「いたちくん」「うさぎくん」を'
                            'この会場(Trailblazer Zone)で探して撮影し、'
                            'アップロードしてください。\n\n3匹すべて正解すると、'
                            'Trailblazer ZoneのTrading Postで豪華景品と'
                            '交換ができます。\n'
                            '皆様、是非チャレンジしてください！\n\n'
                            '※景品と交換できるのは先着3名様までとなります。'
                            ).format(probability)
                elif label == 'friend_02':
                    contact.update(character_01_ok=True)
                    return '正解！' + label_name + 'です。(' + probability + ')'
                elif label == 'friend_03':
                    contact.update(character_01_ok=True)
                    return '正解！' + label_name + 'です。(' + probability + ')'
                elif label == 'friend_04':
                    contact.update(character_02_ok=True)
                    return '正解！' + label_name + 'です。(' + probability + ')'
                elif label == 'friend_05':
                    contact.update(character_03_ok=True)
                    return '正解！' + label_name + 'です。(' + probability + ')'
            else:
                return 'この写真は判断できませんでした。'
        except:
            return 'この写真は判断できませんでした。'

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

    @staticmethod
    def get_img_urls():
        return {
            'preview': get_url('trading_post_ezsxiz', sizes={
                'width': 240, 'height': 240}),
            'original': ('https://res.cloudinary.com/hapzui2ny/image/upload/'
                         'v1506310044/trading_post_ezsxiz.png'),
        }
