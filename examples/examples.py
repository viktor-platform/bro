from datetime import datetime

from bro.api import Envelope
from bro.api import Point
from bro.api import get_cpt_characteristics_and_return_cpt_objects

begin_date = datetime(2015, 1, 1).strftime("%Y-%m-%d")
end_date = datetime(2023, 3, 3).strftime("%Y-%m-%d")

# Small square area that gives 5 valid cpts
lower_corner = Point(51.92269686635185, 4.469594207611851)
upper_corner = Point(51.923034432171065, 4.470094707426648)

# Define a bounding box, this bbox will give 33 CPTs in front of Rotterdam Central and a lot of deregistered ones
# lower_corner = Point(51.92254633760697, 4.469672543777936)
# upper_corner = Point(51.923349880667615, 4.471895836054459)

# Square area that gives 339 valid cpts
# lower_corner = Point(51.92216787765749, 4.468506938267776)
# upper_corner = Point(51.93072241668058, 4.478816547587933)

area = Envelope(lower_corner, upper_corner)
xml_bytes = get_cpt_characteristics_and_return_cpt_objects(begin_date, end_date, area)
