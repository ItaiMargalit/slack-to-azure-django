from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from azure.servicebus import ServiceBusClient, ServiceBusMessage

@csrf_exempt
def send_to_queue(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        try:
            # Parse format: <conn-string>|<queue-name>|<message>
            conn_str, queue_name, message = text.split("|", 2)

            with ServiceBusClient.from_connection_string(conn_str) as client:
                sender = client.get_queue_sender(queue_name=queue_name)
                with sender:
                    sender.send_messages(ServiceBusMessage(message))

            return HttpResponse(f"✅ Sent to queue `{queue_name}`: {message}", status=200)

        except ValueError:
            return JsonResponse({
                "error": "Invalid format. Use: <conn-string>|<queue-name>|<message>"
            }, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
