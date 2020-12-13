
# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.api_client import context
from ask_sdk_core.utils import (
    is_request_type, is_intent_name,
    get_api_access_token, get_device_id)

from ask_sdk_model import Response

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PERMISSIONS = ['alexa::devices:all:geolocation:read']
NOTIFY_MISSING_PERMISSIONS = 'Por favor, activa el permiso de localización en la app de Alexa.'
BIKES_AVAILABLE = "Hay {mechanical} bicis mecánicas y {ebike} eléctricas."""
HELP_REQUEST = "Qué necesitas?"
BYE = "Adios!"
GENERIC_EXCEPTION = "Perdona pero no te acabo de entender"
REFLECTOR = "Acabas de lanzar {}"
NO_ADDRESS = 'It looks like you don\'t have an address set. You can set your address from the companion app.'
ADDRESS_AVAILABLE = 'Here is your full address: {}, {}, {}'
ERROR = 'There was an error with the skill. Please check the logs.'
LOCATION_FAILURE = 'There was an error with the Device Address API.'

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        logger.info(context.System.device.supportedInterfaces.Geolocation)
        speak_output = "Hola, Hay Bicis activado. Puedes preguntarme si hay bicis disponibles."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# class HayBicisIntentHandler(AbstractRequestHandler):
#     """Handler for HayBicis Intent."""
#     def can_handle(self, handler_input):
#         # type: (HandlerInput) -> bool
        
#         return is_intent_name("HayBicis")(handler_input)

#     def handle(self, handler_input):

#         # type: (HandlerInput) -> Response
#         logger.info("In HayBicisIntentHandler")
#         service_client_fact = handler_input.service_client_factory
#         response_builder = handler_input.response_builder

#         if not (get_api_access_token(handler_input)):
#             logger.info("no api access token")
#             response_builder.speak(NOTIFY_MISSING_PERMISSIONS)
#             response_builder.set_card(
#                 AskForPermissionsConsentCard(permissions=PERMISSIONS))
#             return response_builder.response

#         try:
#             device_id = get_device_id(handler_input)
#             device_addr_client = service_client_fact.get_device_address_service()
#             addr = device_addr_client.get_full_address(device_id)

#             logger.info('Location API response retrieved, now building response')
#             logger.info(addr)
#             if addr.address_line1 is None and addr.state_or_region is None:
#                 response_builder.speak(NO_ADDRESS)
#             else:
#                 bikes_available = self.get_bikes(244)
#                 speak_output = bikes_available
                
#                 response_builder.speak(ADDRESS_AVAILABLE.format(
#                     addr.address_line1, addr.state_or_region, addr.postal_code) + speak_output)
#             return response_builder.response
#         except ServiceException as e:
#             logger.error("error reported by device location service")
#             raise e
#         except Exception as e:
#             logger.error(e, exc_info=True)
#             return handler_input.response_builder.speak(ERROR)


#     # def get_closest_bicing_id():
#     #     pass

#     def get_bikes(self, station_id):
#         resp = requests.get("https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status")
#         # station information: https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information
#         # TODO: Remove hardcoded station and pass the argument. Have to find out how to set personal settings in Alexa
#         available_bikes = list(filter(lambda item: item["station_id"] == station_id, resp.json()["data"]["stations"]))[0]["num_bikes_available_types"]
#         return BIKES_AVAILABLE.format(mechanical=available_bikes["mechanical"], ebike=available_bikes["ebike"])

# class HayBicisErrorHandler(AbstractExceptionHandler):
#     """Catch getAddress error handler, log exception and
#     respond with custom message.
#     """
#     def can_handle(self, handler_input, exception):
#         # type: (HandlerInput, Exception) -> bool
#         return (isinstance(exception, ServiceException))

#     def handle(self, handler_input, exception):
#         # type: (HandlerInput, Exception) -> Response
#         logger.info("In GetAddressErrorHandler")
#         logger.error(exception , exc_info=True)

#         if (exception.status_code==403):
#             return (handler_input.response_builder
#                 .speak(NOTIFY_MISSING_PERMISSIONS)
#                 .set_card(
#                     AskForPermissionsConsentCard(permissions=PERMISSIONS))
#                 .response
#             )

#         # not a permissions issue, so just return general failure
#         return (handler_input.response_builder
#             .speak(LOCATION_FAILURE)
#             .response
#         )


# class HelpIntentHandler(AbstractRequestHandler):
#     """Handler for Help Intent."""
#     def can_handle(self, handler_input):
#         # type: (HandlerInput) -> bool
#         return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

#     def handle(self, handler_input):
#         # type: (HandlerInput) -> Response
#         speak_output = "Qué necesitas?"

#         return (
#             handler_input.response_builder
#                 .speak(speak_output)
#                 .ask(speak_output)
#                 .response
#         )


# class CancelOrStopIntentHandler(AbstractRequestHandler):
#     """Single handler for Cancel and Stop Intent."""
#     def can_handle(self, handler_input):
#         # type: (HandlerInput) -> bool
#         return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
#                 ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

#     def handle(self, handler_input):
#         # type: (HandlerInput) -> Response
#         speak_output = "Adios!"

#         return (
#             handler_input.response_builder
#                 .speak(speak_output)
#                 .response
#         )


# class SessionEndedRequestHandler(AbstractRequestHandler):
#     """Handler for Session End."""
#     def can_handle(self, handler_input):
#         # type: (HandlerInput) -> bool
#         return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

#     def handle(self, handler_input):
#         # type: (HandlerInput) -> Response

#         # Any cleanup logic goes here.

#         return handler_input.response_builder.response


# class IntentReflectorHandler(AbstractRequestHandler):
#     """The intent reflector is used for interaction model testing and debugging.
#     It will simply repeat the intent the user said. You can create custom handlers
#     for your intents by defining them above, then also adding them to the request
#     handler chain below.
#     """
#     def can_handle(self, handler_input):
#         # type: (HandlerInput) -> bool
#         return ask_utils.is_request_type("IntentRequest")(handler_input)

#     def handle(self, handler_input):
#         # type: (HandlerInput) -> Response
#         intent_name = ask_utils.get_intent_name(handler_input)
#         speak_output = "Acabas de lanzar " + intent_name + "."

#         return (
#             handler_input.response_builder
#                 .speak(speak_output)
#                 # .ask("add a reprompt if you want to keep the session open for the user to respond")
#                 .response
#         )


# class CatchAllExceptionHandler(AbstractExceptionHandler):
#     """Generic error handling to capture any syntax or routing errors. If you receive an error
#     stating the request handler chain is not found, you have not implemented a handler for
#     the intent being invoked or included it in the skill builder below.
#     """
#     def can_handle(self, handler_input, exception):
#         # type: (HandlerInput, Exception) -> bool
#         return True

#     def handle(self, handler_input, exception):
#         # type: (HandlerInput, Exception) -> Response
#         logger.error(exception, exc_info=True)

#         speak_output = "Perdona pero no te acabo de entender"

#         return (
#             handler_input.response_builder
#                 .speak(speak_output)
#                 .ask(speak_output)
#                 .response
#         )


# # Request and Response loggers
# class RequestLogger(AbstractRequestInterceptor):
#     """Log the alexa requests."""
#     def process(self, handler_input):
#         # type: (HandlerInput) -> None
#         logger.debug("Alexa Request: {}".format(
#             handler_input.request_envelope.request))


# class ResponseLogger(AbstractResponseInterceptor):
#     """Log the alexa responses."""
#     def process(self, handler_input, response):
#         # type: (HandlerInput, Response) -> None
#         logger.debug("Alexa Response: {}".format(response))



sb = CustomSkillBuilder(api_client=DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
# sb.add_request_handler(HayBicisIntentHandler())
# sb.add_request_handler(HelpIntentHandler())
# sb.add_request_handler(CancelOrStopIntentHandler())
# sb.add_request_handler(SessionEndedRequestHandler())
# sb.add_exception_handler(HayBicisErrorHandler())

# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()


