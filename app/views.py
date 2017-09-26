import os
import qrcode
from base64 import b64encode
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from app.models import SfContact
from line.service import jwt_decode
from line.utilities import line_bot_api
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings as st
from line.utilities import parser
from line.einstein_vision import Predict
from line.cloudinary import set_image_upload, get_url
from line.service import jwt_encode, logger
from linebot.models import (MessageEvent, TextSendMessage, FollowEvent,
                            ImageSendMessage)


class CallbackView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def events_parse(request):
        return parser.parse(
            request.body.decode('utf-8'),
            request.META['HTTP_X_LINE_SIGNATURE'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

            logger.info(label_name + '(' + probability + ')')

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
                            ).format(probability=probability)
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
        except Exception as ex:
            logger.info(ex)
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

    @staticmethod
    def get(_):
        return HttpResponse()

    def post(self, request):
        try:
            events = self.events_parse(request)
        except Exception as ex:
            logger.info(ex)
            return HttpResponseForbidden()

        for event in events:
            line_id = event.source.sender_id

            if isinstance(event, FollowEvent):
                SfContact.create(line_id)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text='まずはアストロくんを撮影し、アップロードしてみましょう。'
                    )
                )

            if isinstance(event, MessageEvent):

                c = SfContact.get_by_line_id(line_id)

                if event.message.type == 'text':

                    if event.message.text == 'リセット':
                        c.update(character_01_ok=False,
                                 character_02_ok=False,
                                 character_03_ok=False,
                                 premium_distribution_ok=False)
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(
                                text='リセットしました。'
                            )
                        )

                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(
                                text=('ごめんなさい。\n'
                                      'このLINEチャットBotは、アップロードされた'
                                      '画像をEinstein Visionで解析し、一致した答え'
                                      'を返却する機能をお試しいただけます。\n'
                                      '※講演でお話したような、文字入力による応答機能'
                                      'はついていません。')
                            )
                        )

                if event.message.type == 'image':
                    message_content = line_bot_api.get_message_content(
                        event.message.id)
                    try:
                        if (
                            c.character_01_ok is True and
                            c.character_02_ok is True and
                            c.character_03_ok is True and
                            c.premium_distribution_ok is False
                        ):
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(
                                    text='ご利用ありがとうございました。'
                                )
                            )

                        else:
                            SfContact.image_upload_by_line_id(
                                line_id,
                                message_content.content,
                                event.message.id)
                            pr = Predict()
                            result = pr.base64(
                                b64encode(message_content.content))
                            reply_text = self.get_predict_result(
                                result.get('probabilities'), c)
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(
                                    text=reply_text
                                )
                            )

                        c.reload()

                        if (
                            c.character_01_ok is True and
                            c.character_02_ok is True and
                            c.character_03_ok is True and
                            c.premium_distribution_ok is False
                        ):
                            # urls = self.get_qrcode(line_id)
                            # line_bot_api.push_message(
                            #     line_id,
                            #     ImageSendMessage(
                            #         preview_image_url=urls.get('preview'),
                            #         original_content_url=urls.get('original'),
                            #     )
                            # )
                            urls = self.get_img_urls()
                            line_bot_api.push_message(
                                line_id,
                                ImageSendMessage(
                                    preview_image_url=urls.get('preview'),
                                    original_content_url=urls.get(
                                        'original'),
                                )
                            )

                            line_bot_api.push_message(
                                line_id,
                                TextSendMessage(
                                    text=('おめでとうございます！\n\n'
                                          'ミッションコンプリートです。\n'
                                          'Trailblazer ZoneのTrading Postで'
                                          '景品と交換しましょう。\n'
                                          '受付にこのLINE画面をお見せください。')
                                )
                            )

                    except Exception as ex:
                        logger.info(ex)
                        return HttpResponse()

        return HttpResponse()


class QrcodeView(View):
    @staticmethod
    def get(request, encode_id):
        decode_data = jwt_decode(encode_id)
        if decode_data is None:
            return render(request, 'qrcode_bad_signature.html')

        contact = SfContact.get_by_line_id(decode_data.get('line_id'))

        images = contact.image_path.split('\n')

        data = {
            'contact': contact,
            'images': images,
        }

        if contact.premium_distribution_ok is True:
            data.update({
                'premium_distribution_ok': True,
            })

        return render(request, 'qrcode_confirm.html', {'data': data})

    @staticmethod
    def post(request, encode_id):
        decode_data = jwt_decode(encode_id)
        if decode_data is None:
            return render(request, 'qrcode_bad_signature.html')

        contact = SfContact.get_by_line_id(decode_data.get('line_id'))
        contact.update(premium_distribution_ok=True)

        return redirect('/qr/' + encode_id)
