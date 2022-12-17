import math


from allpress.settings import EQUATORIAL_CIRCUMFERENCE, MERIDIONAL_CIRCUMFERENCE, VALID_UNITS
from allpress.exceptions import CoordinateError, UnitError

from googletrans import Translator
from country_converter import convert
import geopy


def _calculate_chord_length(r: float, d: float) -> float:
    return 2.0 * math.sqrt((r ** 2) - (d ** 2))


def _long_to_miles(latitude: float, degrees=1):
    equatorial_radius = (EQUATORIAL_CIRCUMFERENCE/math.pi) / 2.0
    meridional_semicircle = MERIDIONAL_CIRCUMFERENCE / 4.0
    distance_to_latitude_from_equator = meridional_semicircle * (latitude/90.0)
    subcircle_diameter = _calculate_chord_length(equatorial_radius, distance_to_latitude_from_equator)
    subcircle_circumference = (math.pi * subcircle_diameter)
    return (subcircle_circumference / 360.0) * degrees


def _mile_to_long(latitude: float, miles: float) -> float:
    equatorial_radius = (EQUATORIAL_CIRCUMFERENCE/math.pi) / 2.0
    meridional_semicircle = MERIDIONAL_CIRCUMFERENCE / 4.0
    distance_to_latitude_from_equator = meridional_semicircle * (latitude/90.0)
    subcircle_diameter = _calculate_chord_length(equatorial_radius, distance_to_latitude_from_equator)
    subcircle_circumference = (math.pi * subcircle_diameter)
    return (miles/subcircle_circumference) * 360

def _lat_to_miles(degrees: float) -> float:
    return (MERIDIONAL_CIRCUMFERENCE/360.0) * degrees


def _mile_to_lat(miles: float) -> float:
    return (miles/MERIDIONAL_CIRCUMFERENCE) * 360



class Coordinate:
    """
    Coordinate: Class that represents a point on the earth's surface. Also \n
    has attached address and geocoder objects.\n
    \n
    instantiation; \n
    __init__(self, latitude: float, longitude: float) \n
    \n
    functions;\n
    update_location(self, latitude=None, longitude=None):\n
    get_country_from_coordinate(self) -> str:\n
    move_east(self, value: float, in_='miles')\n
    move_west(self, value: float, in_='miles')\n
    move_north(self, value: float, in_='miles')\n
    move_south(self, value: float, in_='miles')\n
    clone(self)\n
    """

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self.geocoder = geopy.Nominatim(user_agent='allpress')
        self.location = self.geocoder.geocode(f'{self.latitude},{self.longitude}')


    def update_location(self, latitude=None, longitude=None):
        """
        update_location(self, latitude=None, longitude=None): Sets the location of \n
        the Coordaniate to a new one, given a latitude and longitude. lat and long should \n
        be floats. \n
        args; \n
        self: allpress.geo.geo.Coordinate (Instance reference for Coordinate object) \n
        latitude: float or None (New latitude to be set.) \n
        longitude: float or None (New longitude to be set.) \n
        """
        if not latitude and longitude:
            self.location = self.geocoder.geocode(f'{self.latitude},{self.longitude}')
            return
        elif latitude:
            self.latitude = latitude
        elif longitude:
            self.longitude = longitude
        self.location = self.geocoder.geocode(f'{self.latitude},{self.longitude}')


    def get_country_from_coordinate(self) -> str:
        """
        get_country_from_coordinate(self): Returns a string containing the name of the \n
        country a coordinate is located in. If none is found, then the default value \n
        'NullRepublic' is returned. \n
        args; \n
        self: allpress.geo.geo.Coordinate (Instance reference for Coordinate object) \n
        \n
        returns str 
        """
        import spacy
        processor = spacy.load('en_core_web_sm')
        address = self.geocoder.reverse(f'{self.latitude}, {self.longitude}')
        translated = Translator().translate(address.address, dest='en')
        processed = processor(translated.text)
        ents = [ent.text for ent in processed.ents if ent.label_ == 'GPE']
        for ent in ents:
            converted_name = convert(ent, to='name_official')
            if converted_name == 'not found':
                continue
            else:
                return converted_name
        return 'NullRepublic'


    def move_east(self, value: float, in_='miles'):
        """
        move_east(self, value: float, in_='miles'): Moves the longitude of the coordinate \n
        east and updates the coordinates automatically. Can automatically convert miles into  \n
        the appropriate # degrees in longitude given a certain latitude. Also automatically \n
        handles crossing the prime meridian. \n
        args; \n
        self: allpress.geo.geo.Coordinate (Instance reference for Coordinate object) \n
        value: float (Value that the longitude is to be updated by) \n
        in_='miles': str (Unit of the value. Can be either miles, kilometers, or degrees.) \n
        """
        if in_.lower() == 'miles' or in_.lower() == 'mi':
            degrees_to_move = _mile_to_long(self.latitude, value)
        elif in_.lower() == 'degrees' or in_.lower() == 'deg':
            degrees_to_move = value
        else:
            raise UnitError("Invalid Unit selected, must either be 'mi', 'miles', 'deg', or 'degrees'")
        while degrees_to_move > 0:
            if self.longitude + degrees_to_move > 180.0:
                increment = 180.0 - self.longitude
                self.longitude = -180.0
                degrees_to_move -= increment
            elif degrees_to_move > 0:
                self.longitude += degrees_to_move
                degrees_to_move = 0
        self.update_location()
    

    def move_west(self, value: float, in_='miles'):
        """
        move_west(self, value: float, in_='miles'): Moves the longitude of the coordinate \n
        west and updates the coordinates automatically. Can automatically convert miles into  \n
        the appropriate # degrees in longitude given a certain latitude. Also automatically \n
        handles crossing the prime meridian. \n
        args; \n
        self: allpress.geo.geo.Coordinate (Instance reference for Coordinate object) \n
        value: float (Value that the longitude is to be updated by) \n
        in_='miles': str (Unit of the value. Can be either miles, kilometers, or degrees.) \n
        """
        if in_.lower() == 'miles' or in_.lower() == 'mi':
            degrees_to_move = _mile_to_long(self.latitude, value)
        elif in_.lower() == 'degrees' or in_.lower() == 'deg':
            degrees_to_move = value
        else:
            raise UnitError("Invalid Unit selected, must either be 'mi', 'miles', 'deg', or 'degrees'")
        while degrees_to_move > 0:
            if self.longitude - degrees_to_move < -180.0:
                increment = -180.0 + self.longitude
                self.longitude = 180.0
                degrees_to_move -= increment
            elif degrees_to_move > 0:
                self.longitude -= degrees_to_move
                degrees_to_move = 0
        self.update_location()
    

    def move_north(self, value: float, in_='miles'):
        """
        move_north(self, value: float, in_='miles'): Moves the latitude of the coordinate \n
        north and updates the coordinates automatically. Can automatically convert miles into  \n
        the appropriate # degrees in latitude. Will throw an error if attempting to move further \n
        north than the North Pole \n
        args; \n
        self: allpress.geo.geo.Coordinate (Instance reference for Coordinate object) \n
        value: float (Value that the longitude is to be updated by) \n
        in_='miles': str (Unit of the value. Can be either miles, kilometers, or degrees.) \n
        """
        if in_.lower() not in VALID_UNITS:
            raise UnitError
        if in_.lower() == 'miles' or in_.lower() == 'mi':
            degrees_to_move = _mile_to_lat(value)
        elif in_.lower() == 'degrees' or in_.lower() == 'deg':
            degrees_to_move = value
        else:
            raise UnitError("Invalid Unit selected, must either be 'mi', 'miles', 'deg', or 'degrees'")
        if self.latitude + degrees_to_move > 90.0:
            raise CoordinateError("Cannot move further north than the North Pole")
        self.latitude += degrees_to_move
        self.update_location()


    def move_south(self, value: float, in_='miles'):
        """
        move_south(self, value: float, in_='miles'): Moves the latitude of the coordinate \n
        south and updates the coordinates automatically. Can automatically convert miles into  \n
        the appropriate # degrees in latitude. Will throw an error if attempting to move further \n
        sorth than the Sorth Pole \n
        args; \n
        self: allpress.geo.geo.Coordinate (Instance reference for Coordinate object) \n
        value: float (Value that the longitude is to be updated by) \n
        in_='miles': str (Unit of the value. Can be either miles, kilometers, or degrees.) \n
        """
        if in_.lower() not in VALID_UNITS:
            raise UnitError
        if in_.lower() == 'miles' or in_.lower() == 'mi':
            degrees_to_move = _mile_to_lat(value)
        elif in_.lower() == 'degrees' or in_.lower() == 'deg':
            degrees_to_move = value
        else:
            raise UnitError("Invalid Unit selected, must either be 'mi', 'miles', 'deg', or 'degrees'")
        if self.latitude + degrees_to_move < -90.0:
            raise CoordinateError("Cannot move further south than the South Pole")
        self.latitude -= degrees_to_move
        self.update_location()


    def clone(self):
        """
        clone(self): Returns another Coordinate object with the same latitude and \n
        longitude values.\n
        args;\n
        self: allpress.geo.geo.Coordinate (Instance reference for Coordinate object) \n
        \n
        returns allpress.geo.geo.Coordinate
        """
        return Coordinate(self.latitude, self.longitude)

    def __str__(self):
        return f'<coord:({str(self.latitude)[:5]}..,{str(self.longitude)[:5]}..) near {self.location.address}>'

    
    def __repr__(self):
        return self.__str__()



class Region:
    """
    Region: Class that represents a region on the earth's surface. Contains \n
    four Coordinate objects that are represent the bounds of the region.\n
    instantiation; \n
    __init__(self, around=Coordinate(0.0,0.0), radius=250.0) \n
    """

    def __init__(self, around=Coordinate(0.0,0.0), radius=250.0):
        self.center = around
        self.north_bound = around.clone()
        self.north_bound.move_north(radius, in_='miles')
        self.south_bound = around.clone()
        self.south_bound.move_south(radius, in_='miles')
        self.east_bound = around.clone()
        self.east_bound.move_east(radius, in_='miles')
        self.west_bound = around.clone()
        self.west_bound.move_west(radius, in_='miles')


    def __str__(self):
        return f"""Region:\n
                   Nbound({self.north_bound.latitude},{self.north_bound.longitude})\n
                   Sbound({self.south_bound.latitude},{self.south_bound.longitude})\n
                   Ebound({self.east_bound.latitude},{self.east_bound.longitude})\n
                   WBound({self.west_bound.latitude},{self.west_bound.longitude})\n
                   Centered around:{self.center.location}
                    """





