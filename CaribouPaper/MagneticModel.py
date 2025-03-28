import numpy as np
from scipy.optimize import minimize
from pygeomag import GeoMag
import pandas as pd

def to_decimal_year(date):
    date_object = pd.to_datetime(date, format="mixed")
    total_days = 366 if date_object.is_leap_year else 365
    return date_object.year + (date_object.dayofyear - 1) / total_days

class MagneticModel:
    def __init__(self, sample_resolution, datestr=None, model=None, version=None):
        # Initialize properties
        if model is not None or version is not None:
            raise ValueError("No support for different Model/Version yet")
        elif datestr is None:
            self.decimal_year = to_decimal_year("2020-01-01")
        elif datestr is not None:
            self.decimal_year = to_decimal_year(datestr)
        elif model is not None or version is not None:
            raise ValueError("No support for different Model/Version yet")
        self.height = 0.0  # altitude in meters
        self.sample_resolution = sample_resolution if sample_resolution is not None else 1.0
        self.sample_latitudes = np.arange(-90, 91, self.sample_resolution)
        self.sample_longitudes = np.arange(-180, 181, self.sample_resolution)
        self.lat_mesh_size=np.prod(self.sample_latitudes.shape)
        self.lon_mesh_size=np.prod(self.sample_longitudes.shape)
        self.geo_mag = GeoMag()
        self.contour_levels = {
            'I_INCL': np.arange(-80, 81, 20),  # degrees
            'F_TOTAL': np.arange(0, 101, 5)  # microtesla
        }

        self.populate_samples()
        #self.compute_contours()
        self.compute_gradients()
        self.compute_orthogonality()

    def evaluate_model(self, lat, lon):
        # Evaluate the magnetic field at the given coordinates
        # Outputs in microtesla and degrees
        result=self.geo_mag.calculate(lat, lon, self.height, self.decimal_year)
        #XYZ, H, D, I, F = self.geo_mag.calculate(lat, lon, self.height, self.decimal_year)
        # Access the results
        declination = result.d          # Declination (degrees)
        inclination = result.i          # Inclination (degrees)
        total_intensity = result.f /1000      # Total intensity (nT) converted to µT
        horizontal_intensity = result.h /1000 # Horizontal intensity (nT) converted to µT
        north_component = result.x   /1000   # North component (nT) converted to µT
        east_component = result.y      /1000 # East component (nT) converted to µT
        vertical_component = result.z /1000  # Vertical component (nT) converted to µT

        return north_component, east_component, vertical_component, horizontal_intensity, declination, inclination, total_intensity

    def estimate_gradients(self, lat, lon, ddeg=1e-3):
        # Estimate the intensity and inclination gradients at a location
        _, _, _, _, _, I1, F1 = self.evaluate_model(lat, lon)
        _, _, _, _, _, I2, F2 = self.evaluate_model(lat, lon + ddeg)
        dFdx = (F2 - F1) / ddeg
        dIdx = (I2 - I1) / ddeg
        _, _, _, _, _, I2, F2 = self.evaluate_model(lat + ddeg, lon)
        dFdy = (F2 - F1) / ddeg
        dIdy = (I2 - I1) / ddeg
        return dFdx, dFdy, dIdx, dIdy

    def populate_samples(self):
        # Collect samples of magnetic field properties at all coordinates
        lat = self.sample_latitudes
        lon = self.sample_longitudes
        self.samples = {
            'D_DECL': np.full((len(lat), len(lon)), np.nan),
            'I_INCL': np.full((len(lat), len(lon)), np.nan),
            'F_TOTAL': np.full((len(lat), len(lon)), np.nan)
        }

        for i, latitude in enumerate(lat):
            for j, longitude in enumerate(lon):
                _, _, _, _, D, I, F = self.evaluate_model(latitude, longitude)
                self.samples['D_DECL'][i, j] = D
                self.samples['I_INCL'][i, j] = I
                self.samples['F_TOTAL'][i, j] = F

    #def compute_contours(self):
        # Compute magnetic field property contours
       # self.contour_tables = {}
        #for param, levels in self.contour_levels.items():
         #   contour_matrix = contourc(self.sample_longitudes, self.sample_latitudes, self.samples[param], levels)
         #   self.contour_tables[param] = getContourLineCoordinates(contour_matrix)

    def compute_gradients(self):
        # Compute magnetic field property gradients
        dI_INCL = np.full((2, len(self.sample_latitudes), len(self.sample_longitudes)), np.nan)
        dF_TOTAL = np.full((2, len(self.sample_latitudes), len(self.sample_longitudes)), np.nan)

        for i, lat in enumerate(self.sample_latitudes):
            for j, lon in enumerate(self.sample_longitudes):
                dFdx, dFdy, dIdx, dIdy = self.estimate_gradients(lat, lon)
                dF_TOTAL[:, i, j] = [dFdx, dFdy]
                dI_INCL[:, i, j] = [dIdx, dIdy]

        self.sample_gradients = {
            'I_INCL': dI_INCL,
            'F_TOTAL': dF_TOTAL
        }

    def compute_orthogonality(self):
        # Compute the angle in degrees between gradient vectors for inclination and intensity
        dI_INCL = self.sample_gradients['I_INCL']
        dF_TOTAL = self.sample_gradients['F_TOTAL']
        orthogonality = np.full((len(self.sample_latitudes), len(self.sample_longitudes)), np.nan)

        for i in range(len(self.sample_latitudes)):
            for j in range(len(self.sample_longitudes)):
                angle = self.angle_from_u_to_v(dI_INCL[:, i, j], dF_TOTAL[:, i, j])
                orthogonality[i, j] = angle

        self.sample_orthogonality = orthogonality

    @staticmethod
    def angle_from_u_to_v(U, V):
        # Compute the signed angle in degrees from vector U to vector V
        angleU = np.degrees(np.arctan2(U[1], U[0])) % 360
        angleV = np.degrees(np.arctan2(V[1], V[0])) % 360
        angle = angleV - angleU
        return np.degrees(np.arctan2(np.sin(np.radians(angle)), np.cos(np.radians(angle))))  # between -180 and 180 degrees

    def find_coords(self, F_TOTAL_target, I_INCL_target, lat0, lon0, options=None):
        if options is None:
            options = {'xatol': 1e-16, 'fatol': 1e-16, 'maxiter': 10000, 'disp': True}
        
        latlon = minimize(self.find_coords_error, [lat0, lon0], args=(F_TOTAL_target, I_INCL_target), options=options)
        return latlon.x[0], latlon.x[1]

    def find_coords_error(self, latlon, F_TOTAL_target, I_INCL_target):
        lat = latlon[0]
        lon = latlon[1]
        _, _, _, _, _, I, F = self.evaluate_model(lat, lon)
        return (F - F_TOTAL_target)**2 + (I - I_INCL_target)**2
