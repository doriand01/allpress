import math


from allpress.settings import EQUATORIAL_CIRCUMFERENCE, MERIDIONAL_CIRCUMFERENCE, VALID_UNITS
from allpress.exceptions import CoordinateError, UnitError

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

    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self.geocoder = geopy.Nominatim(user_agent='allpress')
        self.location = self.geocoder.geocode(f'{self.latitude},{self.longitude}')

    def update_location(self, latitude=None, longitude=None):
        if not latitude and longitude:
            self.location = self.geocoder.geocode(f'{self.latitude},{self.longitude}')
            return
        elif latitude:
            self.latitude = latitude
        elif longitude:
            self.longitude = longitude
        self.location = self.geocoder.geocode(f'{self.latitude},{self.longitude}')

    def move_east(self, value: float, in_='miles'):
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
        return Coordinate(self.latitude, self.longitude)



            


    def __str__(self):
        return f'<coord:({str(self.latitude)[:5]}..,{str(self.longitude)[:5]}..) near {self.location.address}>'

    
    def __repr__(self):
        return self.__str__()
        
class Region:

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





