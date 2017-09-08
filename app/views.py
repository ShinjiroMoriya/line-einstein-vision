from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from app.models import SfContact, CountException
from line.utilities import line_bot_api
from line.line_view import LineCallbackView
from linebot.models import MessageEvent, TextSendMessage, FollowEvent


class CallbackView(LineCallbackView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
                self.session_create(line_id)

            if isinstance(event, MessageEvent):
                if event.message.type == 'text':
                    message = event.message.text
                    if message == '画像リセット':
                        SfContact.image_reset_by_line_id(line_id)
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(
                                text='回数をリセットしました。'
                            )
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(
                                text='画像をアップロードしてください。'
                            )
                        )

                if event.message.type == 'image':
                    message_content = line_bot_api.get_message_content(
                        event.message.id)

                    try:
                        SfContact.image_upload_by_line_id(
                            line_id, message_content.content, event.message.id)
                        result = self.predict.get(message_content.content)
                        reply_text = self.get_message_reply_by_predict_label(
                            result.get('probabilities'))

                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(
                                text=reply_text
                            )
                        )

                    except CountException as ex:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(
                                text=str(ex)
                            )
                        )
                        return HttpResponse()

                    except:
                        return HttpResponse()

        return HttpResponse()
