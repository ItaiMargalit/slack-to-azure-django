from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def send_to_queue(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        logger.warning(f"Received text from Slack: {text!r}")

        try:
            conn_str, queue_name, message = text.split("|", 2)
            logger.warning(f"Parsed: conn_str=..., queue_name={queue_name}, message={message}")

            with ServiceBusClient.from_connection_string(conn_str) as client:
                sender = client.get_queue_sender(queue_name=queue_name)
                with sender:
                    sender.send_messages(ServiceBusMessage(message))

            return HttpResponse(f"✅ Sent to queue `{queue_name}`: {message}", status=200)

        except ValueError:
            logger.error("ValueError: likely bad format in command")
            return JsonResponse({
                "error": "Invalid format. Use: <conn-str>|<queue-name>|<message>"
            }, status=400)

        except Exception as e:
            logger.exception("Unexpected error")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
