import numpy as np
#from joblib import Parallel, delayed
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
class AxesmMagneticMap:
    def __init__(self, magmod):
        self.projection = 'robin'
        self.coastline_plot = None
        self.R = None
        self.lat_mesh = None
        self.lon_mesh = None
        self.stability = None
        self.surface_mesh = None
        self.surface_mesh_type = None
        self.vector_field = None
        self.vector_field_type = None
        self.vector_field_downsample_factor = 5
        self.vector_field_gradients_scale = 0.5
        self.magmodel=magmod
        self.colors = {
            'surface_mesh': {
                'terrain': {
                    'land': '#D2E9B8',  # muted green
                    'ocean': '#9DD7EE'  # muted blue
                }
            },
            'agent': {
                'start': 'g',
                'goal': 'r',
                'trajectory': 'b',
                'position': 'y'
            }
        }
        self.ax = None

    def initialize_axes(self, projection='robin', surfmesh="stability"):
        self.projection = projection
        
        fig, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.set_facecolor('k')
        
        # Initialize Basemap
        self.m = Basemap(projection=self.projection, lon_0=0, ax=self.ax)
        self.m.drawcoastlines(color='w', linewidth=1)
        self.m.drawcountries(color='w', linewidth=0.5)
        
        # Colors for land and ocean
        self.m.drawmapboundary(fill_color=self.colors['surface_mesh']['terrain']['ocean'])
        #self.m.fillcontinents(color=self.colors['surface_mesh']['terrain']['land'], lake_color=self.colors['surface_mesh']['terrain']['ocean'])
        
        self.lon_mesh, self.lat_mesh = np.meshgrid(np.linspace(-90, 90, self.magmodel.lon_mesh_size), np.linspace(-180, 180, self.magmodel.lat_mesh_size))

        self.set_surface_mesh(surfmesh)
        self.set_vector_field("none")

    def set_surface_mesh(self, surface_mesh_type):
        self.surface_mesh_type = surface_mesh_type
        if self.surface_mesh_type == "stability":
            self.draw_stability_mesh()

    def set_vector_field(self, vector_field_type, downsample_factor=5, gradients_scale=0.5):
        self.vector_field_type = vector_field_type
        self.vector_field_downsample_factor = downsample_factor
        self.vector_field_gradients_scale = gradients_scale
        if self.vector_field_type == "flow":
            self.draw_flow_vector_field_plot()
        elif self.vector_field_type == "gradients":
            self.draw_if_gradients()
    def calculate_stability(self,a):
        lat = self.magmodel.sample_latitudes
        lon = self.magmodel.sample_longitudes
        dF = self.magmodel.sample_gradients['F_TOTAL']
        dI = self.magmodel.sample_gradients['I_INCL']
        D = self.magmodel.samples['D_DECL']
        def compute_stability(i, j):
            Jg = -a.dot(np.array([dF[:,i, j], dI[:,i, j]]))
            ev,_=np.linalg.eig(Jg)
            evreal = np.real(ev)
            evimag = np.imag(ev)
            is_unstable = evreal[0] > 1e-12 or evreal[1] > 1e-12
            is_degenerate = abs(evreal[0]) < 1e-12 or abs(evreal[1]) < 1e-12
            has_rotation = evimag[0] != 0 or evimag[1] != 0

            if is_unstable:
                if has_rotation:
                    return 0.75  # Spiral source (light green)
                else:
                    return 1  # Unstable node (yellow)
            else:
                if is_degenerate:
                    return 0.5  # Neutrally stable
                else:
                    if has_rotation:
                        return 0.25  # Spiral sink (medium green)
                    else:
                        return 0  # Stable node (dark green)
        stab=np.full((len(lat), len(lon)), np.nan)
        for i in range(len(lat)):
            for j in range(len(lon)):
                stab[i,j]=compute_stability(i, j)
        self.stability=stab

    def draw_stability_mesh(self,AMatrix=np.array([[1, 0], [0, 1]])):
        self.calculate_stability(AMatrix)
        lon, lat = np.meshgrid(np.linspace(-180, 180, self.magmodel.lon_mesh_size), np.linspace(-90, 90, self.magmodel.lat_mesh_size))
        x, y = self.m(lon, lat)  # Ensure correct order for Basemap
        self.m.contourf(x, y, self.stability, cmap='summer')

    def draw_flow_vector_field_plot(self):
        lon, lat = np.meshgrid(np.linspace(-180, 180, 50), np.linspace(-90, 90, 50))
        u = np.random.rand(50, 50) - 0.5
        v = np.random.rand(50, 50) - 0.5
        x, y = self.m(lon, lat)
        self.m.quiver(x, y, u, v)

    def draw_if_gradients(self):
        lon, lat = np.meshgrid(np.linspace(-180, 180, 50), np.linspace(-90, 90, 50))
        u = np.random.rand(50, 50) - 0.5
        v = np.random.rand(50, 50) - 0.5
        x, y = self.m(lon, lat)
        self.m.quiver(x, y, u, v, color='gray')

    def update_agent_start(self, start_lat, start_lon):
        x, y = self.m(start_lon, start_lat)
        self.ax.plot(x, y, 'go', markersize=8, label='Start')

    def update_agent_goal(self, goal_lat, goal_lon):
        x, y = self.m(goal_lon, goal_lat)
        self.ax.plot(x, y, 'ro', markersize=8, label='Goal')

    def update_agent_trajectory(self, trajectory_lat, trajectory_lon):
        x, y = self.m(trajectory_lon, trajectory_lat)
        self.ax.plot(x, y, 'b-', label='Trajectory')

    def show(self):
        plt.legend()
        plt.show()
