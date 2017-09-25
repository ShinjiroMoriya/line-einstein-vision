from base64 import b64encode
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from app.models import SfContact
from line.service import jwt_decode
from line.utilities import line_bot_api
from line.line_view import LineCallbackView, View
from linebot.models import (MessageEvent, TextSendMessage, FollowEvent,
                            ImageSendMessage)


class CallbackView(LineCallbackView):
    @staticmethod
    def get(_):
        return HttpResponse()

    def post(self, request):
        try:
            events = self.events_parse(request)
        except:
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
                        if c.premium_distribution_ok is False:
                            SfContact.image_upload_by_line_id(
                                line_id,
                                message_content.content,
                                event.message.id)
                            result = self.predict.base64(
                                b64encode(message_content.content))
                            reply_text = self.get_predict_result(
                                result.get('probabilities'), c)
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(
                                    text=reply_text
                                )
                            )
                        else:
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(
                                    text='ご利用ありがとうございました。'
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
                                    original_content_url=urls.get('original'),
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
                        print(ex)
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
