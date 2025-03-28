import numpy as np

class Agent:
    def __init__(self, magmodel, verbose=False):
        self.magmodel = magmodel
        self.verbose = verbose

        # Start and goal positions
        self.start_lat = None
        self.start_lon = None
        self.goal_lat = None
        self.goal_lon = None

        # Magnetic model data
        self.start_D_DECL = None
        self.start_I_INCL = None
        self.start_F_TOTAL = None
        self.goal_D_DECL = None
        self.goal_I_INCL = None
        self.goal_F_TOTAL = None
        self.current_D_DECL = None
        self.current_I_INCL = None
        self.current_F_TOTAL = None

        self.A = np.array([[1, 0], [0, 1]])  # TODO scale properly
        self.use_magnetic_north = False
        self.max_speed = 1 / 10  # TODO scale properly
        self.time_step = 1
        self.sample_velocities = None

        self.trajectory_lat = []
        self.trajectory_lon = []

        # Initialize start and goal
        self.SetStart(-5.2367, -35.4049)  # Brazil coast
        self.SetGoal(-7.923, -14.407)  # Ascension Island

        self.Reset()
        self.ComputeVelocities()
    def SetAMatrix(self, x):
        self.A = x
    def SetStart(self, lat, lon):
        self.start_lat = lat
        self.start_lon = lon
        north_component, east_component, vertical_component, horizontal_intensity, declination, inclination, total_intensity = self.magmodel.evaluate_model(self.start_lat, self.start_lon)
        self.start_D_DECL = declination
        self.start_I_INCL = inclination
        self.start_F_TOTAL = total_intensity

        if self.verbose:
            print(f'=== START SET ===\nLatitude: {self.start_lat}, Longitude: {self.start_lon}')
            print(f'Inclination: {round(self.start_I_INCL, 2)}°, Intensity: {round(self.start_F_TOTAL, 2)} μT')

    def SetGoal(self, lat, lon):
        self.goal_lat = lat
        self.goal_lon = lon
        north_component, east_component, vertical_component, horizontal_intensity, declination, inclination, total_intensity = self.magmodel.evaluate_model(self.goal_lat, self.goal_lon)
        self.goal_D_DECL = declination
        self.goal_I_INCL = inclination
        self.goal_F_TOTAL = total_intensity

        if self.verbose:
            print(f'=== GOAL SET ===\nLatitude: {self.goal_lat}, Longitude: {self.goal_lon}')
            print(f'Inclination: {round(self.goal_I_INCL, 2)}°, Intensity: {round(self.goal_F_TOTAL, 2)} μT')

    def Reset(self):
        self.trajectory_lat = [self.start_lat]
        self.trajectory_lon = [self.start_lon]
        self.current_D_DECL = self.start_D_DECL
        self.current_I_INCL = self.start_I_INCL
        self.current_F_TOTAL = self.start_F_TOTAL

    def Step(self, n=1):
        for _ in range(n):
            velocity = self.ComputeVelocity()
            new_lon = self.trajectory_lon[-1] + velocity[0] * self.time_step
            new_lat = self.trajectory_lat[-1] + velocity[1] * self.time_step

            if abs(new_lat) > 90:
                print("aborting: crossed polar singularity")
                break

            self.trajectory_lat.append(new_lat)
            self.trajectory_lon.append(new_lon)

            north_component, east_component, vertical_component, horizontal_intensity, declination, inclination, total_intensity = self.magmodel.evaluate_model(new_lat, new_lon)
            self.current_D_DECL = declination
            self.current_I_INCL = inclination
            self.current_F_TOTAL = total_intensity

    def Run(self, max_steps=10000):
        self.Reset()
        velocity_threshold = self.max_speed / 100
        steps_taken = 0

        while steps_taken < max_steps:
            velocity = self.ComputeVelocity()
            if np.linalg.norm(velocity) < velocity_threshold:
                break

            new_lon = self.trajectory_lon[-1] + velocity[0] * self.time_step
            new_lat = self.trajectory_lat[-1] + velocity[1] * self.time_step

            if abs(new_lat) > 90:
                print("aborting: crossed polar singularity")
                break

            self.trajectory_lat.append(new_lat)
            self.trajectory_lon.append(new_lon)

            north_component, east_component, vertical_component, horizontal_intensity, declination, inclination, total_intensity = self.magmodel.evaluate_model(new_lat, new_lon)
            self.current_D_DECL = declination
            self.current_I_INCL = inclination
            self.current_F_TOTAL = total_intensity

            steps_taken += 1

    def ComputeVelocity(self, goal_I_INCL=None, goal_F_TOTAL=None, current_I_INCL=None, current_F_TOTAL=None, current_D_DECL=None):
        if goal_I_INCL is None:
            goal_I_INCL = self.goal_I_INCL
        if goal_F_TOTAL is None:
            goal_F_TOTAL = self.goal_F_TOTAL
        if current_I_INCL is None:
            current_I_INCL = self.current_I_INCL
        if current_F_TOTAL is None:
            current_F_TOTAL = self.current_F_TOTAL
        if current_D_DECL is None:
            current_D_DECL = self.current_D_DECL

        if not self.use_magnetic_north:
            rotation_matrix = np.array([[1, 0], [0, 1]])
        else:
            rotation_matrix = np.array([
                [np.cos(np.radians(-current_D_DECL)), -np.sin(np.radians(-current_D_DECL))],
                [np.sin(np.radians(-current_D_DECL)), np.cos(np.radians(-current_D_DECL))]
            ])

        velocity = rotation_matrix @ self.A @ np.array([goal_F_TOTAL - current_F_TOTAL, goal_I_INCL - current_I_INCL])

        if np.linalg.norm(velocity) > self.max_speed:
            velocity = self.max_speed * velocity / np.linalg.norm(velocity)

        return velocity

    def ComputeVelocities(self):
        goal_I = self.goal_I_INCL
        goal_F = self.goal_F_TOTAL

        latitudes = self.magmodel.sample_latitudes
        longitudes = self.magmodel.sample_longitudes

        D_DECL = self.magmodel.samples['D_DECL']
        I_INCL = self.magmodel.samples['I_INCL']
        F_TOTAL = self.magmodel.samples['F_TOTAL']

        velocities = np.full((2, len(latitudes), len(longitudes)), np.nan)

        for i, lat in enumerate(latitudes):
            for j, lon in enumerate(longitudes):
                D = D_DECL[i, j]
                I = I_INCL[i, j]
                F = F_TOTAL[i, j]
                velocities[:, i, j] = self.ComputeVelocity(goal_I, goal_F, I, F, D)

        self.sample_velocities = velocities
    def GetTraj(self):
        return self.trajectory_lat, self.trajectory_lon
    def Bearing(self, velocity):
        return np.mod(90 - np.degrees(np.arctan2(velocity[1], velocity[0])), 360)
