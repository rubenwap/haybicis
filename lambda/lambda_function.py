# -*- coding: utf-8 -*-

import random
import logging

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import (
    is_request_type, is_intent_name,
    get_api_access_token, get_device_id)
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.services import ServiceException
from ask_sdk_model.ui import AskForPermissionsConsentCard

import requests
from geopy.geocoders import Nominatim
import geopy.distance


# =========================================================================================================================================
WELCOME = 'Bienvenido a Hay Bicis. Si vives en Barcelona puedes preguntar si hay bicis disponibles en el bicing mas cercano a tu domicilio.'
NOTIFY_MISSING_PERMISSIONS = 'Por favor activa el permiso de ubicación en la sección mis skills de la app de Alexa en tu móvil.'
NO_ADDRESS = 'Parece que no tienes ninguna dirección configurada en Barcelona. Puedes añadir una desde la app de Alexa en tu móvil.'
ERROR = 'Hubo un error al ejecutar el skill. Por favor mira los logs.'
LOCATION_FAILURE = 'Hubo un fallo con la API de direcciones.'
GOODBYE = 'Adios! Gracias por usar Hay Bicis'
HELP = 'Puedes usar este skill pidiendo a Alexa que le pregunte a la estación de bicing si hay bicis. O más brevemente, pide que mire la estación de bicing.'
AVAILABLE_BIKES = 'En la estación de {} hay {} bicis mecánicas y {} eléctricas.'

# =========================================================================================================================================

PERMISSIONS = ['read::alexa:device:all:address']

# =========================================================================================================================================

sb = CustomSkillBuilder(api_client=DefaultApiClient())
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Built-in Intent Handlers
class HayBicisIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input)
                or (is_intent_name("HayBicis")(handler_input)))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HayBicisIntentHandler")

        service_client_fact = handler_input.service_client_factory
        response_builder = handler_input.response_builder

        if not (get_api_access_token(handler_input)):
            logger.info("no api access token")
            response_builder.speak(NOTIFY_MISSING_PERMISSIONS)
            response_builder.set_card(
                AskForPermissionsConsentCard(permissions=PERMISSIONS))
            return response_builder.response

        try:
            device_id = get_device_id(handler_input)
            device_addr_client = service_client_fact.get_device_address_service()
            addr = device_addr_client.get_full_address(device_id)
            logger.info(addr)
            logger.info('Location API response retrieved, now building response')

            if not addr.city.lower() == "barcelona":
                return handler_input.response_builder.speak(NO_ADDRESS).response
            else:
                
                geolocator = Nominatim(user_agent="hay-bicis")
                address = "{}, Barcelona, {}".format(addr.address_line1, addr.postal_code)
                logger.info(address)
                coordinates = geolocator.geocode(address)
                
                closest = self.get_closest_distance(coordinates.latitude, coordinates.longitude)
                
                bikes_available = self.get_bikes(closest)
            
            return (
            handler_input.response_builder
                .speak(bikes_available)
                .response
                )

        except ServiceException as e:
            logger.error("error reported by device location service")
            raise e
        except Exception as e:
            logger.error(e, exc_info=True)
            return handler_input.response_builder.speak(ERROR)
           
          
    def get_closest_distance(self, lat, lon):
        stations = requests.get("https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information").json()
        stations_w_distance = [{**item, **{'distance_to_user': geopy.distance.distance((lat, lon), (item["lat"], item["lon"])).km}}  for item in stations["data"]["stations"]]
        return sorted(stations_w_distance, key=lambda k: k['distance_to_user'])[0]
        
        
    def get_bikes(self, station):
        resp = requests.get("https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status")
        available_bikes = list(filter(lambda item: item["station_id"] == station["station_id"], resp.json()["data"]["stations"]))[0]["num_bikes_available_types"]
        return AVAILABLE_BIKES.format(station["address"], available_bikes["mechanical"], available_bikes["ebike"])


class HayBicisErrorHandler(AbstractExceptionHandler):
    """Catch HayBicis error handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return (isinstance(exception, ServiceException))

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In HayBicisErrorHandler")
        logger.error(exception , exc_info=True)

        if (exception.status_code==403):
            return (handler_input.response_builder
                .speak(NOTIFY_MISSING_PERMISSIONS)
                .set_card(
                    AskForPermissionsConsentCard(permissions=PERMISSIONS))
                .response
            )

        # not a permissions issue, so just return general failure
        return (handler_input.response_builder
            .speak(LOCATION_FAILURE)
            .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP).ask(HELP)
        return handler_input.response_builder.response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(GOODBYE)
        return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response

# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))

class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(HayBicisIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(HayBicisErrorHandler())

sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()