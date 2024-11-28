import azure.functions as func
import logging
from azure.iot.hub import IoTHubRegistryManager

# Azure IoT Hub connection string
IOTHUB_CONNECTION_STRING = "HostName=icaiiiotlabrmg.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=aSRSN3a0OIokmMo7NxYd/Y6qLBmZ00Ui3AIoTDXNEYE="


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger_commands")

        
def http_trigger_commands(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function received a request.')

    # Extract parameters from the request
    device_id = req.params.get('deviceId')
    message = req.params.get('message')

    if not device_id or not message:
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                "Invalid request. Please provide 'deviceId' and 'message' in query parameters or JSON body.",
                status_code=400
            )
        device_id = req_body.get('deviceId')
        message = req_body.get('message')

    if not device_id or not message:
        return func.HttpResponse(
            "Missing 'deviceId' or 'message'.",
            status_code=400
        )

    try:
        # Create an IoT Hub Registry Manager instance
        registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)

        # Send C2D message to the specified device
        registry_manager.send_c2d_message(device_id, message)
        logging.info(f"C2D message sent to device {device_id}: {message}")

        return func.HttpResponse(f"Message sent to device {device_id}: {message}", status_code=200)
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return func.HttpResponse(f"Failed to send message: {e}", status_code=500)