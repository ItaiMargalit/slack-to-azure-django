import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from azure.servicebus import ServiceBusClient, ServiceBusMessage

SERVICE_BUS_CONNECTION_STRING = os.environ.get("SERVICE_BUS_CONNECTION_STRING")
QUEUE_NAME = os.environ.get("QUEUE_NAME")

@csrf_exempt
def send_to_queue(request):
    if request.method == "POST":
        slack_text = request.POST.get("text", "")
        if not slack_text:
            return JsonResponse({"error": "No text provided"}, status=400)

        try:
            with ServiceBusClient.from_connection_string(SERVICE_BUS_CONNECTION_STRING) as client:
                sender = client.get_queue_sender(queue_name=QUEUE_NAME)
                with sender:
                    sender.send_messages(ServiceBusMessage(slack_text))
            return HttpResponse(f"Message sent to Azure queue: {slack_text}")
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
