from base64 import b64encode
from django.http import HttpResponse, HttpResponseForbidden
from line.utilities import line_bot_api
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from line.utilities import parser
from line.einstein_vision import Predict
from line.service import logger
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    FollowEvent
)


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
    def get_predict_result(result_lists):
        try:
            result_list = result_lists[0]
            probability = str(result_list.get('probability', ''))
            label = result_list.get('label')

            return f'{label}\n{probability}'

        except Exception as ex:
            logger.info(ex)
            return 'この写真は判断できませんでした。'

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
            # line_id = event.source.sender_id

            if isinstance(event, FollowEvent):
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text='画像を送信してみましょう。'
                    )
                )

            if isinstance(event, MessageEvent):

                if event.message.type == 'text':
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text='画像を送信してください。'
                        )
                    )

                if event.message.type == 'image':
                    message_content = line_bot_api.get_message_content(
                        event.message.id)
                    try:
                        pr = Predict()
                        result = pr.base64(
                            b64encode(message_content.content))
                        reply_text = self.get_predict_result(
                            result.get('probabilities'))
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(
                                text=reply_text
                            )
                        )
                        # line_bot_api.push_message(
                        #     line_id,
                        #     TextSendMessage(
                        #         text='ありがとうございます。'
                        #     )
                        # )

                    except Exception as ex:
                        logger.info(ex)
                        return HttpResponse()

        return HttpResponse()
